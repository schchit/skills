import asyncio
from tang_agents import TangSystem

async def main():
    """Example usage of Tang Agents"""
    
    # Initialize the system
    system = TangSystem()
    
    # Submit a task
    print("=" * 60)
    print("Tang Dynasty Multi-Agent System Demo")
    print("=" * 60)
    
    edict_id = await system.process("Create marketing strategy for new product launch")
    
    # Check status
    status = system.dashboard.get_status(edict_id)
    print(f"\nFinal status: {status['status']}")
    
    # Show dashboard
    system.dashboard.display()
    
    # If pending approval, you can approve it
    if status['status'] == 'pending_approval':
        system.approve(edict_id)

if __name__ == "__main__":
    asyncio.run(main())