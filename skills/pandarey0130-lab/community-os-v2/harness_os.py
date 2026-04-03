"""
CommunityOS - Harness Engineering Framework
==========================================
用 Harness Engineering 模式重新设计的 CommunityOS

核心原则：
1. 所有操作通过 GovernanceEngine 托管
2. Bot = Harness-managed Agent
3. 工具注册 + 策略门控
4. YAML 配置驱动
"""
import os
import time
import asyncio
import threading
from pathlib import Path
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import yaml
from apscheduler.schedulers.background import BackgroundScheduler

# ── Harness 核心 ──────────────────────────────────────────
from harness.core import GovernanceEngine, GovernanceConfig
from harness.policy_gate import PolicyGate, PolicyContext, PolicyDecision, PolicyDeniedError
from harness.circuit_breaker import CircuitBreaker, CircuitOpenError, get_breaker
from harness.token_budget import TokenBudget
from harness.output_gate import OutputGate
from harness.config import load_harness_config, HarnessFullConfig


class BotRole(Enum):
    HELPER = "helper"           # Panda - 运营助手
    MODERATOR = "moderator"      # Cypher - 技术专家
    BROADCASTER = "broadcaster"  # Buzz - 社区活跃


@dataclass
class BotConfig:
    """Bot 配置"""
    bot_id: str
    role: BotRole
    soul: str
    llm_model: str = "MiniMax-M2.7"
    max_response_tokens: int = 500
    is_admin: bool = False
    telegram_token: str = ""
    knowledge_folder: str = "ai"  # 知识库文件夹


@dataclass
class ToolResult:
    """工具执行结果"""
    success: bool
    data: Any = None
    error: str = ""
    tokens_used: int = 0
    cost_cny: float = 0.0
    duration_ms: int = 0


class ToolRegistry:
    """工具注册表 - 所有 Bot 可用的工具"""
    
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._policies: Dict[str, List[str]] = {}  # tool → allowed roles
        self._lock = threading.Lock()
        self._register_default_tools()
    
    def _register_default_tools(self):
        """注册默认工具"""
        # 所有角色可用的基础工具
        self._policies = {
            "llm_call": ["helper", "moderator", "broadcaster"],
            "receive_message": ["helper", "moderator", "broadcaster"],
            "send_message": ["helper", "moderator", "broadcaster"],
            "reply_message": ["helper", "moderator"],
            "access_knowledge": ["helper", "moderator"],
            "broadcast": ["broadcaster"],
            "welcome_user": ["helper"],
            "pin_message": ["moderator"],
            "kick_user": ["moderator"],
        }
    
    def register(self, name: str, func: Callable, allowed_roles: List[str] = None):
        """注册工具"""
        with self._lock:
            self._tools[name] = func
            if allowed_roles:
                self._policies[name] = allowed_roles
    
    def can_use(self, tool: str, role: BotRole) -> bool:
        """检查角色是否有权限使用工具"""
        allowed = self._policies.get(tool, [])
        return not allowed or role.value in allowed
    
    def get_tool(self, name: str) -> Optional[Callable]:
        return self._tools.get(name)
    
    def list_tools(self, role: BotRole) -> List[str]:
        """列出角色可用的工具"""
        return [t for t, roles in self._policies.items() 
                if not roles or role.value in roles]


