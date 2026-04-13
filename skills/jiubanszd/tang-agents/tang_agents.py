"""
Tang Dynasty Multi-Agent System
A fault-tolerant multi-agent collaboration framework
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from datetime import datetime
from abc import ABC, abstractmethod


class Status(Enum):
    PENDING = "pending"
    DRAFTING = "drafting"
    REVIEWING = "reviewing"
    REJECTED = "rejected"
    EXECUTING = "executing"
    APPROVING = "pending_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    DEGRADED = "degraded"


@dataclass
class AgentHealth:
    """Health status monitoring for each agent"""
    agent_name: str
    status: str = "healthy"
    last_success: datetime = field(default_factory=datetime.now)
    failure_count: int = 0
    total_calls: int = 0
    avg_response_time: float = 0.0


@dataclass
class Edict:
    """A task/document to be processed"""
    id: str
    content: str
    status: Status = Status.PENDING
    draft: Dict = field(default_factory=dict)
    review_result: Dict = field(default_factory=dict)
    execution_results: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    history: List[Dict] = field(default_factory=list)
    retry_count: int = 0
    max_retry: int = 3
    timeout: int = 10
    
    def log(self, agent: str, action: str):
        self.history.append({
            "agent": agent,
            "action": action,
            "time": datetime.now().isoformat()
        })


class CircuitBreaker:
    """Circuit breaker pattern to prevent cascade failures"""
    
    def __init__(self, failure_threshold=3, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = {}
        self.last_failure_time = {}
        self.is_open = {}
    
    def call(self, agent_name: str, func: Callable, *args, **kwargs):
        """Execute with circuit breaker protection"""
        if self.is_open.get(agent_name, False):
            if time.time() - self.last_failure_time.get(agent_name, 0) > self.recovery_timeout:
                self.is_open[agent_name] = False
                self.failures[agent_name] = 0
            else:
                raise Exception(f"Agent {agent_name} circuit open - service unavailable")
        
        try:
            result = func(*args, **kwargs)
            self.failures[agent_name] = 0
            return result
        except Exception as e:
            self.failures[agent_name] = self.failures.get(agent_name, 0) + 1
            self.last_failure_time[agent_name] = time.time()
            
            if self.failures[agent_name] >= self.failure_threshold:
                self.is_open[agent_name] = True
                print(f"[!] Circuit breaker opened for {agent_name}")
            
            raise e


class BaseAgent(ABC):
    """Base agent class with fault tolerance"""
    
    def __init__(self, name: str, timeout: int = 10):
        self.name = name
        self.timeout = timeout
        self.health = AgentHealth(agent_name=name)
        self.circuit_breaker = CircuitBreaker()
        self.fallback_enabled = True
    
    def execute_with_fallback(self, task: Dict, edict: Edict) -> Dict:
        """Execute with timeout and fallback handling"""
        start_time = time.time()
        
        try:
            result = self.circuit_breaker.call(
                self.name, 
                self._execute_with_timeout,
                task,
                edict
            )
            self._update_health(True, time.time() - start_time)
            return result
            
        except FutureTimeoutError:
            print(f"[TIMEOUT] [{self.name}] Execution timeout")
            self._update_health(False, time.time() - start_time)
            return self._timeout_fallback(task, edict)
            
        except Exception as e:
            print(f"[ERROR] [{self.name}] Execution error: {e}")
            self._update_health(False, time.time() - start_time)
            return self._error_fallback(task, edict, str(e))
    
    def _execute_with_timeout(self, task: Dict, edict: Edict) -> Dict:
        """Execute with timeout control"""
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.execute, task, edict)
            return future.result(timeout=self.timeout)
    
    @abstractmethod
    def execute(self, task: Dict, edict: Edict) -> Dict:
        """Implement specific logic in subclasses"""
        pass
    
    def _timeout_fallback(self, task: Dict, edict: Edict) -> Dict:
        """Fallback when timeout occurs"""
        print(f"[FALLBACK] [{self.name}] Using timeout fallback")
        return {
            "dept": self.name,
            "status": "degraded",
            "reason": "timeout",
            "fallback_data": self._get_fallback_data(task)
        }
    
    def _error_fallback(self, task: Dict, edict: Edict, error: str) -> Dict:
        """Fallback when error occurs"""
        print(f"[FALLBACK] [{self.name}] Using error fallback")
        return {
            "dept": self.name,
            "status": "failed",
            "reason": error,
            "fallback_data": self._get_fallback_data(task)
        }
    
    def _get_fallback_data(self, task: Dict) -> Any:
        """Override in subclass to provide fallback data"""
        return None
    
    def _update_health(self, success: bool, response_time: float):
        """Update health status"""
        self.health.total_calls += 1
        if success:
            self.health.last_success = datetime.now()
            self.health.avg_response_time = (
                (self.health.avg_response_time * (self.health.total_calls - 1) + response_time)
                / self.health.total_calls
            )
        else:
            self.health.failure_count += 1
            self.health.status = "degraded" if self.health.failure_count < 3 else "failed"


# ==================== Three Departments (三省) ====================

class ZhongshuAgent(BaseAgent):
    """Zhongshu Department: Policy drafting and decision-making"""
    
    def __init__(self):
        super().__init__("Zhongshu", timeout=15)
        self.templates = {
            "default": {
                "strategy": "Standard approach",
                "options": ["conservative", "balanced", "aggressive"],
                "selected": "balanced"
            }
        }
    
    def execute(self, task: Dict, edict: Edict) -> Dict:
        """Draft policy proposals"""
        print(f"[Zhongshu] Drafting edict #{edict.id}...")
        time.sleep(0.5)
        
        content = task.get("content", "")
        draft = {
            "strategy": f"Solution for: {content}",
            "options": [
                {"type": "conservative", "confidence": 0.8, "cost": 100, "risk": "low"},
                {"type": "balanced", "confidence": 0.9, "cost": 200, "risk": "medium"},
                {"type": "aggressive", "confidence": 0.7, "cost": 500, "risk": "high"}
            ],
            "selected": "balanced",
            "estimated_time": "2 days"
        }
        
        return {"status": "success", "draft": draft}
    
    def _get_fallback_data(self, task: Dict) -> Dict:
        return self.templates["default"]


class MenxiaAgent(BaseAgent):
    """Menxia Department: Review and veto power (checks and balances)"""
    
    def __init__(self):
        super().__init__("Menxia", timeout=10)
        self.rejection_count = {}
        self.max_retry = 3
    
    def execute(self, task: Dict, edict: Edict) -> Dict:
        """Review draft with power to reject (veto)"""
        print(f"[Menxia] Reviewing edict #{edict.id}...")
        
        draft = task.get("draft", {})
        risks = []
        
        if draft.get("selected") == "aggressive":
            risks.append("High-risk strategy requires additional approval")
        
        selected_option = next(
            (o for o in draft.get("options", []) if o.get("type") == draft.get("selected")),
            {}
        )
        if selected_option.get("cost", 0) > 1000:
            risks.append("Budget exceeds limit - requires special approval")
        
        # Check sensitive keywords in strategy text only (not in field names)
        strategy_text = draft.get("strategy", "")
        if any(word in strategy_text.lower() for word in ["sensitive", "violation", "risk"]):
            risks.append("Content contains sensitive keywords")
        
        return {
            "passed": len(risks) == 0,
            "risks": risks,
            "seal": "Menxia_Approved" if len(risks) == 0 else None,
            "review_time": datetime.now().isoformat()
        }
    
    def _error_fallback(self, task: Dict, edict: Edict, error: str) -> Dict:
        """When review fails, pass with manual review flag"""
        print(f"[WARN] [Menxia] Review system error - flagging for manual review")
        return {
            "passed": True,
            "risks": ["Review system error - manual review required"],
            "seal": "Temporary_Approval",
            "requires_manual_review": True
        }


class ShangshuAgent(BaseAgent):
    """Shangshu Department: Coordination and dispatch"""
    
    def __init__(self):
        super().__init__("Shangshu", timeout=5)
    
    def execute(self, task: Dict, edict: Edict) -> Dict:
        """Dispatch tasks to six ministries"""
        print(f"[Shangshu] Dispatching edict #{edict.id}...")
        
        content = task.get("content", "")
        tasks = {
            "libu": {"action": "permission_check", "target": content},
            "hubu": {"action": "resource_allocation", "budget": 200},
            "libu_content": {"action": "content_generation", "topic": content},
            "bingbu": {"action": "security_scan", "level": "standard"},
            "xingbu": {"action": "compliance_review", "strict": True},
            "gongbu": {"action": "deployment", "execute": True}
        }
        
        return {"status": "success", "tasks": tasks}
    
    def aggregate_results(self, edict: Edict, results: Dict) -> Dict:
        """Aggregate results from six ministries"""
        print(f"[Shangshu] Aggregating results for #{edict.id}...")
        
        failures = []
        degraded = []
        
        for dept, result in results.items():
            if result.get("status") == "failed":
                failures.append(dept)
            elif result.get("status") == "degraded":
                degraded.append(dept)
        
        draft = edict.draft
        high_risk = (
            draft.get("selected") == "aggressive" or 
            len(failures) > 0 or
            len([r for r in results.values() if r.get("requires_manual_review")]) > 0
        )
        
        if failures and len(failures) >= 3:
            return {
                "status": "failed",
                "message": f"{len(failures)} ministries failed execution",
                "failures": failures,
                "degraded": degraded
            }
        
        if high_risk:
            return {
                "status": "pending_approval",
                "message": "High risk or anomalies detected - requires approval",
                "failures": failures,
                "degraded": degraded,
                "results": results
            }
        
        return {
            "status": "completed",
            "failures": failures,
            "degraded": degraded,
            "results": results
        }


# ==================== Six Ministries (六部) ====================

class LibuAgent(BaseAgent):
    """Libu: Personnel and permissions"""
    def __init__(self):
        super().__init__("Libu", timeout=3)
    
    def execute(self, task: Dict, edict: Edict) -> Dict:
        print(f"[Libu] Checking permissions...")
        time.sleep(0.3)
        return {"dept": "Libu", "status": "success", "permission": "granted", "user_level": "LV5"}


class HubuAgent(BaseAgent):
    """Hubu: Resources and budget"""
    def __init__(self):
        super().__init__("Hubu", timeout=3)
    
    def execute(self, task: Dict, edict: Edict) -> Dict:
        print(f"[Hubu] Allocating resources...")
        budget = task.get("budget", 0)
        if budget > 1000:
            raise Exception("Insufficient budget")
        time.sleep(0.3)
        return {"dept": "Hubu", "status": "success", "allocated": budget, "remaining": 1000-budget}


class LibuContentAgent(BaseAgent):
    """Libu (Content): Content generation"""
    def __init__(self):
        super().__init__("Libu-Content", timeout=8)
        self.fallback_content = "[System Generated] Standard promotional copy"
    
    def execute(self, task: Dict, edict: Edict) -> Dict:
        print(f"[Libu-Content] Generating content...")
        topic = task.get("topic", "")
        time.sleep(0.5)
        
        content = f"Promotional copy for '{topic}': ..."
        return {"dept": "Libu-Content", "status": "success", "content": content, "word_count": 500}
    
    def _get_fallback_data(self, task: Dict) -> str:
        return self.fallback_content


class BingbuAgent(BaseAgent):
    """Bingbu: Security"""
    def __init__(self):
        super().__init__("Bingbu", timeout=5)
    
    def execute(self, task: Dict, edict: Edict) -> Dict:
        print(f"[Bingbu] Security scanning...")
        time.sleep(0.4)
        return {"dept": "Bingbu", "status": "success", "threats": [], "security_level": "A"}


class XingbuAgent(BaseAgent):
    """Xingbu: Compliance"""
    def __init__(self):
        super().__init__("Xingbu", timeout=5)
    
    def execute(self, task: Dict, edict: Edict) -> Dict:
        print(f"[Xingbu] Compliance review...")
        time.sleep(0.4)
        return {"dept": "Xingbu", "status": "success", "violations": [], "compliance_score": 98}


class GongbuAgent(BaseAgent):
    """Gongbu: Engineering and deployment"""
    def __init__(self):
        super().__init__("Gongbu", timeout=6)
    
    def execute(self, task: Dict, edict: Edict) -> Dict:
        print(f"[Gongbu] Deploying...")
        time.sleep(0.5)
        return {"dept": "Gongbu", "status": "success", "deployed": True, "api_calls": 5}


# ==================== Dashboard and System ====================

class TangDashboard:
    """Government dashboard for monitoring"""
    
    def __init__(self):
        self.edicts: Dict[str, Edict] = {}
        self.agents_health: Dict[str, AgentHealth] = {}
        self.agents_status = {
            "Zhongshu": "idle",
            "Menxia": "idle", 
            "Shangshu": "idle",
            "Libu": "idle",
            "Hubu": "idle",
            "Libu-Content": "idle",
            "Bingbu": "idle",
            "Xingbu": "idle",
            "Gongbu": "idle"
        }
    
    def submit_edict(self, content: str) -> str:
        """Submit a new edict (task)"""
        edict_id = f"EDICT_{len(self.edicts) + 1:04d}"
        edict = Edict(id=edict_id, content=content)
        self.edicts[edict_id] = edict
        
        print(f"\n{'='*60}")
        print(f"[NEW EDICT] #{edict_id}")
        print(f"   Content: {content}")
        print(f"{'='*60}")
        return edict_id
    
    def get_status(self, edict_id: str) -> Dict:
        """Query edict status"""
        edict = self.edicts.get(edict_id)
        if not edict:
            return {"error": "Edict not found"}
        
        return {
            "id": edict.id,
            "status": edict.status.value,
            "current_step": edict.history[-1] if edict.history else "pending",
            "retry_count": edict.retry_count,
            "draft": edict.draft,
            "review": edict.review_result,
            "execution": edict.execution_results
        }
    
    def display(self):
        """Display dashboard"""
        print(f"\n{'='*70}")
        print("TANG GOVERNMENT DASHBOARD")
        print(f"{'='*70}")
        
        status_count = {}
        for e in self.edicts.values():
            status_count[e.status.value] = status_count.get(e.status.value, 0) + 1
        
        print(f"\n[STATISTICS] {len(self.edicts)} total edicts")
        for status, count in status_count.items():
            print(f"   {status}: {count}")
        
        pending = [e for e in self.edicts.values() if e.status in [Status.PENDING, Status.DRAFTING]]
        if pending:
            print(f"\n[PENDING] ({len(pending)}):")
            for e in pending[:5]:
                print(f"   #{e.id}: {e.content[:20]}... [{e.status.value}]")
        
        rejected = [e for e in self.edicts.values() if e.status == Status.REJECTED]
        if rejected:
            print(f"\n[REJECTED] ({len(rejected)}):")
            for e in rejected:
                print(f"   #{e.id}: {e.review_result.get('risks', [])}")
        
        approving = [e for e in self.edicts.values() if e.status == Status.APPROVING]
        if approving:
            print(f"\n[PENDING APPROVAL] ({len(approving)}):")
            for e in approving:
                print(f"   #{e.id}")
        
        print(f"\n[AGENT STATUS]")
        for agent, status in self.agents_status.items():
            print(f"   {agent}: {status}")
        
        print(f"{'='*70}\n")


class TangSystem:
    """Main entry point for Tang Dynasty Multi-Agent System"""
    
    def __init__(self):
        self.zhongshu = ZhongshuAgent()
        self.menxia = MenxiaAgent()
        self.shangshu = ShangshuAgent()
        
        self.ministries = {
            "libu": LibuAgent(),
            "hubu": HubuAgent(),
            "libu_content": LibuContentAgent(),
            "bingbu": BingbuAgent(),
            "xingbu": XingbuAgent(),
            "gongbu": GongbuAgent()
        }
        
        self.dashboard = TangDashboard()
    
    async def process(self, content: str) -> str:
        """Process an edict through the complete workflow"""
        edict_id = self.dashboard.submit_edict(content)
        edict = self.dashboard.edicts[edict_id]
        
        try:
            # Stage 1: Zhongshu drafting
            print(f"\n[STAGE 1] Zhongshu Drafting")
            self.dashboard.agents_status["Zhongshu"] = "drafting"
            
            draft_result = self.zhongshu.execute_with_fallback(
                {"content": content}, 
                edict
            )
            
            if draft_result.get("status") == "degraded":
                edict.status = Status.DEGRADED
                print(f"[WARN] Using degraded solution")
            
            edict.draft = draft_result.get("draft", draft_result.get("fallback_data", {}))
            edict.status = Status.DRAFTING
            edict.log("Zhongshu", "Draft completed")
            self.dashboard.agents_status["Zhongshu"] = "idle"
            
            # Stage 2: Menxia review
            print(f"\n[STAGE 2] Menxia Review")
            self.dashboard.agents_status["Menxia"] = "reviewing"
            
            while edict.retry_count < edict.max_retry:
                review_result = self.menxia.execute_with_fallback(
                    {"draft": edict.draft}, 
                    edict
                )
                
                edict.review_result = review_result
                
                if review_result.get("passed"):
                    edict.status = Status.EXECUTING
                    edict.log("Menxia", "Review passed")
                    print(f"[OK] Menxia review passed")
                    break
                else:
                    edict.retry_count += 1
                    if edict.retry_count >= edict.max_retry:
                        edict.status = Status.FAILED
                        edict.log("Menxia", f"Rejected {edict.retry_count} times - abandoned")
                        print(f"[FAIL] Multiple rejections - task abandoned")
                        return edict_id
                    
                    edict.status = Status.REJECTED
                    edict.log("Menxia", f"Rejected - revision #{edict.retry_count}")
                    print(f"[RETRY] Rejected, redrafting... ({edict.retry_count}/{edict.max_retry})")
                    
                    draft_result = self.zhongshu.execute_with_fallback(
                        {"content": content, "revision": True}, 
                        edict
                    )
                    edict.draft = draft_result.get("draft", {})
            
            self.dashboard.agents_status["Menxia"] = "idle"
            
            # Stage 3: Shangshu dispatch
            print(f"\n[STAGE 3] Shangshu Dispatch")
            self.dashboard.agents_status["Shangshu"] = "dispatching"
            
            dispatch_result = self.shangshu.execute_with_fallback(
                {"content": content}, 
                edict
            )
            tasks = dispatch_result.get("tasks", {})
            edict.log("Shangshu", "Tasks dispatched")
            
            # Stage 4: Six ministries parallel execution
            print(f"\n[STAGE 4] Six Ministries Execution")
            self.dashboard.agents_status["Shangshu"] = "coordinating"
            
            results = {}
            
            async def execute_isolated(agent_key, agent, task):
                try:
                    self.dashboard.agents_status[agent.name] = "executing"
                    result = agent.execute_with_fallback(task, edict)
                    self.dashboard.agents_status[agent.name] = "idle"
                    return agent_key, result
                except Exception as e:
                    print(f"[CRASH] [{agent.name}] {e}")
                    self.dashboard.agents_status[agent.name] = "failed"
                    return agent_key, {
                        "dept": agent.name,
                        "status": "failed",
                        "reason": str(e)
                    }
            
            coroutines = [
                execute_isolated(key, agent, tasks[key])
                for key, agent in self.ministries.items()
            ]
            
            completed = await asyncio.gather(*coroutines, return_exceptions=True)
            
            for item in completed:
                if isinstance(item, Exception):
                    print(f"[EXCEPTION] Agent execution: {item}")
                    continue
                key, result = item
                results[key] = result
            
            edict.execution_results = results
            
            # Stage 5: Shangshu aggregation
            print(f"\n[STAGE 5] Results Aggregation")
            final_result = self.shangshu.aggregate_results(edict, results)
            self.dashboard.agents_status["Shangshu"] = "idle"
            
            if final_result["status"] == "failed":
                edict.status = Status.FAILED
                print(f"[FAIL] #{edict_id} Execution failed: {final_result.get('message')}")
                
            elif final_result["status"] == "pending_approval":
                edict.status = Status.APPROVING
                print(f"[APPROVAL] #{edict_id} Awaiting approval...")
                print(f"   Reason: {final_result.get('message')}")
                
            else:
                edict.status = Status.COMPLETED
                print(f"\n[OK] #{edict_id} Execution completed")
                if final_result.get("failures"):
                    print(f"   [WARN] Partial failures: {final_result['failures']}")
                if final_result.get("degraded"):
                    print(f"   [INFO] Degraded: {final_result['degraded']}")
            
            return edict_id
            
        except Exception as e:
            edict.status = Status.FAILED
            print(f"\n[SYSTEM ERROR] #{edict_id}: {e}")
            return edict_id
    
    def approve(self, edict_id: str) -> bool:
        """Emperor's approval for high-risk edicts"""
        edict = self.dashboard.edicts.get(edict_id)
        if not edict or edict.status != Status.APPROVING:
            return False
        
        edict.status = Status.COMPLETED
        edict.log("Emperor", "Approved")
        print(f"\n[APPROVED] #{edict_id} Approved by emperor")
        return True


# Example usage
async def main():
    """Demo run"""
    system = TangSystem()
    
    print("\n" + "="*70)
    print("TEST CASE 1: Normal Task")
    print("="*70)
    await system.process("Launch marketing campaign for Demon Slayer anime")
    
    print("\n" + "="*70)
    print("TEST CASE 2: High-Risk Task")
    print("="*70)
    await system.process("Aggressive promotion of sensitive content")
    
    print("\n" + "="*70)
    print("FINAL DASHBOARD")
    print("="*70)
    system.dashboard.display()


if __name__ == "__main__":
    asyncio.run(main())