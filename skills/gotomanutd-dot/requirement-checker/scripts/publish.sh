#!/bin/bash
# ClawHub 发布脚本 v1.0
# 用法: ./scripts/publish.sh [版本号] [changelog]
# 自动更新所有文件的版本号和版本历史，然后发布

set -e

VERSION="${1:-2.5.0}"
CHANGELOG="${2:-更新}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "════════════════════════════════════════════════════════"
echo "  Requirement-Checker 发布脚本 v1.0"
echo "════════════════════════════════════════════════════════"
echo ""
echo "📦 版本: ${VERSION}"
echo "📝 Changelog: ${CHANGELOG}"
echo "📁 目录: ${PROJECT_DIR}"
echo ""

# 确认发布
read -p "继续发布? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 已取消"
    exit 1
fi

echo ""

# 调用 Python 脚本更新所有文件
echo "🔧 更新版本号和版本历史..."
python3 "${SCRIPT_DIR}/update_version.py" "${VERSION}" "${CHANGELOG}"

echo ""

# 运行测试
echo "🧪 运行测试..."
cd "${PROJECT_DIR}"
bash scripts/test.sh
echo ""

# 发布
echo "📦 发布到 ClawHub..."
clawhub publish . --version "${VERSION}" --changelog "v${VERSION}: ${CHANGELOG}" 2>&1

# 等待服务器处理
echo ""
echo "⏳ 等待服务器处理..."
sleep 5

# 验证远程状态
echo "🔍 验证发布状态..."
RESULT=$(clawhub inspect requirement-checker --json 2>/dev/null | grep -o '"latest": "[^"]*"')

if echo "$RESULT" | grep -q "${VERSION}"; then
    echo ""
    echo "════════════════════════════════════════════════════════"
    echo "  ✅ 发布成功！"
    echo "════════════════════════════════════════════════════════"
    echo ""
    echo "   版本: ${VERSION}"
    echo "   验证: $RESULT"
    echo ""
    echo "🔗 安装命令: clawhub install requirement-checker"
    echo ""
else
    echo ""
    echo "⚠️ 无法确认发布状态"
    echo "   期望版本: ${VERSION}"
    echo "   远程状态: $RESULT"
    echo ""
    echo "💡 建议：稍后手动验证"
    echo "   clawhub inspect requirement-checker --json | grep latest"
fi