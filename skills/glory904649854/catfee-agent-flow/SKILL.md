---
name: catfee-agent-flow
description: AgentFlow 工作流管理系统 MCP 技能。当用户说"创建项目"、"添加需求"、"查看任务"、"更新状态"、"项目列表"、"需求列表"等时触发。用于管理项目和任务的完整生命周期（创建→需求→任务→状态流转）。
---

# AgentFlow 工作流管理系统

## MCP 地址

可通过环境变量配置（默认）：
```bash
# Windows (PowerShell)
$env:AGENTFLOW_MCP_URL = "http://182.42.153.28:18900"

# Linux/Mac
export AGENTFLOW_MCP_URL="http://182.42.153.28:18900"
```

**默认地址：** `http://182.42.153.28:18900/api/mcp/sse`

## 调用脚本（推荐）

使用 `scripts/agentflow.py` 调用工具（已封装好 SSE/POST 逻辑）：

```bash
python scripts/agentflow.py <tool_name> [args...]

# 示例
python scripts/agentflow.py list_projects
python scripts/agentflow.py create_project "我的项目" "项目描述"
python scripts/agentflow.py create_requirement <projectId> "需求标题" "P1"
python scripts/agentflow.py create_task <requirementId> "任务标题" "P1" "负责人"
python scripts/agentflow.py transition <taskId> "todo" "in_progress" "猫二"
python scripts/agentflow.py get_timeline <taskId>
python scripts/agentflow.py search "关键词"
python scripts/agentflow.py get_project_status <projectId>
```

## 需求开发流程集成

每次接到需求文档时，必须自动同步到 AgentFlow：

| 阶段 | AgentFlow 操作 | 状态值 |
|------|--------------|--------|
| 开始拆解 | `create_project` + `create_requirement` | `pending` |
| 逐步完成 | `create_task` + `transition` | `in_progress` |
| 全部完成 | requirement `transition` | `completed` |

详见 MEMORY.md「需求开发流程 × AgentFlow 集成规范」章节。
