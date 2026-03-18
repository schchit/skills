#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书AI创作者识别 - 主入口
触发命令: /小红书创作者识别, /找AI创作者, /xhs-finder
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from xhs_creator_finder import XiaoHongShuBot, asyncio

def main():
    """主入口函数"""
    bot = XiaoHongShuBot()
    asyncio.run(bot.run())

if __name__ == "__main__":
    main()
