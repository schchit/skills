#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境检查脚本 - 检查 TradingAgents-CN 运行环境

Usage:
    python check_env.py
"""

import os
import sys
from pathlib import Path

# 修复 Windows 控制台编码问题
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def check_project_path():
    """检查项目路径"""
    project_path = Path("E:/TradingAgents-CN")
    
    print("\n📁 项目路径检查")
    print("-" * 40)
    
    if project_path.exists():
        print(f"✅ 项目目录存在: {project_path}")
        
        # 检查关键文件
        key_files = [
            "main.py",
            "requirements.txt",
            "pyproject.toml",
            "cli/main.py",
            "tradingagents/graph/trading_graph.py",
        ]
        
        for f in key_files:
            file_path = project_path / f
            if file_path.exists():
                print(f"   ✅ {f}")
            else:
                print(f"   ❌ {f} (缺失)")
        
        return True
    else:
        print(f"❌ 项目目录不存在: {project_path}")
        print(f"   请先克隆项目:")
        print(f"   git clone https://github.com/hsliuping/TradingAgents-CN.git E:\\TradingAgents-CN")
        return False


def check_env_file():
    """检查 .env 配置文件"""
    env_path = Path("E:/TradingAgents-CN/.env")
    env_example = Path("E:/TradingAgents-CN/.env.example")
    
    print("\n📄 配置文件检查")
    print("-" * 40)
    
    if env_path.exists():
        print(f"✅ .env 文件存在")
        
        # 读取并检查 API Keys
        from dotenv import load_dotenv
        load_dotenv(env_path)
        
        api_keys = {
            "DEEPSEEK_API_KEY": "DeepSeek (推荐)",
            "DASHSCOPE_API_KEY": "通义千问",
            "OPENAI_API_KEY": "OpenAI",
            "GOOGLE_API_KEY": "Google AI",
            "ANTHROPIC_API_KEY": "Anthropic",
            "TUSHARE_TOKEN": "Tushare (A股数据)",
            "FINNHUB_API_KEY": "FinnHub (美股数据)",
        }
        
        configured = []
        for key, name in api_keys.items():
            value = os.getenv(key)
            if value:
                masked = value[:8] + "..." if len(value) > 8 else "***"
                print(f"   ✅ {name}: {masked}")
                configured.append(name)
        
        if not configured:
            print(f"   ⚠️ 未配置任何 API Key")
        
        return len(configured) > 0
    else:
        print(f"❌ .env 文件不存在")
        if env_example.exists():
            print(f"   💡 参考模板: {env_example}")
            print(f"   复制并配置: copy {env_example} {env_path}")
        return False


def check_python_version():
    """检查 Python 版本"""
    print("\n🐍 Python 环境")
    print("-" * 40)
    
    version = sys.version_info
    print(f"   Python 版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 10:
        print(f"   ✅ Python 版本满足要求 (>=3.10)")
        return True
    else:
        print(f"   ❌ Python 版本过低，需要 3.10+")
        return False


def check_dependencies():
    """检查依赖安装"""
    print("\n📦 依赖检查")
    print("-" * 40)
    
    required_packages = [
        ("langgraph", "LangGraph"),
        ("langchain_openai", "LangChain OpenAI"),
        ("openai", "OpenAI SDK"),
        ("pandas", "Pandas"),
        ("akshare", "AkShare"),
        ("tushare", "Tushare"),
        ("rich", "Rich"),
        ("typer", "Typer"),
        ("dotenv", "python-dotenv"),
    ]
    
    installed = []
    missing = []
    
    for module, name in required_packages:
        try:
            __import__(module)
            print(f"   ✅ {name}")
            installed.append(name)
        except ImportError:
            print(f"   ❌ {name} (未安装)")
            missing.append(name)
    
    if missing:
        print(f"\n   💡 安装缺失依赖:")
        print(f"   cd E:\\TradingAgents-CN")
        print(f"   pip install -r requirements.txt")
    
    return len(missing) == 0


def check_data_sources():
    """检查数据源配置"""
    print("\n📊 数据源配置")
    print("-" * 40)
    
    sources = {
        "A股": ["TUSHARE_TOKEN", "AkShare (免费)"],
        "港股": ["yfinance (免费)"],
        "美股": ["FINNHUB_API_KEY", "yfinance (免费)"],
    }
    
    for market, requirements in sources.items():
        print(f"   {market}:")
        for req in requirements:
            if "免费" in req:
                print(f"      ✅ {req}")
            elif os.getenv(req):
                print(f"      ✅ {req} (已配置)")
            else:
                print(f"      ⚠️ {req} (未配置)")


def main():
    print("\n" + "=" * 50)
    print("🔍 TradingAgents-CN 环境检查")
    print("=" * 50)
    
    results = []
    
    # 执行各项检查
    results.append(("Python版本", check_python_version()))
    results.append(("项目路径", check_project_path()))
    results.append(("配置文件", check_env_file()))
    results.append(("依赖安装", check_dependencies()))
    check_data_sources()
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("📋 检查结果汇总")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 未通过"
        print(f"   {name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("\n🎉 环境检查通过！可以开始使用。")
        print("\n快速开始:")
        print("   cd E:\\TradingAgents-CN")
        print("   python -m cli.main")
    else:
        print("\n⚠️ 部分检查未通过，请按提示修复后重试。")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
