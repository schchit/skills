#!/bin/bash
# MarkHub v6.0 安装脚本

set -e

echo "=========================================="
echo "🎨 MarkHub v6.0 - 安装程序"
echo "=========================================="

# 1. 检查 Python
echo ""
echo "📦 检查 Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 Python 3"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python $PYTHON_VERSION"

# 2. 检查 FFmpeg
echo ""
echo "📦 检查 FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  警告：未找到 FFmpeg"
    echo "   安装方法："
    echo "   macOS:  brew install ffmpeg"
    echo "   Linux: apt install ffmpeg"
    echo ""
    read -p "是否继续安装？(y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    FFMPEG_VERSION=$(ffmpeg -version | head -n1)
    echo "✅ $FFMPEG_VERSION"
fi

# 3. 安装 Python 依赖
echo ""
echo "📦 安装 Python 依赖..."

echo "   - stable-diffusion-cpp-python (这可能需要几分钟)..."
pip3 install stable-diffusion-cpp-python --quiet

echo "   - pillow..."
pip3 install pillow --quiet

echo "   - numpy..."
pip3 install numpy --quiet

echo "✅ Python 依赖安装完成"

# 4. 创建目录
echo ""
echo "📁 创建目录..."
mkdir -p ~/Videos/MarkHub
mkdir -p ~/.markhub/models
echo "✅ 目录已创建"
echo "   输出目录：~/Videos/MarkHub"
echo "   模型目录：~/.markhub/models"

# 5. 测试安装
echo ""
echo "🧪 测试安装..."
python3 -c "
try:
    from stable_diffusion_cpp import StableDiffusion
    print('✅ stable-diffusion-cpp-python 安装成功')
except ImportError as e:
    print(f'⚠️  stable-diffusion-cpp-python 安装失败：{e}')
    print('   请手动运行：pip3 install stable-diffusion-cpp-python')

try:
    from PIL import Image
    print('✅ pillow 安装成功')
except ImportError:
    print('❌ pillow 安装失败')

try:
    import numpy
    print('✅ numpy 安装成功')
except ImportError:
    print('❌ numpy 安装失败')
"

# 6. 完成
echo ""
echo "=========================================="
echo "✅ 安装完成！"
echo "=========================================="
echo ""
echo "📖 使用方法:"
echo "   python3 markhub_v6_local.py -p \"A beautiful woman\""
echo ""
echo "📚 查看文档:"
echo "   cat SKILL.md"
echo ""
echo "🎯 下一步:"
echo "   1. 测试生成：python3 markhub_v6_local.py -p \"test\""
echo "   2. 查看可用模型：cat SKILL.md | grep -A10 \"可用模型\""
echo ""
