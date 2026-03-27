---
name: "dota2 XG next game"
description: "查询 Xtreme Gaming (XG) 战队的下一场比赛信息。当用户询问 XG 何时有比赛或下一场对手是谁时调用。"
author: "ame hater"
version: "1.0.1"
---

# dota2 XG next game

这个技能专门用于从 Liquipedia 抓取 Xtreme Gaming (XG) 的最新赛程。

## 运行逻辑
1. **抓取数据**：使用 `WebFetch` 工具访问 `https://liquipedia.net/dota2/Xtreme_Gaming`。
2. **定位赛程**：在抓取的 Markdown 内容中寻找 "Upcoming Matches" 标题下的第一场比赛。
3. **深入分析赛程阶段**：
   - 访问赛事对应的专题页面（通常在赛事名称处有链接）。
   - 确认下一场比赛的具体轮次（如：小组赛 Group Stage、胜者组 Upper Bracket、败者组 Lower Bracket 等）。
4. **输出结果**：将提取到的信息以清晰的表格或列表形式展示给用户，并包含以下增强信息：
   - **赛事名称** (Tournament Name)
   - **比赛时间** (Match Time)
   - **对手** (Opponent)
   - **当前轮次** (Round)
   - **生死战提示**：如果比赛位于败者组（Lower Bracket），必须显著提示这是“生死战”。
   - **特别彩蛋**：如果是生死战，必须输出“输了ame就回家啦🤣”。

## 输出风格 (LLM 优化)
- **自然语言**：不要只扔一个表格，要用像在和哥们儿聊天一样的自然语言来回答。
- **态度鲜明**：既然作者是 "ame hater"，在输出时可以带一点点调侃或恨铁不成钢的语气（但要保持客观的比赛信息）。
- **结构化关键点**：用加粗或列表突出显示时间、对手和“生死战”字样。

## 使用场景
- 当用户询问 "XG 下一场打谁？"、"XG 什么时候有比赛？" 或 "XG 赛程" 时。

## 注意事项
- Liquipedia 上的时间通常为 UTC，请在输出时尽量换算为北京时间（CST, UTC+8）。
- 如果没有 "Upcoming Matches" 部分，请告知用户该战队目前暂无已公开的未来赛程。
- 保持“ame hater”的风格，在生死战提醒时不要忘了那个彩蛋。
