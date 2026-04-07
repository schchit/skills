#!/bin/bash
# 基金深度研究报告生成器 - 入口脚本
# 功能：环境检查 + 数据获取 + AI 分析提示

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "📊 基金深度研究报告生成器"
echo "========================================"
echo ""

# 检查模式
if [ "$1" = "--check" ]; then
    echo "【环境检查】"
    echo ""
    
    # 检查 mcporter
    if command -v mcporter &> /dev/null; then
        echo -e "${GREEN}✓${NC} mcporter 已安装：$(mcporter --version)"
    else
        echo -e "${RED}✗${NC} mcporter 未安装"
        echo "  安装命令：npm install -g mcporter"
        exit 1
    fi
    
    # 检查 MCP 服务配置
    echo ""
    echo "MCP 服务配置："
    
    if mcporter list 2>/dev/null | grep -q "jy-financedata-api"; then
        echo -e "${GREEN}✓${NC} jy-financedata-api 服务已配置"
    else
        echo -e "${RED}✗${NC} jy-financedata-api 服务未配置"
        echo "  配置命令：mcporter config add jy-financedata-api --url \"https://api.gildata.com/mcp-servers/aidata-assistant-srv-api?token=你的 JY_API_KEY\""
        exit 1
    fi
    
    if mcporter list 2>/dev/null | grep -q "jy-financedata-tool"; then
        echo -e "${GREEN}✓${NC} jy-financedata-tool 服务已配置"
    else
        echo -e "${YELLOW}⚠${NC} jy-financedata-tool 服务未配置（可选）"
        echo "  配置命令：mcporter config add jy-financedata-tool --url \"https://api.gildata.com/mcp-servers/aidata-assistant-srv-tool?token=你的 JY_API_KEY\""
    fi
    
    # 检查 Python3
    if command -v python3 &> /dev/null; then
        echo -e "${GREEN}✓${NC} Python3 已安装：$(python3 --version)"
    else
        echo -e "${RED}✗${NC} Python3 未安装"
        exit 1
    fi
    
    # 检查输出目录
    if [ -d "$SCRIPT_DIR/output" ]; then
        echo -e "${GREEN}✓${NC} 输出目录存在"
    else
        echo -e "${YELLOW}⚠${NC} 创建输出目录"
        mkdir -p "$SCRIPT_DIR/output"
    fi
    
    echo ""
    echo "========================================"
    echo "环境检查完成！"
    echo "========================================"
    exit 0
fi

# 检查基金代码参数
if [ -z "$1" ]; then
    echo -e "${RED}✗${NC} 请提供基金代码或基金名称"
    echo ""
    echo "用法：./run.sh <基金代码> [维度]"
    echo ""
    echo "示例："
    echo "  ./run.sh 005827"
    echo "  ./run.sh 易方达蓝筹精选混合"
    echo "  ./run.sh 005827 performance"
    echo ""
    exit 1
fi

FUND_CODE="$1"
DIMENSION="${2:-all}"

echo "基金：$FUND_CODE"
echo "维度：$DIMENSION"
echo ""

# 运行数据获取脚本
echo "【步骤 1/2】获取基金数据..."
echo ""
python3 "$SCRIPT_DIR/scripts/fetch_data.py" "$FUND_CODE" "$DIMENSION"

echo ""
echo "========================================"
echo "【步骤 2/2】AI 深度分析"
echo "========================================"
echo ""
echo "✅ 数据已准备就绪！"
echo ""
echo "📝 下一步：将数据发送给 AI 进行深度分析"
echo ""
echo "在 OpenClaw 中输入以下指令："
echo "---"
echo "请根据以上基金数据，生成一份深度投资研究报告。"
echo "报告结构："
echo "1. 基金基本概况"
echo "2. 基金业绩分析（含业绩归因）"
echo "3. 资产配置及持仓风格"
echo "4. 基金经理投资框架"
echo "5. 基金公司分析"
echo "6. 综合评价及投资建议"
echo "输出格式：markdown"
echo "---"
echo ""
