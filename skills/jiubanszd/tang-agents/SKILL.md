# Tang Agents - Multi-Agent Collaboration System

## Overview

A fault-tolerant multi-agent collaboration framework inspired by the Tang Dynasty's Three Departments and Six Ministries system. This system implements separation of powers, parallel execution, and comprehensive fault tolerance.

## Architecture

```
User Request
    ↓
[Zhongshu] Policy Drafting
    ↓
[Menxia] Review & Veto (Checks & Balances)
    ↓
[Shangshu] Task Dispatch
    ↓
[Six Ministries] Parallel Execution
    - Libu: Permissions
    - Hubu: Resources
    - Libu-Content: Content Generation
    - Bingbu: Security
    - Xingbu: Compliance
    - Gongbu: Deployment
    ↓
Output / Human Approval
```

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
import asyncio
from tang_agents import TangSystem

async def main():
    system = TangSystem()
    
    # Process a task
    edict_id = await system.process("Your task description")
    
    # Check status
    status = system.dashboard.get_status(edict_id)
    print(status)
    
    # Display dashboard
    system.dashboard.display()

asyncio.run(main())
```

## Fault Tolerance Features

1. **Timeout Handling**: Each agent has independent timeout (3-15s)
2. **Circuit Breaker**: Auto-pause after 3 consecutive failures
3. **Graceful Degradation**: Return template data on failure
4. **Failure Isolation**: One ministry failure doesn't crash others
5. **Retry Mechanism**: Menxia review allows up to 3 retries

## License

MIT