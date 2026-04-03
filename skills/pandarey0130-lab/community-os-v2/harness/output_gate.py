"""
OutputGate - 输出验证门
所有外部行动（发消息/发邮件）前必须通过验证
防止 bot 发出不当内容、spam 或超过平台限制的消息
"""
import re
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List

from .policy_gate import PolicyContext


class OutputDecision(Enum):
    VALID = "valid"           # 验证通过
    BLOCK = "block"           # 阻止
    NEEDS_APPROVAL = "needs_approval"  # 需人工审批


@dataclass
class OutputResult:
    decision: OutputDecision
    reason: str = ""
    warnings: List[str] = None


class OutputGate:
    """
    输出验证门

    在 Bot 发送任何外部内容前进行验证：

    1. 长度检查（ Telegram 限制 4096 字符）
    2. 敏感词过滤
    3. Spam 检测（相同内容重复发送）
    4. 高风险内容检测（外部链接、@陌生人）
    5. 频率限制（防刷屏）
    """

    TELEGRAM_MAX_LENGTH = 4096
    WARNING_MAX_LENGTH = 3900  # 留一定余量

    def __init__(self):
        # 敏感词列表（示例，实际从配置加载）
        self._sensitive_patterns = [
            r"(黑客|破解|盗号)",
            r"(赌|博彩)",
        ]
        self._compiled_patterns = [re.compile(p) for p in self._sensitive_patterns]

        # 最近发送记录（用于 spam 检测）
        self._recent_outputs: dict[str, List[float]] = {}
        self._spam_threshold = 3  # 相同内容3次触发spam
        self._spam_window = 60   # 60秒窗口

    def validate(self, output: any, ctx: PolicyContext) -> OutputResult:
        """
        验证输出内容

        Args:
            output: Bot 的输出内容
            ctx: 策略上下文

        Returns:
            OutputResult: 验证结果
        """
        text = self._extract_text(output)
        if not text:
            return OutputResult(OutputDecision.VALID, "Empty output, allowed")

        warnings = []

        # ── 1. 长度检查 ──
        if len(text) > self.TELEGRAM_MAX_LENGTH:
            return OutputResult(
                OutputDecision.BLOCK,
                f"Message too long ({len(text)} chars, max {self.TELEGRAM_MAX_LENGTH})"
            )
        if len(text) > self.WARNING_MAX_LENGTH:
            warnings.append(f"Long message ({len(text)} chars), may be truncated")

        # ── 2. 敏感词检查 ──
        for pattern in self._compiled_patterns:
            if pattern.search(text):
                return OutputResult(
                    OutputDecision.BLOCK,
                    f"Sensitive content detected (pattern: {pattern.pattern})"
                )

        # ── 3. Spam 检测 ──
        if self._is_spam(text, ctx.chat_id or ctx.bot_id):
            return OutputResult(
                OutputDecision.BLOCK,
                "Spam detected: same content sent too many times"
            )

        # ── 4. 高风险内容 ──
        high_risk = self._check_high_risk(text)
        if high_risk:
            warnings.append(high_risk)

        # ── 5. 频率检查 ──
        freq_warning = self._check_frequency(ctx.chat_id or ctx.bot_id)
        if freq_warning:
            warnings.append(freq_warning)

        result = OutputResult(
            OutputDecision.VALID,
            "Output validated",
            warnings=warnings if warnings else None,
        )
        self._record_output(text, ctx.chat_id or ctx.bot_id)
        return result

    def _extract_text(self, output: any) -> str:
        """从各种输出格式中提取文本"""
        if isinstance(output, str):
            return output.strip()
        elif isinstance(output, dict):
            text = output.get("text") or output.get("message") or output.get("content", "")
            return str(text).strip()
        elif isinstance(output, list):
            return " ".join(self._extract_text(o) for o in output)
        return str(output) if output else ""

    def _is_spam(self, text: str, channel: str) -> bool:
        """检测 spam"""
        import time
        now = time.time()
        if channel not in self._recent_outputs:
            self._recent_outputs[channel] = []
        # 清理过期记录
        self._recent_outputs[channel] = [
            t for t in self._recent_outputs[channel]
            if now - t < self._spam_window
        ]
        # 检查相同内容出现次数
        count = sum(1 for t in self._recent_outputs[channel]
                    if self._recent_outputs[channel].count(t) >= 2)
        # 简化的 spam 检测：相同文本超过阈值
        same_count = self._recent_outputs[channel].count(hash(text))
        return same_count >= self._spam_threshold

    def _check_high_risk(self, text: str) -> Optional[str]:
        """检测高风险内容"""
        # 外部链接
        if re.search(r"https?://(?!t\.me|telegram\.org)", text):
            return "External link detected"
        # 陌生人 @
        mentions = re.findall(r"@(\w+)", text)
        if len(mentions) > 3:
            return f"Too many @mentions ({len(mentions)})"
        return None

    def _check_frequency(self, channel: str) -> Optional[str]:
        """检测发送频率"""
        import time
        now = time.time()
        if channel not in self._recent_outputs:
            return None
        recent = [t for t in self._recent_outputs[channel] if now - t < 10]
        if len(recent) >= 5:
            return "High frequency sending detected"
        return None

    def _record_output(self, text: str, channel: str):
        import time
        if channel not in self._recent_outputs:
            self._recent_outputs[channel] = []
        self._recent_outputs[channel].append(time.time())
        self._recent_outputs[channel] = self._recent_outputs[channel][-50:]

    def add_sensitive_pattern(self, pattern: str):
        """动态添加敏感词（运行时）"""
        self._compiled_patterns.append(re.compile(pattern))