class BotAgent:
    """
    Bot Agent - Harness 管理的 Bot 实例
    """
    
    def __init__(
        self,
        config: BotConfig,
        governance: GovernanceEngine,
        tool_registry: ToolRegistry,
        group_id: Optional[str] = None
    ):
        self.config = config
        self.governance = governance
        self.tools = tool_registry
        self.group_id = group_id
        
        # LLM 客户端
        self._llm = None
        
        # 会话历史
        self._history: List[Dict] = []
    
    @property
    def bot_id(self) -> str:
        return self.config.bot_id
    
    @property
    def role(self) -> BotRole:
        return self.config.role
    
    def set_llm(self, llm_client):
        """设置 LLM 客户端"""
        self._llm = llm_client
    
    # ── 核心方法 ────────────────────────────────────────
    
    async def handle_message(
        self,
        message: str,
        user_id: Optional[str] = None,
        chat_type: str = "group",
        is_mentioned: bool = True,
        chat_id: Optional[str] = None,
    ) -> str:
        """
        处理收到的消息
        通过 GovernanceEngine 托管执行
        """
        # 群组消息无需@也能回复（is_mentioned由调用方控制）
        # chat_id 来自实际消息，用于动态查找群关联的知识库
        effective_chat_id = chat_id or self.group_id
        
        start_time = time.time()
        
        # 构建策略上下文
        ctx = PolicyContext(
            bot_id=self.bot_id,
            bot_role=self.config.role.value,
            user_id=user_id,
            chat_id=effective_chat_id,
            chat_type=chat_type,
            is_admin=self.config.is_admin,
        )
        
        # 通过治理引擎执行
        try:
            result = self.governance.execute(
                bot_id=self.bot_id,
                bot_role=self.config.role.value,
                tool="llm_call",
                func=lambda: self._generate_response(message, effective_chat_id),
                ctx=ctx,
                chat_id=effective_chat_id,
                user_id=user_id,
                chat_type=chat_type,
            )
            
            # 记录到历史
            self._history.append({
                "role": "user",
                "content": message,
                "timestamp": time.time()
            })
            self._history.append({
                "role": "assistant", 
                "content": result,
                "timestamp": time.time()
            })
            
            return result
            
        except CircuitOpenError:
            return f"⚠️ {self.config.bot_id} 服务暂时繁忙，请稍后再试~"
        except PolicyDeniedError as e:
            return f"⚠️ 无权执行此操作: {e.reason}"
        except Exception as e:
            return f"⚠️ 处理出错: {str(e)[:50]}"
    
    def _generate_response(self, message: str, chat_id: Optional[str] = None) -> str:
        """生成 LLM 响应"""
        if not self._llm:
            return "⚠️ LLM 未配置"
        
        # 尝试从知识库检索相关内容
        knowledge_context = ""
        effective_chat_id = chat_id or self.group_id
        try:
            from knowledge_base.indexer import KnowledgeIndexer
            from pathlib import Path
            
            indexer = KnowledgeIndexer(
                knowledge_dir=str(Path(__file__).parent / "knowledge"),
                chroma_dir=str(Path(__file__).parent / "chroma_db")
            )
            
            # 检索相关文档（最多3条）
            # 根据实际收到的 chat_id 查找对应的知识库项目
            kb_project = "ai"  # 默认
            try:
                groups_file = Path(__file__).parent / "admin" / "data" / "groups.json"
                if groups_file.exists():
                    with open(groups_file) as f:
                        groups_data = json.load(f)
                    for g in groups_data.get("groups", []):
                        if str(g.get("chat_id")) == str(effective_chat_id):
                            kb_project = g.get("project_id", "ai")
                            break
            except:
                pass
            
            # 混合检索：文档 + URL内容
            all_knowledge = []
            
            # 1. 检索文档
            results = indexer.search(kb_project, message, top_k=5)
            for r in results:
                all_knowledge.append({"text": r["text"][:800], "source": "文档", "type": "doc"})
            
            # 2. 抓取URL内容并匹配
            try:
                projects_file = Path(__file__).parent / "admin" / "data" / "projects.json"
                if projects_file.exists():
                    with open(projects_file) as f:
                        proj_data = json.load(f)
                    proj = next((p for p in proj_data.get("projects", []) if p.get("id") == kb_project), None)
                    if proj and proj.get("urls"):
                        keywords = message.lower().split()[:8]
                        for u in proj.get("urls", []):
                            url_text = indexer._fetch_url_content(u["url"])
                            if url_text and any(kw in url_text.lower() for kw in keywords):
                                all_knowledge.append({
                                    "text": url_text[:1500], 
                                    "source": u.get("title") or u["url"], 
                                    "type": "url"
                                })
            except:
                pass
            
            # 混合所有内容
            if all_knowledge:
                knowledge_context = "\n\n【相关知识】:\n" + "\n".join([
                    f"[{k['source']}] {k['text'][:600]}" for k in all_knowledge
                ])
        except Exception as e:
            pass  # 知识库不可用时继续
        
        prompt = f"""{self.config.soul}

用户: {message}{knowledge_context}

请直接回复，简洁明了。如果有相关知识，优先使用知识库内容。"""
        
        try:
            return self._llm.chat(prompt, max_tokens=self.config.max_response_tokens)
        except Exception as e:
            raise Exception(f"LLM 调用失败: {e}")
    
    async def send_message(self, chat_id: str, text: str) -> ToolResult:
        """发送消息（通过治理引擎）"""
        start_time = time.time()
        
        ctx = PolicyContext(
            bot_id=self.bot_id,
            bot_role=self.config.role.value,
            chat_id=chat_id,
            chat_type="group" if chat_id != self.bot_id else "private",
        )
        
        try:
            result = self.governance.execute(
                bot_id=self.bot_id,
                bot_role=self.config.role.value,
                tool="send_message",
                func=lambda: self._send_telegram(chat_id, text),
                ctx=ctx,
                chat_id=chat_id,
            )
            
            return ToolResult(
                success=True,
                data=result,
                duration_ms=int((time.time() - start_time) * 1000)
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
                duration_ms=int((time.time() - start_time) * 1000)
            )
    
    def _send_telegram(self, chat_id: str, text: str) -> dict:
        """实际发送 Telegram 消息"""
        import requests
        
        url = f"https://api.telegram.org/bot{self.config.telegram_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text[:4096]
        }
        
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        return resp.json()
    
    def get_status(self) -> dict:
        """获取 Bot 状态"""
        return {
            "bot_id": self.bot_id,
            "role": self.config.role.value,
            "group_id": self.group_id,
            "history_count": len(self._history),
            "governance": self.governance.get_status(),
        }


