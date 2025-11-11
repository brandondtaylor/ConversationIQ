"""
Results aggregation and analysis.
"""
from typing import List, Dict, Any, Tuple
from collections import Counter
import statistics

from ..storage.schemas import Evaluation


class ResultsAggregator:
    """Aggregates and analyzes evaluation results"""

    @staticmethod
    def aggregate_test_results(evaluations: List[Evaluation]) -> Dict[str, Any]:
        """
        Aggregate results from all evaluations in a test.

        Args:
            evaluations: List of evaluations

        Returns:
            Dict with aggregated results
        """
        if not evaluations:
            return {
                "total_evaluations": 0,
                "error": "No evaluations found"
            }

        # Calculate ratings statistics
        ratings = [e.rating for e in evaluations if e.rating is not None]
        rating_stats = ResultsAggregator._calculate_rating_stats(ratings)

        # Aggregate likes, dislikes, suggestions
        all_likes = []
        all_dislikes = []
        all_suggestions = []

        for eval in evaluations:
            all_likes.extend(eval.likes)
            all_dislikes.extend(eval.dislikes)
            all_suggestions.extend(eval.suggestions)

        # Find common themes
        common_likes = ResultsAggregator._find_common_themes(all_likes, top_n=10)
        common_dislikes = ResultsAggregator._find_common_themes(all_dislikes, top_n=10)
        common_suggestions = ResultsAggregator._find_common_themes(all_suggestions, top_n=10)

        # Get unique questions and agents
        unique_questions = len(set(e.question_id for e in evaluations))
        unique_agents = len(set(e.agent_id for e in evaluations))

        return {
            "total_evaluations": len(evaluations),
            "unique_questions": unique_questions,
            "unique_agents": unique_agents,
            "rating_stats": rating_stats,
            "common_likes": common_likes,
            "common_dislikes": common_dislikes,
            "common_suggestions": common_suggestions,
            "total_likes": len(all_likes),
            "total_dislikes": len(all_dislikes),
            "total_suggestions": len(all_suggestions)
        }

    @staticmethod
    def aggregate_by_question(evaluations: List[Evaluation]) -> Dict[str, Dict[str, Any]]:
        """
        Aggregate results grouped by question.

        Args:
            evaluations: List of evaluations

        Returns:
            Dict mapping question_id to aggregated results
        """
        by_question = {}

        for eval in evaluations:
            if eval.question_id not in by_question:
                by_question[eval.question_id] = []
            by_question[eval.question_id].append(eval)

        results = {}
        for question_id, evals in by_question.items():
            results[question_id] = ResultsAggregator.aggregate_test_results(evals)
            results[question_id]["question_id"] = question_id

        return results

    @staticmethod
    def aggregate_by_agent(evaluations: List[Evaluation]) -> Dict[str, Dict[str, Any]]:
        """
        Aggregate results grouped by agent.

        Args:
            evaluations: List of evaluations

        Returns:
            Dict mapping agent_id to aggregated results
        """
        by_agent = {}

        for eval in evaluations:
            if eval.agent_id not in by_agent:
                by_agent[eval.agent_id] = []
            by_agent[eval.agent_id].append(eval)

        results = {}
        for agent_id, evals in by_agent.items():
            results[agent_id] = ResultsAggregator.aggregate_test_results(evals)
            results[agent_id]["agent_id"] = agent_id

        return results

    @staticmethod
    def _calculate_rating_stats(ratings: List[float]) -> Dict[str, float]:
        """
        Calculate statistics for ratings.

        Args:
            ratings: List of rating values

        Returns:
            Dict with rating statistics
        """
        if not ratings:
            return {
                "count": 0,
                "average": 0,
                "median": 0,
                "min": 0,
                "max": 0,
                "std_dev": 0
            }

        return {
            "count": len(ratings),
            "average": round(statistics.mean(ratings), 2),
            "median": round(statistics.median(ratings), 2),
            "min": min(ratings),
            "max": max(ratings),
            "std_dev": round(statistics.stdev(ratings), 2) if len(ratings) > 1 else 0
        }

    @staticmethod
    def _find_common_themes(items: List[str], top_n: int = 10) -> List[Tuple[str, int]]:
        """
        Find common themes in a list of strings.

        Args:
            items: List of strings
            top_n: Number of top themes to return

        Returns:
            List of (theme, count) tuples
        """
        if not items:
            return []

        # Count occurrences
        counter = Counter(items)

        # Get top N
        return counter.most_common(top_n)

    @staticmethod
    def compare_questions(
        evaluations: List[Evaluation],
        question_id_1: str,
        question_id_2: str
    ) -> Dict[str, Any]:
        """
        Compare results between two questions.

        Args:
            evaluations: List of all evaluations
            question_id_1: First question ID
            question_id_2: Second question ID

        Returns:
            Comparison dict
        """
        q1_evals = [e for e in evaluations if e.question_id == question_id_1]
        q2_evals = [e for e in evaluations if e.question_id == question_id_2]

        q1_stats = ResultsAggregator.aggregate_test_results(q1_evals)
        q2_stats = ResultsAggregator.aggregate_test_results(q2_evals)

        # Calculate differences
        avg_rating_diff = (
            q1_stats["rating_stats"]["average"] - q2_stats["rating_stats"]["average"]
        )

        return {
            "question_1": {
                "id": question_id_1,
                "stats": q1_stats
            },
            "question_2": {
                "id": question_id_2,
                "stats": q2_stats
            },
            "comparison": {
                "average_rating_difference": round(avg_rating_diff, 2),
                "better_rated": question_id_1 if avg_rating_diff > 0 else question_id_2
            }
        }

    @staticmethod
    def get_top_rated_responses(
        evaluations: List[Evaluation],
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get top rated responses.

        Args:
            evaluations: List of evaluations
            top_n: Number of top responses to return

        Returns:
            List of top rated response data
        """
        # Group by question to get average rating per response
        by_question = {}

        for eval in evaluations:
            if eval.question_id not in by_question:
                by_question[eval.question_id] = {
                    "ratings": [],
                    "response": eval.api_response,
                    "question_id": eval.question_id
                }

            if eval.rating is not None:
                by_question[eval.question_id]["ratings"].append(eval.rating)

        # Calculate average ratings
        scored = []
        for question_id, data in by_question.items():
            if data["ratings"]:
                avg_rating = statistics.mean(data["ratings"])
                scored.append({
                    "question_id": question_id,
                    "response": data["response"],
                    "average_rating": round(avg_rating, 2),
                    "num_ratings": len(data["ratings"])
                })

        # Sort by average rating
        scored.sort(key=lambda x: x["average_rating"], reverse=True)

        return scored[:top_n]

    @staticmethod
    def get_lowest_rated_responses(
        evaluations: List[Evaluation],
        bottom_n: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get lowest rated responses.

        Args:
            evaluations: List of evaluations
            bottom_n: Number of bottom responses to return

        Returns:
            List of lowest rated response data
        """
        top_rated = ResultsAggregator.get_top_rated_responses(
            evaluations,
            top_n=len(evaluations)
        )

        # Return bottom N
        return top_rated[-bottom_n:] if top_rated else []
