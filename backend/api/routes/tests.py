"""
Test management endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional

from src.tests.config import TestConfigManager
from src.tests.executor import TestExecutor
from src.storage.schemas import TestConfig, TestConfigCreate, TestConfigUpdate, TestStatus, Question

router = APIRouter()


@router.get("", response_model=List[TestConfig])
async def list_tests(status: Optional[TestStatus] = None):
    """List all tests with optional status filter"""
    with TestConfigManager() as manager:
        return manager.list(status=status)


@router.post("", response_model=TestConfig, status_code=201)
async def create_test(config: TestConfigCreate):
    """Create a new test configuration"""
    with TestConfigManager() as manager:
        return manager.create(config)


@router.get("/{test_id}", response_model=TestConfig)
async def get_test(test_id: str):
    """Get test configuration by ID"""
    with TestConfigManager() as manager:
        test = manager.get(test_id)
        if not test:
            raise HTTPException(status_code=404, detail="Test not found")
        return test


@router.put("/{test_id}", response_model=TestConfig)
async def update_test(test_id: str, update: TestConfigUpdate):
    """Update a test configuration"""
    with TestConfigManager() as manager:
        updated = manager.update(test_id, update)
        if not updated:
            raise HTTPException(status_code=404, detail="Test not found")
        return updated


@router.delete("/{test_id}", status_code=204)
async def delete_test(test_id: str):
    """Delete a test configuration"""
    with TestConfigManager() as manager:
        deleted = manager.delete(test_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Test not found")


@router.get("/{test_id}/questions", response_model=List[Question])
async def get_test_questions(test_id: str):
    """Get all questions for a test"""
    with TestConfigManager() as manager:
        return manager.get_questions(test_id)


@router.post("/{test_id}/questions", status_code=201)
async def add_test_questions(test_id: str, questions: List[dict]):
    """Add questions to a test"""
    from src.storage.schemas import QuestionCreate

    with TestConfigManager() as manager:
        question_objs = [QuestionCreate(**q) for q in questions]
        success = manager.add_questions(test_id, question_objs)
        if not success:
            raise HTTPException(status_code=404, detail="Test not found")
        return {"message": f"Added {len(questions)} questions"}


@router.post("/{test_id}/run")
async def run_test(test_id: str, background_tasks: BackgroundTasks):
    """Start running a test"""
    # Run test in background
    def run_test_task():
        executor = TestExecutor()
        try:
            executor.run_test(test_id)
        except Exception as e:
            print(f"Test execution failed: {e}")

    background_tasks.add_task(run_test_task)

    return {"message": "Test started", "test_id": test_id}


@router.get("/{test_id}/status")
async def get_test_status(test_id: str):
    """Get current test status"""
    with TestConfigManager() as manager:
        test = manager.get(test_id)
        if not test:
            raise HTTPException(status_code=404, detail="Test not found")

        return {
            "test_id": test.id,
            "status": test.status,
            "name": test.name
        }
