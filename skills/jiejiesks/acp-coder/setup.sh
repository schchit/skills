#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# acp-coder — 一键安装脚本
# 配置 OpenClaw ACP + acpx agent 映射
# ============================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${CYAN}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
fail()  { echo -e "${RED}[FAIL]${NC}  $*"; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ----------------------------------------------------------
# 1. 检测已安装的 coding agent
# ----------------------------------------------------------
info "检测已安装的 coding agent..."

AGENTS=()

check_agent() {
  local name=$1 cmd=$2 label=$3
  if command -v "$cmd" &>/dev/null; then
    AGENTS+=("$name")
    ok "$name ($label)"
  fi
}

check_agent "claude"   "claude"   "Claude Code"
check_agent "codex"    "codex"    "Codex CLI"
check_agent "gemini"   "gemini"   "Gemini CLI"
check_agent "opencode" "opencode" "OpenCode"
check_agent "kimi"     "kimi"     "Kimi CLI"
check_agent "aider"    "aider"    "Aider"

if [ ${#AGENTS[@]} -eq 0 ]; then
  fail "未检测到任何 coding agent。请至少安装一个，如:\n  npm install -g @anthropic-ai/claude-code"
fi

# 构建白名单 JSON（纯 bash，不依赖 jq）
ALLOW_JSON="["
for i in "${!AGENTS[@]}"; do
  [ "$i" -gt 0 ] && ALLOW_JSON+=","
  ALLOW_JSON+="\"${AGENTS[$i]}\""
done
ALLOW_JSON+="]"

DEFAULT_AGENT="${AGENTS[0]}"

info "可用 agent: ${AGENTS[*]}  (默认: $DEFAULT_AGENT)"

# ----------------------------------------------------------
# 2. 配置 OpenClaw
# ----------------------------------------------------------
info "配置 OpenClaw..."

# acpx 插件（使用 openclaw 内置 acpx）
openclaw config set plugins.entries.acpx.enabled true
openclaw config set plugins.entries.acpx.config.permissionMode approve-all

# ACP
openclaw config set acp.enabled true
openclaw config set acp.backend acpx
openclaw config set acp.defaultAgent "$DEFAULT_AGENT"
openclaw config set acp.allowedAgents "$ALLOW_JSON"

# 跨 session 访问
openclaw config set tools.sessions.visibility all
openclaw config set tools.agentToAgent.enabled true

ok "OpenClaw 配置完成"

# ----------------------------------------------------------
# 3. 修复 acpx agent 命令映射
# ----------------------------------------------------------
# acpx 0.3.x 内置映射指向已 deprecated 的 @zed-industries/claude-agent-acp，
# 与新版 Claude Code 不兼容。通过 ~/.acpx/config.json 覆盖为新包。
info "配置 acpx agent 命令..."

ACPX_CONFIG_DIR="$HOME/.acpx"
ACPX_CONFIG="$ACPX_CONFIG_DIR/config.json"
mkdir -p "$ACPX_CONFIG_DIR"

# 构建 agents 配置（只覆盖检测到的 agent 中需要修复的）
ACPX_AGENTS="{"
NEED_COMMA=false

# claude: deprecated @zed-industries → @agentclientprotocol
for agent in "${AGENTS[@]}"; do
  if [ "$agent" = "claude" ]; then
    $NEED_COMMA && ACPX_AGENTS+=","
    ACPX_AGENTS+="\"claude\":{\"command\":\"npx -y @agentclientprotocol/claude-agent-acp\"}"
    NEED_COMMA=true
  fi
done

ACPX_AGENTS+="}"

if [ -f "$ACPX_CONFIG" ]; then
  # 已有配置文件，备份后合并 claude 覆盖
  cp "$ACPX_CONFIG" "$ACPX_CONFIG.bak"
  # 用 node 做 JSON 合并（比 sed 可靠）
  node -e "
    const fs = require('fs');
    const cfg = JSON.parse(fs.readFileSync('$ACPX_CONFIG', 'utf8'));
    const patch = JSON.parse('$ACPX_AGENTS');
    cfg.agents = Object.assign(cfg.agents || {}, patch);
    fs.writeFileSync('$ACPX_CONFIG', JSON.stringify(cfg, null, 2) + '\n');
  " && ok "已合并 acpx agent 配置" || warn "合并失败，请手动编辑 $ACPX_CONFIG"
else
  echo "{\"agents\":$ACPX_AGENTS}" > "$ACPX_CONFIG"
  ok "已创建 $ACPX_CONFIG"
fi

# ----------------------------------------------------------
# 4. 配置 heartbeat（streamTo 自动回调必需）
# ----------------------------------------------------------
# sessions_spawn streamTo:"parent" + sessions_yield 实现子 agent 完成后自动唤醒父 session。
# 前提：父 session 所属的 agent 必须在 agents.list 里配置 heartbeat.target = "last"。
# 若无此配置，回调通知会被丢弃，需用户手动发消息才能继续。
info "配置 heartbeat（子 agent 完成自动回调）..."

OPENCLAW_CONFIG="$HOME/.openclaw/openclaw.json"

if [ ! -f "$OPENCLAW_CONFIG" ]; then
  warn "未找到 $OPENCLAW_CONFIG，跳过 heartbeat 配置（可在 openclaw 初始化后重新运行此脚本）"
else
  node -e "
    const fs = require('fs');
    const cfg = JSON.parse(fs.readFileSync('$OPENCLAW_CONFIG', 'utf8'));
    const list = cfg.agents?.list ?? [];
    let changed = 0;
    for (const entry of list) {
      if (!entry.heartbeat) {
        entry.heartbeat = { every: '30m', target: 'last' };
        changed++;
      } else if (!entry.heartbeat.target) {
        entry.heartbeat.target = 'last';
        changed++;
      }
    }
    if (changed > 0) {
      fs.writeFileSync('$OPENCLAW_CONFIG', JSON.stringify(cfg, null, 2) + '\n');
      console.log('已为 ' + changed + ' 个 agent 添加 heartbeat 配置');
    } else {
      console.log('heartbeat 已配置，跳过');
    }
  " && ok "heartbeat 配置完成" || warn "heartbeat 配置失败，请手动在 openclaw.json 的 agents.list 每个 agent 下添加: { \"heartbeat\": { \"every\": \"30m\", \"target\": \"last\" } }"
fi

# ----------------------------------------------------------
# 5. 重启 daemon
# ----------------------------------------------------------
info "重启 OpenClaw daemon..."

if openclaw daemon restart 2>/dev/null; then
  ok "daemon 已重启"
else
  warn "daemon 重启失败（可能未在运行），请手动执行: openclaw daemon restart"
fi

# ----------------------------------------------------------
# 5. 验证
# ----------------------------------------------------------
info "验证 acpx 通信..."

sleep 2

if acpx "${DEFAULT_AGENT}" exec "echo foreman-setup-ok" 2>/dev/null | grep -q "foreman-setup-ok"; then
  ok "acpx → $DEFAULT_AGENT 通信正常"
else
  warn "acpx → $DEFAULT_AGENT 通信验证失败，可能 agent 尚未就绪，请稍后手动验证:\n  acpx $DEFAULT_AGENT exec \"echo hello\""
fi

# ----------------------------------------------------------
# 完成
# ----------------------------------------------------------
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  acp-coder 安装完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "  可用 agent:  ${AGENTS[*]}"
echo "  默认 agent:  $DEFAULT_AGENT"
echo "  Workspace:   ~/.openclaw/workspace"
echo ""
echo "  使用方式："
echo "    - 通过 Web UI / Telegram 发送代码任务，自动触发"
echo "    - 或手动发送 /acp-coder <任务描述>"
echo ""
