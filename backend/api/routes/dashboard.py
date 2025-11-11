"""
Dashboard statistics endpoints
"""
from fastapi import APIRouter
from src.agents.manager import AgentManager
from src.api.config import APIConfigManager
from src.tests.config import TestConfigManager
from src.tests.executor import TestExecutor
from src.storage.schemas import TestStatus

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    with AgentManager() as agent_mgr, \
         APIConfigManager() as api_mgr, \
         TestConfigManager() as test_mgr:

        agents = agent_mgr.list()
        api_configs = api_mgr.list()
        all_tests = test_mgr.list()

        # Count tests by status
        tests_by_status = {
            "draft": len([t for t in all_tests if t.status == TestStatus.DRAFT]),
            "ready": len([t for t in all_tests if t.status == TestStatus.READY]),
            "running": len([t for t in all_tests if t.status == TestStatus.RUNNING]),
            "completed": len([t for t in all_tests if t.status == TestStatus.COMPLETED]),
            "failed": len([t for t in all_tests if t.status == TestStatus.FAILED])
        }

        # Get recent tests (last 10)
        recent_tests = sorted(all_tests, key=lambda t: t.created_at, reverse=True)[:10]

        # Get completed tests for stats
        completed_tests = [t for t in all_tests if t.status == TestStatus.COMPLETED]

        # Get total evaluations count
        total_evaluations = 0
        executor = TestExecutor()
        for test in completed_tests:
            evals = executor.get_test_evaluations(test.id)
            total_evaluations += len(evals)

        return {
            "total_agents": len(agents),
            "total_api_configs": len(api_configs),
            "total_tests": len(all_tests),
            "tests_by_status": tests_by_status,
            "total_evaluations": total_evaluations,
            "recent_tests": [
                {
                    "id": t.id,
                    "name": t.name,
                    "status": t.status,
                    "created_at": t.created_at.isoformat(),
                    "agent_count": len(t.agent_ids)
                }
                for t in recent_tests
            ]
        }
