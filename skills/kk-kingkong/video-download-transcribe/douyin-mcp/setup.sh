#!/bin/bash
# Douyin Analyzer MCP 初始化安装脚本
# 用法: ./setup.sh

set -e

echo "=== Douyin Analyzer 安装脚本 ==="
echo

# 1. 检测操作系统
echo "[1/5] 检测环境..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    PLAYWRIGHT_DOWNLOAD_HOST="https://npmmirror.com/mirrors/playwright"
    CHROME_BASE="$HOME/Library/Caches/ms-playwright"
else
    PLAYWRIGHT_DOWNLOAD_HOST="https://npmmirror.com/mirrors/playwright"
    CHROME_BASE="$HOME/.cache/ms-playwright"
fi
echo "  Playwright 镜像: $PLAYWRIGHT_DOWNLOAD_HOST"

# 2. 找 Python
echo "[2/5] 查找 Python..."
if [ -f "$HOME/.openclaw/mcp-servers/douyin-analyzer/.venv/bin/python3" ]; then
    PYTHON="$HOME/.openclaw/mcp-servers/douyin-analyzer/.venv/bin/python3"
elif [ -f "/Users/kk/.openclaw/mcp-servers/douyin-analyzer/.venv/bin/python3" ]; then
    PYTHON="/Users/kk/.openclaw/mcp-servers/douyin-analyzer/.venv/bin/python3"
else
    PYTHON=$(which python3 2>/dev/null || which python 2>/dev/null || echo "python3")
fi
echo "  Python: $PYTHON"

# 3. 安装 Playwright Chromium
echo "[3/5] 检查/安装 Chromium..."
CHROMIUM_PATHS=(
    "$HOME/Library/Caches/ms-playwright/chromium-1105/chrome-mac/Chromium.app/Contents/MacOS/Chromium"
    "$HOME/.cache/ms-playwright/chromium-1105/chrome-linux/chromium"
    "/Users/kk/Library/Caches/ms-playwright/chromium-1105/chrome-mac/Chromium.app/Contents/MacOS/Chromium"
)

CHROMIUM_PATH=""
for p in "${CHROMIUM_PATHS[@]}"; do
    if [ -f "$p" ]; then
        CHROMIUM_PATH="$p"
        break
    fi
done

if [ -z "$CHROMIUM_PATH" ]; then
    echo "  未找到 Chromium，开始安装..."
    if [ -f "$HOME/openclaw-media/.venv/bin/playwright" ]; then
        PLAYWRIGHT_BIN="$HOME/openclaw-media/.venv/bin/playwright"
    elif [ -f "/Users/kk/openclaw-media/.venv/bin/playwright" ]; then
        PLAYWRIGHT_BIN="/Users/kk/openclaw-media/.venv/bin/playwright"
    else
        echo "  错误: 未找到 openclaw-media venv 的 playwright"
        echo "  请先安装: git clone https://github.com/openclaw/openclaw-media ~/openclaw-media"
        exit 1
    fi
    
    PLAYWRIGHT_DOWNLOAD_HOST="$PLAYWRIGHT_DOWNLOAD_HOST" $PLAYWRIGHT_BIN install chromium
    echo "  Chromium 安装完成"
    
    # 再次查找
    for p in "${CHROMIUM_PATHS[@]}"; do
        if [ -f "$p" ]; then
            CHROMIUM_PATH="$p"
            break
        fi
    done
else
    echo "  已安装: $CHROMIUM_PATH"
fi

# 4. 提示配置环境变量
echo "[4/5] 配置环境变量..."
if [ -n "$CHROMIUM_PATH" ]; then
    echo
    echo "  在 ~/.zshrc 或 ~/.bashrc 中添加:"
    echo "  export DOUYIN_CHROMIUM_PATH=\"$CHROMIUM_PATH\""
    echo
    echo "  或在运行 AI 助手前执行:"
    echo "  export DOUYIN_CHROMIUM_PATH=\"$CHROMIUM_PATH\""
fi

# 5. 测试
echo "[5/5] 测试..."
if [ -n "$CHROMIUM_PATH" ]; then
    RESULT=$(DOUYIN_CHROMIUM_PATH="$CHROMIUM_PATH" $PYTHON -c "
import sys
sys.path.insert(0, '$HOME/.openclaw/mcp-servers/douyin-analyzer')
from server import get_douyin_download_link
result = get_douyin_download_link('https://v.douyin.com/6JviX7lMpDg/')
print(result)
" 2>&1)
    
    if echo "$RESULT" | grep -q "download_url"; then
        echo "  ✓ 测试通过！"
    else
        echo "  ✗ 测试失败: $RESULT"
    fi
else
    echo "  ⚠️ 跳过测试（Chromium 未安装）"
fi

echo
echo "=== 安装完成 ==="
echo
echo "下一步:"
echo "1. 重启 AI 助手或在终端设置 DOUYIN_CHROMIUM_PATH 环境变量"
echo "2. 使用 AI 助手分析抖音视频"
