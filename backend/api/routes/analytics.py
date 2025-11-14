"""
Analytics and insights endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.storage.database import EvaluationModel, get_db_manager
from src.agents.focus_group_analyzer import analyze_focus_group_evaluation

router = APIRouter()


@router.get("/trend/{test_id}")
async def get_trend_analysis(
    test_id: str,
    time_range_days: Optional[int] = 7
):
    """
    Get trend analysis for evaluation scores over time.

    Args:
        test_id: Test ID
        time_range_days: Number of days to analyze (default: 7)

    Returns:
        Trend data with ratings over time
    """
    session = get_db_manager().get_session()

    try:
        # Calculate cutoff date
        cutoff_date = datetime.utcnow() - timedelta(days=time_range_days)

        # Query evaluations with timestamps
        evaluations = session.query(EvaluationModel).filter(
            EvaluationModel.test_id == test_id,
            EvaluationModel.timestamp >= cutoff_date
        ).order_by(EvaluationModel.timestamp).all()

        if not evaluations:
            raise HTTPException(status_code=404, detail="No evaluations found for this test")

        # Group by date
        trend_data = {}
        for eval in evaluations:
            date_key = eval.timestamp.strftime("%Y-%m-%d")
            if date_key not in trend_data:
                trend_data[date_key] = {
                    "date": date_key,
                    "ratings": [],
                    "response_times": [],
                    "evaluation_count": 0
                }

            if eval.rating is not None:
                trend_data[date_key]["ratings"].append(eval.rating)
            if eval.response_time is not None:
                trend_data[date_key]["response_times"].append(eval.response_time)
            trend_data[date_key]["evaluation_count"] += 1

        # Calculate averages
        trend_summary = []
        for date_key, data in sorted(trend_data.items()):
            avg_rating = sum(data["ratings"]) / len(data["ratings"]) if data["ratings"] else None
            avg_response_time = sum(data["response_times"]) / len(data["response_times"]) if data["response_times"] else None

            trend_summary.append({
                "date": data["date"],
                "avg_rating": round(avg_rating, 2) if avg_rating else None,
                "avg_response_time": round(avg_response_time, 3) if avg_response_time else None,
                "evaluation_count": data["evaluation_count"],
                "rating_range": {
                    "min": min(data["ratings"]) if data["ratings"] else None,
                    "max": max(data["ratings"]) if data["ratings"] else None
                }
            })

        return {
            "test_id": test_id,
            "time_range_days": time_range_days,
            "trend_data": trend_summary,
            "total_evaluations": len(evaluations)
        }

    finally:
        session.close()


@router.get("/response-times/{test_id}")
async def get_response_time_analysis(test_id: str):
    """
    Get detailed response time analysis.

    Args:
        test_id: Test ID

    Returns:
        Response time statistics
    """
    session = get_db_manager().get_session()

    try:
        evaluations = session.query(EvaluationModel).filter(
            EvaluationModel.test_id == test_id,
            EvaluationModel.response_time.isnot(None)
        ).all()

        if not evaluations:
            raise HTTPException(status_code=404, detail="No response time data found")

        response_times = [e.response_time for e in evaluations if e.response_time is not None]

        return {
            "test_id": test_id,
            "count": len(response_times),
            "avg_response_time": round(sum(response_times) / len(response_times), 3),
            "min_response_time": round(min(response_times), 3),
            "max_response_time": round(max(response_times), 3),
            "response_times": response_times
        }

    finally:
        session.close()


@router.get("/focus-group-insights/{evaluation_id}")
async def get_focus_group_insights(evaluation_id: str):
    """
    Get detailed insights from a focus group evaluation.

    Args:
        evaluation_id: Evaluation ID

    Returns:
        Focus group insights including consensus, disagreements, and influential agents
    """
    session = get_db_manager().get_session()

    try:
        evaluation = session.query(EvaluationModel).filter(
            EvaluationModel.id == evaluation_id
        ).first()

        if not evaluation:
            raise HTTPException(status_code=404, detail="Evaluation not found")

        if evaluation.agent_id != "focus_group":
            raise HTTPException(status_code=400, detail="This evaluation is not a focus group evaluation")

        # Convert to dict for analysis
        eval_dict = {
            "raw_evaluation": evaluation.raw_evaluation
        }

        insights = analyze_focus_group_evaluation(eval_dict)

        if insights is None:
            raise HTTPException(status_code=400, detail="Failed to analyze focus group evaluation")

        return {
            "evaluation_id": evaluation_id,
            "test_id": evaluation.test_id,
            "question_id": evaluation.question_id,
            "insights": insights
        }

    finally:
        session.close()


@router.get("/ideal-response/{test_id}")
async def get_ideal_response_examples(test_id: str, min_rating: float = 8.0):
    """
    Get example "ideal responses" based on high evaluation scores.

    Args:
        test_id: Test ID
        min_rating: Minimum rating to be considered ideal (default: 8.0)

    Returns:
        List of high-rated responses with their evaluations
    """
    session = get_db_manager().get_session()

    try:
        # Query high-rated evaluations
        high_rated = session.query(EvaluationModel).filter(
            EvaluationModel.test_id == test_id,
            EvaluationModel.rating >= min_rating
        ).order_by(EvaluationModel.rating.desc()).limit(10).all()

        if not high_rated:
            return {
                "test_id": test_id,
                "min_rating": min_rating,
                "ideal_examples": [],
                "message": f"No responses found with rating >= {min_rating}"
            }

        ideal_examples = []
        for eval in high_rated:
            ideal_examples.append({
                "evaluation_id": eval.id,
                "question_id": eval.question_id,
                "agent_id": eval.agent_id,
                "rating": eval.rating,
                "api_response": eval.api_response,
                "likes": eval.likes,
                "suggestions": eval.suggestions,
                "agent_perspective": eval.agent_perspective,
                "response_time": eval.response_time
            })

        # Extract common characteristics from ideal responses
        all_likes = []
        for example in ideal_examples:
            all_likes.extend(example["likes"])

        # Count most common likes
        from collections import Counter
        common_characteristics = Counter(all_likes).most_common(5)

        return {
            "test_id": test_id,
            "min_rating": min_rating,
            "count": len(ideal_examples),
            "ideal_examples": ideal_examples,
            "common_characteristics": [
                {"characteristic": char, "frequency": freq}
                for char, freq in common_characteristics
            ]
        }

    finally:
        session.close()
