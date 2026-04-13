# Tang Dynasty Multi-Agent System

A fault-tolerant multi-agent collaboration framework inspired by the Tang Dynasty's Three Departments and Six Ministries system.

## Features

- **Three Departments (三省)**: Decision-making hub with separation of powers
  - Zhongshu (中书): Policy drafting
  - Menxia (门下): Review and veto power  
- **Six Ministries (六部)**: Parallel execution layer
  - Libu (吏部): Personnel/Permissions
  - Hubu (户部): Resources/Budget
  - Libu-content (礼部): Content generation
  - Bingbu (兵部): Security
  - Xingbu (刑部): Compliance
  - Gongbu (工部): Engineering/Deployment
- **Fault Tolerance**: Circuit breaker, timeout handling, graceful degradation
- **Real-time Dashboard**: Monitor all agents and tasks

## Installation

```bash
pip install asyncio aiohttp
```

## Quick Start

```python
from tang_agents import TangSystem
import asyncio

async def main():
    system = TangSystem()
    
    # Submit a task
    edict_id = await system.process("Launch marketing campaign for new anime")
    
    # Check status
    status = system.dashboard.get_status(edict_id)
    print(status)
    
    # Display dashboard
    system.dashboard.display()

asyncio.run(main())
```

## Architecture

```
User Request (Edict)
    ↓
[ZhongshuAgent] Draft policy
    ↓
[MenxiaAgent] Review (can veto/reject)
    ↓
[ShangshuAgent] Dispatch tasks
    ↓
[Six Ministries] Parallel execution
    ↓
[ShangshuAgent] Aggregate results
    ↓
Output / Human approval
```

## Fault Tolerance

Each agent has built-in fault tolerance:

- **Timeout handling**: Auto-degrade if execution exceeds limit
- **Circuit breaker**: Pause agent after consecutive failures
- **Fallback strategies**: Return default/template data on failure
- **Failure isolation**: One ministry failure doesn't crash others

## License

MIT