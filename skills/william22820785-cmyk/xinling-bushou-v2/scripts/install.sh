#!/bin/bash
#
# 心灵补手 V2.0 安装脚本
#
# 用法: ./install.sh
#

set -e

XINLING_DIR="$HOME/.xinling-bushou-v2"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "============================================"
echo "  心灵补手 V2.0 安装程序"
echo "============================================"
echo ""

# 1. 创建目录结构
echo "[1/5] 创建目录结构..."
mkdir -p "$XINLING_DIR/personas"
mkdir -p "$XINLING_DIR/sessions"
mkdir -p "$XINLING_DIR/corpus"
echo "      目录: $XINLING_DIR"

# 2. 复制核心文件
echo "[2/5] 复制核心文件..."
cp -r "$PROJECT_DIR/core" "$XINLING_DIR/"
cp -r "$PROJECT_DIR/adapters" "$XINLING_DIR/"
cp -r "$PROJECT_DIR/schemas" "$XINLING_DIR/"
cp -r "$PROJECT_DIR/personas" "$XINLING_DIR/"
cp -r "$PROJECT_DIR/corpus" "$XINLING_DIR/"
echo "      核心模块已复制"

# 3. 复制CLI脚本
echo "[3/5] 复制CLI脚本..."
cp "$PROJECT_DIR/scripts/xinling" "$XINLING_DIR/"
chmod +x "$XINLING_DIR/xinling"
echo "      CLI已安装到: $XINLING_DIR/xinling"

# 4. 设置PATH（提示）
echo "[4/5] 检查PATH配置..."
if [[ ":$PATH:" == *":$HOME/bin:"* ]]; then
    ln -sf "$XINLING_DIR/xinling" "$HOME/bin/xinling"
    echo "      链接已创建: ~/bin/xinling"
elif [[ ":$PATH:" == *":$HOME/.local/bin:"* ]]; then
    ln -sf "$XINLING_DIR/xinling" "$HOME/.local/bin/xinling"
    echo "      链接已创建: ~/.local/bin/xinling"
else
    echo "      提示: 将 $XINLING_DIR 加入PATH"
fi

# 5. 验证安装
echo "[5/5] 验证安装..."
python3 -c "
import sys
sys.path.insert(0, '$XINLING_DIR')
from core.persona_engine import PersonaEngine
engine = PersonaEngine()
personas = engine.registry.list_personas()
print(f'      ✅ 安装成功! 已注册 {len(personas)} 个人格')
" 2>/dev/null || echo "      ⚠️ 验证跳过，请手动测试"

echo ""
echo "============================================"
echo "  安装完成!"
echo "============================================"
echo ""
echo "使用方式:"
echo "  cd $XINLING_DIR && python3 xinling list"
echo "  cd $XINLING_DIR && python3 xinling show taijian"
echo "  cd $XINLING_DIR && python3 xinling activate taijian"
echo ""
echo "或在Python中引用:"
echo "  import sys"
echo "  sys.path.insert(0, '$XINLING_DIR')"
echo "  from core.persona_engine import PersonaEngine"
echo ""
