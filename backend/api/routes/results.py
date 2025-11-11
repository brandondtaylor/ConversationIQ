"""
Results and analytics endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from typing import Optional

from src.evaluation.evaluator import EvaluationAnalyzer
from src.tests.executor import TestExecutor

router = APIRouter()


@router.get("/{test_id}")
async def get_test_results(test_id: str):
    """Get complete test results with analysis"""
    analyzer = EvaluationAnalyzer()
    try:
        analysis = analyzer.analyze_test(test_id)
        if "error" in analysis:
            raise HTTPException(status_code=404, detail=analysis["error"])
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{test_id}/summary")
async def get_test_summary(test_id: str):
    """Get test results summary"""
    analyzer = EvaluationAnalyzer()
    try:
        analysis = analyzer.analyze_test(test_id)
        if "error" in analysis:
            raise HTTPException(status_code=404, detail=analysis["error"])
        return analysis["overall"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{test_id}/evaluations")
async def get_test_evaluations(test_id: str):
    """Get all evaluations for a test"""
    executor = TestExecutor()
    evaluations = executor.get_test_evaluations(test_id)
    return [e.model_dump() for e in evaluations]


@router.get("/{test_id}/export")
async def export_test_results(
    test_id: str,
    format: str = Query("json", regex="^(json|csv|txt|report)$")
):
    """Export test results in specified format"""
    analyzer = EvaluationAnalyzer()
    try:
        output_file = analyzer.export_results(test_id, format)
        return FileResponse(
            output_file,
            media_type="application/octet-stream",
            filename=os.path.basename(output_file)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{test_id}/by-question")
async def get_results_by_question(test_id: str):
    """Get results aggregated by question"""
    analyzer = EvaluationAnalyzer()
    try:
        analysis = analyzer.analyze_test(test_id)
        if "error" in analysis:
            raise HTTPException(status_code=404, detail=analysis["error"])
        return analysis["by_question"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{test_id}/by-agent")
async def get_results_by_agent(test_id: str):
    """Get results aggregated by agent"""
    analyzer = EvaluationAnalyzer()
    try:
        analysis = analyzer.analyze_test(test_id)
        if "error" in analysis:
            raise HTTPException(status_code=404, detail=analysis["error"])
        return analysis["by_agent"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


import os
