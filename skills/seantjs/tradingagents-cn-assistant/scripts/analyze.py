#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents-CN 股票分析脚本

简化版的股票分析入口，支持快速分析单只股票。

Usage:
    python analyze.py --ticker 600519
    python analyze.py --ticker AAPL --date 2026-03-30
    python analyze.py --ticker 0700.HK --provider deepseek
"""

import os
import sys
import argparse
from pathlib import Path

# 修复 Windows 控制台编码问题
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent  # 跳转到 E:\TradingAgents-CN
TRADINGAGENTS_PATH = Path("E:/TradingAgents-CN")

if TRADINGAGENTS_PATH.exists():
    sys.path.insert(0, str(TRADINGAGENTS_PATH))
    os.chdir(TRADINGAGENTS_PATH)


def check_environment():
    """检查运行环境"""
    # 检查项目目录
    if not TRADINGAGENTS_PATH.exists():
        print(f"❌ 错误：未找到 TradingAgents-CN 项目目录")
        print(f"   期望路径: {TRADINGAGENTS_PATH}")
        print(f"   请先克隆项目: git clone https://github.com/hsliuping/TradingAgents-CN.git E:\\TradingAgents-CN")
        return False
    
    # 检查 .env 文件
    env_file = TRADINGAGENTS_PATH / ".env"
    if not env_file.exists():
        print(f"⚠️ 警告：未找到 .env 配置文件")
        print(f"   建议创建: {env_file}")
        print(f"   参考: {TRADINGAGENTS_PATH / '.env.example'}")
        
        # 检查环境变量
        has_api_key = any([
            os.getenv("DEEPSEEK_API_KEY"),
            os.getenv("DASHSCOPE_API_KEY"),
            os.getenv("OPENAI_API_KEY"),
            os.getenv("GOOGLE_API_KEY"),
        ])
        
        if not has_api_key:
            print(f"\n❌ 错误：未配置任何 LLM API Key")
            print(f"   请在 .env 文件中配置至少一个 API Key：")
            print(f"   - DEEPSEEK_API_KEY=sk-xxx  (推荐)")
            print(f"   - DASHSCOPE_API_KEY=sk-xxx")
            print(f"   - OPENAI_API_KEY=sk-xxx")
            return False
    
    return True


def run_analysis(ticker: str, date: str = None, provider: str = "deepseek", 
                 depth: int = 1, analysts: list = None):
    """
    执行股票分析
    
    Args:
        ticker: 股票代码
        date: 分析日期 (YYYY-MM-DD)，默认今天
        provider: LLM 提供商 (deepseek/dashscope/openai/google)
        depth: 研究深度 (1-3)
        analysts: 分析师列表
    """
    from datetime import datetime
    from dotenv import load_dotenv
    
    # 加载环境变量
    load_dotenv(TRADINGAGENTS_PATH / ".env")
    
    # 默认日期
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"\n{'='*60}")
    print(f"📊 TradingAgents-CN 股票分析")
    print(f"{'='*60}")
    print(f"📈 股票代码: {ticker}")
    print(f"📅 分析日期: {date}")
    print(f"🤖 LLM提供商: {provider}")
    print(f"🔬 研究深度: {depth}")
    print(f"{'='*60}\n")
    
    # 导入 TradingAgents 模块
    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
        print(f"   请确保已安装依赖: pip install -r requirements.txt")
        return None
    
    # 配置
    config = DEFAULT_CONFIG.copy()
    config["llm_provider"] = provider.lower()
    config["max_debate_rounds"] = depth
    config["max_risk_discuss_rounds"] = depth
    
    # 根据提供商设置模型
    provider_models = {
        "deepseek": {
            "quick_think_llm": "deepseek-chat",
            "deep_think_llm": "deepseek-chat"
        },
        "dashscope": {
            "quick_think_llm": "qwen-plus",
            "deep_think_llm": "qwen-max"
        },
        "google": {
            "quick_think_llm": "gemini-2.0-flash",
            "deep_think_llm": "gemini-2.0-flash"
        },
        "openai": {
            "quick_think_llm": "gpt-4o-mini",
            "deep_think_llm": "gpt-4o"
        }
    }
    
    if provider.lower() in provider_models:
        config.update(provider_models[provider.lower()])
    
    # 分析师配置
    if analysts is None:
        analysts = ["market", "fundamentals", "news"]  # 默认分析师
    
    print(f"🚀 开始分析...\n")
    
    try:
        # 初始化分析图
        graph = TradingAgentsGraph(analysts, config=config, debug=True)
        
        # 执行分析
        _, decision = graph.propagate(ticker, date)
        
        print(f"\n{'='*60}")
        print(f"✅ 分析完成！")
        print(f"{'='*60}")
        print(f"\n📋 最终决策:\n")
        print(decision)
        
        # 报告路径
        results_dir = TRADINGAGENTS_PATH / "results" / ticker / date
        print(f"\n📁 详细报告已保存至: {results_dir}")
        
        return decision
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    parser = argparse.ArgumentParser(
        description="TradingAgents-CN 股票分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python analyze.py --ticker 600519                    # 分析茅台
  python analyze.py --ticker AAPL --date 2026-03-30    # 分析苹果
  python analyze.py --ticker 0700.HK --provider google # 分析腾讯
        """
    )
    
    parser.add_argument(
        "--ticker", "-t",
        required=True,
        help="股票代码 (如: 600519, AAPL, 0700.HK)"
    )
    
    parser.add_argument(
        "--date", "-d",
        default=None,
        help="分析日期 (YYYY-MM-DD)，默认今天"
    )
    
    parser.add_argument(
        "--provider", "-p",
        choices=["deepseek", "dashscope", "openai", "google"],
        default="deepseek",
        help="LLM 提供商 (默认: deepseek)"
    )
    
    parser.add_argument(
        "--depth",
        type=int,
        choices=[1, 2, 3],
        default=1,
        help="研究深度 1-3 (默认: 1)"
    )
    
    parser.add_argument(
        "--analysts", "-a",
        nargs="+",
        choices=["market", "fundamentals", "news", "social"],
        default=["market", "fundamentals", "news"],
        help="分析师列表 (默认: market fundamentals news)"
    )
    
    args = parser.parse_args()
    
    # 检查环境
    if not check_environment():
        sys.exit(1)
    
    # 执行分析
    result = run_analysis(
        ticker=args.ticker,
        date=args.date,
        provider=args.provider,
        depth=args.depth,
        analysts=args.analysts
    )
    
    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