class HarnessOS:
    """
    CommunityOS 主控 - Harness Engineering 模式
    ============================
    
    架构：
    ┌─────────────────────────────────────────────────────────┐
    │                    HarnessOS (主控)                      │
    │  ┌─────────────────────────────────────────────────┐   │
    │  │           GovernanceEngine (治理引擎)              │   │
    │  │  ┌─────────┐ ┌──────────┐ ┌────────┐ ┌────────┐   │   │
    │  │  │Policy   │ │Circuit   │ │Retry   │ │Token   │   │   │
    │  │  │Gate     │ │Breaker   │ │Budget  │ │Budget  │   │   │
    │  │  └─────────┘ └──────────┘ └────────┘ └────────┘   │   │
    │  └─────────────────────────────────────────────────┘   │
    └─────────────────────────────────────────────────────────┘
    │                    │                    │
    ▼                    ▼                    ▼
┌─────────┐      ┌─────────┐         ┌─────────┐
│ BotAgent│      │ BotAgent│         │ BotAgent│
│ (Panda) │◄────►│ (Cypher)│◄──────►│ (Buzz)  │
└─────────┘      └─────────┘         └─────────┘
    │                    │                    │
    └────────────────────┼────────────────────┘
                         ▼
              ┌─────────────────────┐
              │   Tool Registry     │
              │   (工具注册表)        │
              └─────────────────────┘
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config_path: Optional[str] = None):
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self.config_path = config_path
        
        # 加载配置
        self.config = self._load_config(config_path)
        
        # 初始化治理引擎
        self.governance = self._init_governance()
        
        # 工具注册表
        self.tools = ToolRegistry()
        
        # Bot 实例
        self.bots: Dict[str, BotAgent] = {}
        self._init_bots()
        
        # 注册工具（在 Bot 初始化之后）
        self._register_tools()
        
        # 30秒间隔播报调度器
        self._interval_scheduler = BackgroundScheduler()
        self._init_interval_broadcast()
        self._interval_scheduler.start()
    
    def _load_config(self, config_path: Optional[str]) -> HarnessFullConfig:
        """加载配置"""
        if config_path and Path(config_path).exists():
            return load_harness_config(config_path)
        return load_harness_config()
    
    def _init_governance(self) -> GovernanceEngine:
        """初始化治理引擎"""
        cfg = GovernanceConfig(
            cb_failure_threshold=self.config.circuit_breaker.get("failure_threshold", 5),
            cb_recovery_timeout=self.config.circuit_breaker.get("recovery_timeout", 60.0),
            max_tokens_per_session=self.config.token_budget.get("max_tokens_per_session", 8192),
            max_cost_cny_per_session=self.config.token_budget.get("max_cost_cny_per_session", 1.0),
            max_messages_per_session=self.config.token_budget.get("max_messages_per_session", 50),
            default_timeout=self.config.execution.get("default_timeout", 30.0),
            require_output_gate=self.config.output_gate.get("enabled", True),
        )
        return GovernanceEngine(cfg)
    
    def _load_bot_configs(self, config_path: Optional[str]) -> Dict[str, Any]:
        """从 admin/data/bots.json 读取 Bot 配置"""
        bots_json_path = Path(__file__).parent / "admin" / "data" / "bots.json"
        if bots_json_path.exists():
            import json
            with open(bots_json_path) as f:
                data = json.load(f)
            bots = {}
            for bot in data.get("bots", []):
                bot_id = bot.get("bot_id")
                if bot_id:
                    bots[bot_id] = {
                        "role": "helper",
                        "soul_file": f"souls/{bot_id}.md",
                        "llm_model": bot.get("llm", {}).get("model", "MiniMax-M2.7"),
                        "max_response_tokens": 500,
                        "is_admin": bot.get("is_admin", False),
                        "telegram_token": bot.get("bot_token", ""),
                    }
            return bots
        return {}

    def _init_bots(self):
        """初始化所有 Bot"""
        self._bot_configs = self._load_bot_configs(self.config_path)
        for bot_id, bot_cfg in self._bot_configs.items():
            role = BotRole(bot_cfg.get("role", "helper"))
            
            # 读取 Soul 文件
            soul_file = bot_cfg.get("soul_file", f"souls/{bot_id}.md")
            soul_path = Path(__file__).parent / soul_file
            soul = soul_path.read_text() if soul_path.exists() else f"你是 {bot_id}"
            
            # 获取 Telegram Token
            token = self._get_token(bot_id)
            
            config = BotConfig(
                bot_id=bot_id,
                role=role,
                soul=soul,
                llm_model=bot_cfg.get("llm_model", "MiniMax-M2.7"),
                max_response_tokens=bot_cfg.get("max_response_tokens", 500),
                is_admin=bot_cfg.get("is_admin", False),
                telegram_token=token,
                knowledge_folder=bot_cfg.get("knowledge", {}).get("folder", "ai"),
            )
            
            self.bots[bot_id] = BotAgent(config, self.governance, self.tools)
            
            # 设置 LLM
            from bot_engine.llm.minimax import LLMClient
            llm = LLMClient(model=config.llm_model)
            self.bots[bot_id].set_llm(llm)
    
    def _get_token(self, bot_id: str) -> str:
        """获取 Bot Token"""
        tokens = {
            "panda": os.environ.get("PANDORA_TOKEN", ""),
            "cypher": os.environ.get("CYPHER_TOKEN", ""),
            "buzz": os.environ.get("BUZZ_TOKEN", ""),
            "Quantkeybot": os.environ.get("QUANTKEY_TOKEN", ""),
        }
        return tokens.get(bot_id, "")
    
    def _register_tools(self):
        """注册工具到注册表"""
        # LLM 调用
        self.tools.register("llm_call", lambda msg, **k: self.bots[k.get('bot_id', 'panda')]._generate_response(msg))
        
        # 消息发送
        for bot_id, bot in self.bots.items():
            self.tools.register(
                "send_message",
                lambda cid, txt, b=bot: bot._send_telegram(cid, txt),
                allowed_roles=[bot.role.value]
            )
    
    def _init_interval_broadcast(self):
        """初始化30秒间隔播报调度器"""
        # 读取 admin/data/bots.json，获取所有 bot 的 interval_broadcast 配置
        base_dir = Path(__file__).parent
        bots_file = base_dir / "admin" / "data" / "bots.json"
        if not bots_file.exists():
            return
        
        try:
            with open(bots_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            for bot_cfg in data.get("bots", []):
                bot_id = bot_cfg.get("bot_id", "")
                ib = bot_cfg.get("interval_broadcast", {})
                if ib.get("enabled") and bot_id in self.bots:
                    interval_sec = 0  # 暂时禁用
                    self._interval_scheduler.add_job(
                        self._run_interval_broadcast,
                        "interval",
                        seconds=interval_sec,
                        id=f"ib_{bot_id}",
                        args=[bot_id],
                        replace_existing=True,
                    )
                    print(f"[IntervalBroadcast] 已注册: bot={bot_id}, 每{interval_sec}秒播报一次")
        except Exception as e:
            print(f"[IntervalBroadcast] 初始化失败: {e}")
    
    def _run_interval_broadcast(self, bot_id: str):
        """执行30秒间隔播报（由 APScheduler 调用）"""
        if bot_id not in self.bots:
            return
        
        bot_agent = self.bots[bot_id]
        base_dir = Path(__file__).parent
        
        try:
            # 重新读取配置（支持热更新）
            bots_file = base_dir / "admin" / "data" / "bots.json"
            groups_file = base_dir / "admin" / "data" / "groups.json"
            
            if not bots_file.exists() or not groups_file.exists():
                return
            
            with open(bots_file, "r", encoding="utf-8") as f:
                bots_data = json.load(f)
            with open(groups_file, "r", encoding="utf-8") as f:
                groups_data = json.load(f)
            
            # 获取当前 bot 的 interval_broadcast 配置
            bot_cfg = next((b for b in bots_data.get("bots", []) if b.get("bot_id") == bot_id), None)
            if not bot_cfg:
                return
            
            ib = bot_cfg.get("interval_broadcast", {})
            if not ib.get("enabled"):
                return
            
            message = ib.get("message", "").strip()
            if not message:
                return
            
            # 获取 bot 所属的群列表
            # 优先用 bots.json 里 bot 的 groups 字段；为空则反向查 groups.json
            bot_group_ids = bot_cfg.get("groups", [])
            
            # 查找每个群的 chat_id
            for group_cfg in groups_data.get("groups", []):
                group_id_str = group_cfg.get("group_id", "")
                # 如果 bots.json 的 groups 为空，则从 groups.json 的 bots 列表反向查找
                if bot_group_ids:
                    if group_id_str not in bot_group_ids:
                        continue
                else:
                    if bot_id not in group_cfg.get("bots", []):
                        continue
                
                if not group_cfg.get("enabled", False):
                    continue
                
                chat_id = group_cfg.get("chat_id", "")
                if not chat_id:
                    continue
                
                # 发送消息
                try:
                    bot_agent._send_telegram(chat_id, message)
                    print(f"[IntervalBroadcast] 播报成功: bot={bot_id} -> group={group_id_str} ({chat_id})")
                except Exception as e:
                    print(f"[IntervalBroadcast] 播报失败: bot={bot_id} -> group={group_id_str}: {e}")
        
        except Exception as e:
            print(f"[IntervalBroadcast] 执行出错 bot={bot_id}: {e}")
    
    def get_bot(self, bot_id: str) -> Optional[BotAgent]:
        """获取 Bot 实例"""
        return self.bots.get(bot_id)
    
    def get_status(self) -> dict:
        """获取系统状态"""
        return {
            "bots": {bid: bot.get_status() for bid, bot in self.bots.items()},
            "governance": self.governance.get_status(),
            "tools": list(self.tools._tools.keys()),
        }
    
    @classmethod
    def get_instance(cls) -> "HarnessOS":
        """获取单例"""
        if cls._instance is None:
            cls()
        return cls._instance


# ── 便捷函数 ──────────────────────────────────────────────

def create_os(config_path: Optional[str] = None) -> HarnessOS:
    """创建 CommunityOS 实例"""
    return HarnessOS(config_path)


def get_os() -> HarnessOS:
    """获取现有实例"""
    return HarnessOS.get_instance()
