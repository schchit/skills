#!/bin/bash
# Setup script for 雨课堂 Skill

set -e

now_ms() {
  ts=$(date +%s%3N 2>/dev/null)
  case "$ts" in
    *N*) ;;
    "") ;;
    *) echo "$ts"; return ;;
  esac

  if command -v python3 >/dev/null 2>&1; then
    python3 -c 'import time; print(int(time.time()*1000))'
    return
  fi

  echo $(( $(date +%s) * 1000 ))
}

START=$(now_ms)

echo "🚀 设置雨课堂 Skill..."
echo ""

## 检查 mcporter
#if ! command -v mcporter &> /dev/null; then
#    echo "⚠️  未找到 mcporter，正在安装..."
#    npm install mcporter
#    echo "✅ mcporter 安装完成"
#fi

MCP_URL="https://open-envning.rainclassroom.com/openapi/v1/mcp-server/sse"
SECRET_URL="https://ykt-envning.rainclassroom.com/ai-workspace/open-claw-skill"

# 新增：检查 YUKETANG_SECRET 环境变量
echo "🔍 检查雨课堂 Secret 环境变量..."
if [ -z "$YUKETANG_SECRET" ]; then
    echo "❌ 错误：未检测到 YUKETANG_SECRET 环境变量！"
    echo "请先执行以下命令设置环境变量（替换为真实 Secret）："
    echo "  export YUKETANG_SECRET=\"your_actual_secret_here\""
    echo "或在执行脚本时直接传入："
    echo "  YUKETANG_SECRET=\"your_actual_secret_here\" bash setup.sh"
    exit 1  # 退出脚本，避免后续无效操作
else
    echo "✅ YUKETANG_SECRET 环境变量已配置"
fi
echo ""

# 添加 MCP 配置
echo "🔧 配置 mcporter..."

# 从环境变量中读取用户填写的 Secret
authorization="Bearer $YUKETANG_SECRET"
npx mcporter config add yuketang-mcp  \
    --url ${MCP_URL} \
    --header "Authorization=$authorization" \
    --scope project

echo "✅ 配置完成！"

# 验证配置
echo "🧪 验证配置..."
if npx mcporter list 2>&1 | grep -q "yuketang-mcp"; then
    echo "✅ 配置验证成功！"
    echo ""
    npx mcporter list | grep -A 1 "yuketang-mcp" || true
else
    echo "⚠️  配置验证失败，请检查网络或 Secret 是否有效"
    echo ""
    echo "如有问题，请访问 ${SECRET_URL} 获取 Secret"
fi


END=$(now_ms)
DURATION=$((END - START))
npx mcporter call yuketang-mcp claw_report --args "{\"payload\": {\"durationMs\": ${DURATION}}, \"action\": \"install\"}" >/dev/null 2>&1

echo ""
echo "─────────────────────────────────────"
echo "🎉 设置完成！"

