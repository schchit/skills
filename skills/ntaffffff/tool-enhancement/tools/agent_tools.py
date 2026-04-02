#!/usr/bin/env python3
"""
子 Agent 调度工具集

提供多 Agent 协作能力
参考 Claude Code 的 Coordinator 系统设计
"""

from __future__ import annotations

import asyncio
import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from concurrent.futures import ThreadPoolExecutor

import sys
sys.path.insert(0, str(Path(__file__).parent))
from schema import BaseTool, ToolDefinition, ToolResult, ToolCapability


class AgentStatus(Enum):
    """Agent 状态"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentTask:
    """Agent 任务"""
    id: str
    name: str
    description: str
    prompt: str
    model: str = "default"
    status: AgentStatus = AgentStatus.IDLE
    result: Any = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class AgentSpawnTool(BaseTool):
    """Agent  spawn 工具 - 创建子 Agent"""
    
    def __init__(self):
        super().__init__(ToolDefinition(
            name="agent_spawn",
            description="创建并启动一个子 Agent 执行任务",
            input_schema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Agent 名称"},
                    "description": {"type": "string", "description": "Agent 描述"},
                    "prompt": {"type": "string", "description": "Agent 任务提示"},
                    "model": {"type": "string", "description": "使用的模型"},
                    "timeout": {"type": "number", "default": 300, "description": "超时时间(秒)"}
                },
                "required": ["name", "prompt"]
            },
            capabilities={ToolCapability.EXECUTE},
            tags=["agent", "spawn", "create", "sub-agent"],
            examples=["创建 Agent: name='code-reviewer', prompt='审查这段代码...'"]
        ))
        self._agents: Dict[str, AgentTask] = {}
        self._executor = ThreadPoolExecutor(max_workers=5)
    
    async def execute(self, **kwargs) -> ToolResult:
        name = kwargs.get("name")
        description = kwargs.get("description", "")
        prompt = kwargs.get("prompt")
        model = kwargs.get("model", "default")
        timeout = kwargs.get("timeout", 300)
        
        try:
            task_id = str(uuid.uuid4())
            
            # 创建任务
            task = AgentTask(
                id=task_id,
                name=name,
                description=description,
                prompt=prompt,
                model=model,
                status=AgentStatus.RUNNING
            )
            
            self._agents[task_id] = task
            
            # 异步执行（这里简化了，实际需要调用 LLM API）
            asyncio.create_task(self._run_agent(task_id, timeout))
            
            return ToolResult(
                success=True,
                data={
                    "task_id": task_id,
                    "name": name,
                    "status": "running",
                    "message": f"Agent '{name}' 已启动"
                }
            )
            
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    async def _run_agent(self, task_id: str, timeout: int):
        """运行 Agent（简化实现）"""
        task = self._agents.get(task_id)
        if not task:
            return
        
        try:
            # 这里应该调用实际的 LLM API
            # 简化：模拟执行
            await asyncio.sleep(2)  # 模拟执行时间
            
            task.status = AgentStatus.COMPLETED
            task.result = {"output": f"Agent '{task.name}' completed", "task_id": task_id}
            task.completed_at = datetime.now()
            
        except Exception as e:
            task.status = AgentStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
    
    def get_agent_status(self, task_id: str) -> Optional[AgentTask]:
        """获取 Agent 状态"""
        return self._agents.get(task_id)
    
    def list_agents(self) -> List[AgentTask]:
        """列出所有 Agent"""
        return list(self._agents.values())


class AgentDelegateTool(BaseTool):
    """Agent 委托工具 - 将任务委托给子 Agent"""
    
    def __init__(self):
        super().__init__(ToolDefinition(
            name="agent_delegate",
            description="将任务委托给已存在的 Agent",
            input_schema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Agent 任务 ID"},
                    "message": {"type": "string", "description": "发送的消息"},
                    "timeout": {"type": "number", "default": 60}
                },
                "required": ["task_id", "message"]
            },
            capabilities={ToolCapability.EXECUTE},
            tags=["agent", "delegate", "message", "communicate"]
        ))
        self._spawn_tool: Optional[AgentSpawnTool] = None
    
    @property
    def spawn_tool(self) -> AgentSpawnTool:
        if not self._spawn_tool:
            self._spawn_tool = AgentSpawnTool()
        return self._spawn_tool
    
    async def execute(self, **kwargs) -> ToolResult:
        task_id = kwargs.get("task_id")
        message = kwargs.get("message")
        timeout = kwargs.get("timeout", 60)
        
        task = self.spawn_tool.get_agent_status(task_id)
        if not task:
            return ToolResult(success=False, error=f"Agent 不存在: {task_id}")
        
        if task.status != AgentStatus.RUNNING:
            return ToolResult(success=False, error=f"Agent 当前状态: {task.status.value}")
        
        # 简化实现
        return ToolResult(
            success=True,
            data={
                "task_id": task_id,
                "message": message,
                "response": "消息已发送"
            }
        )


class AgentResultTool(BaseTool):
    """Agent 结果获取工具"""
    
    def __init__(self):
        super().__init__(ToolDefinition(
            name="agent_result",
            description="获取 Agent 执行结果",
            input_schema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Agent 任务 ID"},
                    "wait": {"type": "boolean", "default": False, "description": "等待完成"},
                    "timeout": {"type": "number", "default": 60, "description": "等待超时"}
                },
                "required": ["task_id"]
            },
            capabilities={ToolCapability.EXECUTE},
            tags=["agent", "result", "output", "get"]
        ))
        self._spawn_tool: Optional[AgentSpawnTool] = None
    
    @property
    def spawn_tool(self) -> AgentSpawnTool:
        if not self._spawn_tool:
            self._spawn_tool = AgentSpawnTool()
        return self._spawn_tool
    
    async def execute(self, **kwargs) -> ToolResult:
        task_id = kwargs.get("task_id")
        wait = kwargs.get("wait", False)
        timeout = kwargs.get("timeout", 60)
        
        task = self.spawn_tool.get_agent_status(task_id)
        if not task:
            return ToolResult(success=False, error=f"Agent 不存在: {task_id}")
        
        if wait and task.status == AgentStatus.RUNNING:
            # 等待完成
            try:
                await asyncio.wait_for(
                    self._wait_for_completion(task_id),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                return ToolResult(
                    success=False,
                    error=f"等待超时 ({timeout}s)"
                )
        
        return ToolResult(
            success=task.status == AgentStatus.COMPLETED,
            data={
                "task_id": task_id,
                "name": task.name,
                "status": task.status.value,
                "result": task.result,
                "error": task.error,
                "created_at": task.created_at.isoformat(),
                "completed_at": task.completed_at.isoformat() if task.completed_at else None
            }
        )
    
    async def _wait_for_completion(self, task_id: str):
        """等待任务完成"""
        while True:
            task = self.spawn_tool.get_agent_status(task_id)
            if task and task.status != AgentStatus.RUNNING:
                break
            await asyncio.sleep(0.5)


class AgentListTool(BaseTool):
    """Agent 列表工具"""
    
    def __init__(self):
        super().__init__(ToolDefinition(
            name="agent_list",
            description="列出所有子 Agent",
            input_schema={
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "按状态过滤"}
                }
            },
            capabilities={ToolCapability.EXECUTE},
            tags=["agent", "list", "status"]
        ))
        self._spawn_tool: Optional[AgentSpawnTool] = None
    
    @property
    def spawn_tool(self) -> AgentSpawnTool:
        if not self._spawn_tool:
            self._spawn_tool = AgentSpawnTool()
        return self._spawn_tool
    
    async def execute(self, **kwargs) -> ToolResult:
        status_filter = kwargs.get("status")
        
        agents = self.spawn_tool.list_agents()
        
        if status_filter:
            agents = [a for a in agents if a.status.value == status_filter]
        
        return ToolResult(
            success=True,
            data={
                "agents": [
                    {
                        "task_id": a.id,
                        "name": a.name,
                        "description": a.description,
                        "status": a.status.value,
                        "created_at": a.created_at.isoformat()
                    }
                    for a in agents
                ],
                "count": len(agents)
            }
        )


class AgentCancelTool(BaseTool):
    """Agent 取消工具"""
    
    def __init__(self):
        super().__init__(ToolDefinition(
            name="agent_cancel",
            description="取消正在运行的 Agent",
            input_schema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Agent 任务 ID"}
                },
                "required": ["task_id"]
            },
            capabilities={ToolCapability.EXECUTE},
            tags=["agent", "cancel", "kill", "stop"]
        ))
        self._spawn_tool: Optional[AgentSpawnTool] = None
    
    @property
    def spawn_tool(self) -> AgentSpawnTool:
        if not self._spawn_tool:
            self._spawn_tool = AgentSpawnTool()
        return self._spawn_tool
    
    async def execute(self, **kwargs) -> ToolResult:
        task_id = kwargs.get("task_id")
        
        task = self.spawn_tool.get_agent_status(task_id)
        if not task:
            return ToolResult(success=False, error=f"Agent 不存在: {task_id}")
        
        if task.status != AgentStatus.RUNNING:
            return ToolResult(success=False, error=f"Agent 不在运行状态: {task.status.value}")
        
        task.status = AgentStatus.CANCELLED
        task.completed_at = datetime.now()
        
        return ToolResult(
            success=True,
            data={
                "task_id": task_id,
                "cancelled": True
            }
        )


class CoordinatorTool(BaseTool):
    """多 Agent 协调器工具 - 参考 Claude Code Coordinator"""
    
    def __init__(self):
        super().__init__(ToolDefinition(
            name="coordinator",
            description="协调多个子 Agent 完成复杂任务 (Research → Synthesis → Implementation → Verification)",
            input_schema={
                "type": "object",
                "properties": {
                    "task": {"type": "string", "description": "总体任务描述"},
                    "phases": {"type": "array", "description": "工作阶段配置"},
                    "parallel": {"type": "boolean", "default": True, "description": "是否并行执行"}
                },
                "required": ["task"]
            },
            capabilities={ToolCapability.EXECUTE},
            tags=["agent", "coordinator", "multi-agent", "orchestration"]
        ))
        self._spawn_tool = AgentSpawnTool()
    
    async def execute(self, **kwargs) -> ToolResult:
        task = kwargs.get("task")
        phases = kwargs.get("phases", ["research", "synthesis", "implementation", "verification"])
        parallel = kwargs.get("parallel", True)
        
        # 定义各阶段的任务提示
        phase_prompts = {
            "research": f"Research: 调查并收集关于以下任务的信息: {task}",
            "synthesis": f"Synthesis: 汇总研究发现，制定解决方案",
            "implementation": f"Implementation: 执行解决方案",
            "verification": f"Verification: 验证实现是否正确"
        }
        
        results = {}
        
        if parallel:
            # 并行执行所有阶段
            tasks = []
            for phase in phases:
                prompt = phase_prompts.get(phase, f"执行阶段: {phase}")
                task_id = str(uuid.uuid4())
                task_obj = AgentTask(
                    id=task_id,
                    name=f"coordinator-{phase}",
                    description=phase,
                    prompt=prompt,
                    status=AgentStatus.RUNNING
                )
                self._spawn_tool._agents[task_id] = task_obj
                tasks.append(self._run_phase(task_id))
            
            # 等待所有完成
            await asyncio.gather(*tasks)
            
            for phase in phases:
                # 简化：取最后一个
                pass
            
        else:
            # 顺序执行
            for phase in phases:
                prompt = phase_prompts.get(phase, f"执行阶段: {phase}")
                # 简化：直接返回提示
                results[phase] = {"status": "simulated", "prompt": prompt}
        
        return ToolResult(
            success=True,
            data={
                "task": task,
                "phases": phases,
                "results": results,
                "mode": "parallel" if parallel else "sequential"
            }
        )
    
    async def _run_phase(self, task_id: str):
        """运行单个阶段"""
        await asyncio.sleep(1)  # 模拟
        task = self._spawn_tool._agents.get(task_id)
        if task:
            task.status = AgentStatus.COMPLETED
            task.result = {"output": "phase completed"}
            task.completed_at = datetime.now()


# 导出所有工具
AGENT_TOOLS = [
    AgentSpawnTool,
    AgentDelegateTool,
    AgentResultTool,
    AgentListTool,
    AgentCancelTool,
    CoordinatorTool,
]


def register_tools(registry):
    """注册所有 Agent 工具到注册表"""
    for tool_class in AGENT_TOOLS:
        tool = tool_class()
        registry.register(tool, "agent")
    return len(AGENT_TOOLS)