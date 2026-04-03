"""
单个 Bot 实例（集成 Harness 治理）
"""
import os
import time
import threading
from typing import Dict, Any, Optional, List
from pathlib import Path
from .config_parser import BotConfig, GroupConfig
from .llm.minimax import MiniMaxLLM

from knowledge_base.loader import scan_folder

# ── Harness 集成 ──────────────────────────────────────────
_harness_lock = threading.Lock()
_governance_engine = None

def get_governance_engine():
    """全局 GovernanceEngine 单例"""
    global _governance_engine
    if _governance_engine is None:
        with _harness_lock:
            if _governance_engine is None:
                from harness.core import GovernanceEngine
                _governance_engine = GovernanceEngine()
    return _governance_engine


class BotInstance:
    def __init__(self, bot_config_path: str, group_config: Optional[GroupConfig] = None, base_dir: str = ""):
        self.config = BotConfig(bot_config_path)
        self.group_config = group_config
        self.base_dir = base_dir or str(Path(bot_config_path).parent.parent.parent)

        # Governance Engine
        self.governance = get_governance_engine()

        # 初始化 LLM - 统一用 Claude Code
        from bot_engine.llm.claude_code import ClaudeCodeLLM
        self.llm = ClaudeCodeLLM(self.config.llm_config)

        # 初始化向量存储
        chroma_dir = os.path.join(self.base_dir, "knowledge_base", "chroma_db")
        try:
            self.vector_store = VectorStore(chroma_dir)
        except Exception as e:
            logger.warning(f"ChromaDB 初始化失败，跳过: {e}")
            self.vector_store = None

        # 合并模式：群配置覆盖 Bot 配置
        self.active_modes = dict(self.config.modes)
        if group_config:
            group_modes = group_config.get_bot_modes(self.config.bot_id)
            self.active_modes.update(group_modes)

        # 确定使用的知识库
        # 优先从 admin/groups.json 读取 project_id（正确的链路）
        self.knowledge_project_id = None
        if group_config:
            groups_file = Path(self.base_dir) / "admin" / "data" / "groups.json"
            if groups_file.exists():
                import json as _json
                with open(groups_file) as _f:
                    groups_data = _json.load(_f)
                for g in groups_data.get("groups", []):
                    if g.get("group_id") == group_config.group_id:
                        self.knowledge_project_id = g.get("project_id")
                        break

        # Chroma collection 名称 = kb_{project_id}（与 indexer.py 保持一致）
        if self.knowledge_project_id:
            self.knowledge_folder = self.knowledge_project_id
        elif group_config and group_config.knowledge_folder:
            self.knowledge_folder = group_config.knowledge_folder
        else:
            self.knowledge_folder = self.config.get_knowledge_folder()

    def should_respond(self, message: str, is_new_member: bool = False) -> bool:
        """
        根据模式和上下文判断是否应该响应
        """
        # 欢迎模式
        if is_new_member and self.active_modes.get("welcome"):
            return True

        # 被动问答模式：有内容就考虑响应
        if self.active_modes.get("passive_qa") and message.strip():
            return True

        return False

    def generate_response(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """根据模式生成响应"""
        context = context or {}

        # 欢迎新成员
        if context.get("is_new_member"):
            return self._generate_welcome(context.get("member_name", ""))

        # RAG 问答
        if self.active_modes.get("passive_qa") and message.strip():
            return self.run_rag(message)

        return ""

    def run_rag(self, query: str) -> str:
        """RAG 检索 + LLM 生成"""
        # 确定 collection 名称
        # 优先用 knowledge_project_id（来自 groups.json），拼成 kb_{project_id} 与 indexer.py 一致
        if self.knowledge_project_id:
            collection = f"kb_{self.knowledge_project_id}"
        elif self.knowledge_folder:
            collection = self.knowledge_folder
        else:
            collection = "default"

        # 检索相关文档
        try:
            results = self.vector_store.query(collection, query, top_k=5)
        except Exception as e:
            print(f"向量检索失败: {e}")
            results = {"documents": [[]], "metadatas": [[]]}

        docs = results.get("documents", [[]])[0]
        if not docs:
            # 没有检索到文档，直接用 LLM
            return self._llm_generate(query, "")

        # 构建上下文
        context = "\n\n".join(f"[文档{i+1}] {doc}" for i, doc in enumerate(docs))

        return self._llm_generate(query, context)

    def _llm_generate(self, query: str, context: str) -> str:
        """调用 LLM 生成回答（通过 Harness 治理）"""
        system = self.config.soul or "你是一个有用的助手。"

        if context:
            system += f"\n\n【参考知识】\n{context}\n\n请根据参考知识回答用户问题。"

        try:
            # ── 通过 GovernanceEngine 托管执行 ──
            from harness.core import CircuitOpenError, TokenBudgetExceededError
            from harness.policy_gate import PolicyContext

            ctx = PolicyContext(
                bot_id=self.config.bot_id,
                bot_role=self.config.llm_config.get("model", "helper"),
                chat_type="group",
            )

            def raw_llm():
                return self.llm.chat(
                    messages=[{"role": "user", "content": query}],
                    system_prompt=system,
                    temperature=0.7
                )

            # GovernanceEngine.execute 会自动处理：
            # PolicyGate + CircuitBreaker + RetryBudget + TokenBudget + OutputGate
            result = self.governance.execute(
                bot_id=self.config.bot_id,
                bot_role=ctx.bot_role,
                tool="llm_call",
                func=raw_llm,
                ctx=ctx,
                chat_id=self.group_config.group_id if self.group_config else None,
            )
            return result

        except CircuitOpenError as e:
            self._report_status(error=f"Circuit OPEN: {e}")
            return f"⚠️ {self.config.avatar} 当前服务繁忙，请稍后再试~"
        except TokenBudgetExceededError:
            self._report_status(error="Token budget exceeded")
            return f"⚠️ {self.config.avatar} 本次会话资源已用完，稍后再试~"
        except Exception as e:
            self._report_status(error=str(e))
            return f"⚠️ 抱歉，生成回答时出错: {e}"

    def _generate_welcome(self, member_name: str = "") -> str:
        """生成欢迎语"""
        template = self.config.welcome_config.get(
            "template",
            f"{self.config.avatar} 欢迎 {{{{name}}}} 加入社区！有什么问题随时问我~"
        )
        name = member_name or "新朋友"
        return template.replace("{{name}}", name)

    def get_broadcast_content(self) -> Optional[str]:
        """获取定时播报内容"""
        if not self.active_modes.get("scheduled_broadcast"):
            return None

        broadcast_cfg = self.config.broadcast_config
        content_source = broadcast_cfg.get("content_source", "api")
        template = broadcast_cfg.get("template", "{content}")

        if content_source == "api":
            api_endpoint = broadcast_cfg.get("api_endpoint", "")
            if api_endpoint:
                try:
                    import requests
                    resp = requests.get(api_endpoint, timeout=10)
                    data = resp.json()
                    content = data.get("content", str(data))
                    return template.format(content=content)
                except Exception as e:
                    return f"📬 播报获取失败: {e}"
        elif content_source == "knowledge":
            # 从知识库随机获取
            return self._get_knowledge_summary()

        return None

    def _get_knowledge_summary(self) -> str:
        """从知识库获取摘要"""
        if not self.knowledge_folder:
            return ""

        folder_path = os.path.join(self.base_dir, "knowledge", self.knowledge_folder)
        if not os.path.exists(folder_path):
            return ""

        docs = scan_folder(folder_path)
        if not docs:
            return ""

        # 取第一个文档的前500字摘要
        _, content = docs[0]
        summary = content[:500]
        return f"📚 今日分享：\n{summary}..."

    def respond_to_mention(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        处理被 @ 提及时的响应
        专门处理针对本 Bot 的提问或指令
        """
        context = context or {}
        
        # 清理消息中的 @ 标记
        import re
        clean_message = re.sub(rf"@{self.config.bot_id}\s*", "", message, flags=re.IGNORECASE)
        clean_message = clean_message.strip()
        
        if not clean_message:
            return f"{self.config.avatar} 有什么事吗？直接问我问题就好~"
        
        # 生成响应
        response = self.generate_response(clean_message, context)
        
        # 上报状态到管理后台
        self._report_status(msg_count_delta=1)
        
        return response
    
    def _report_status(self, msg_count_delta: int = 0, error: Optional[str] = None):
        """上报 Bot 状态到管理后台"""
        try:
            # 延迟导入避免循环依赖
            from admin.app import update_bot_status
            update_bot_status(
                bot_id=self.config.bot_id,
                name=self.config.name,
                status="error" if error else "online",
                msg_count_delta=msg_count_delta,
                error=error,
                groups=[self.group_config.group_name] if self.group_config else [],
                knowledge_enabled=self.config.knowledge_enabled if hasattr(self.config, 'knowledge_enabled') else False,
            )
        except (ImportError, AttributeError):
            # 管理后台未启动或函数不存在，忽略
            pass
        except Exception:
            # 上报失败不影响主流程
            pass


if __name__ == "__main__":
    # 测试
    import os
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "bots", "bot_panda.yaml")
    if os.path.exists(config_path):
        bot = BotInstance(config_path)
        print(f"Bot: {bot.config.name}")
        print(f"Modes: {bot.active_modes}")
    else:
        print(f"配置不存在: {config_path}")
