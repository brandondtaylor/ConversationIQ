"""
Result formatting and export utilities.
"""
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

import pandas as pd

from ..storage.schemas import Evaluation, Agent, Question


class ResultsFormatter:
    """Formats evaluation results for display and export"""

    @staticmethod
    def format_summary_text(aggregated_results: Dict[str, Any]) -> str:
        """
        Format aggregated results as readable text.

        Args:
            aggregated_results: Aggregated results dict

        Returns:
            Formatted text summary
        """
        lines = []
        lines.append("=" * 60)
        lines.append("TEST RESULTS SUMMARY")
        lines.append("=" * 60)
        lines.append("")

        # Overview
        lines.append("Overview:")
        lines.append(f"  Total Evaluations: {aggregated_results.get('total_evaluations', 0)}")
        lines.append(f"  Questions Evaluated: {aggregated_results.get('unique_questions', 0)}")
        lines.append(f"  Agents Used: {aggregated_results.get('unique_agents', 0)}")
        lines.append("")

        # Ratings
        rating_stats = aggregated_results.get("rating_stats", {})
        if rating_stats.get("count", 0) > 0:
            lines.append("Rating Statistics:")
            lines.append(f"  Average Rating: {rating_stats.get('average', 0)}/10")
            lines.append(f"  Median Rating: {rating_stats.get('median', 0)}/10")
            lines.append(f"  Range: {rating_stats.get('min', 0)} - {rating_stats.get('max', 0)}")
            lines.append(f"  Std Deviation: {rating_stats.get('std_dev', 0)}")
            lines.append("")

        # Common Likes
        common_likes = aggregated_results.get("common_likes", [])
        if common_likes:
            lines.append("Most Common Positive Feedback:")
            for theme, count in common_likes[:5]:
                lines.append(f"  • {theme} ({count}x)")
            lines.append("")

        # Common Dislikes
        common_dislikes = aggregated_results.get("common_dislikes", [])
        if common_dislikes:
            lines.append("Most Common Concerns:")
            for theme, count in common_dislikes[:5]:
                lines.append(f"  • {theme} ({count}x)")
            lines.append("")

        # Suggestions
        common_suggestions = aggregated_results.get("common_suggestions", [])
        if common_suggestions:
            lines.append("Top Improvement Suggestions:")
            for theme, count in common_suggestions[:5]:
                lines.append(f"  • {theme} ({count}x)")
            lines.append("")

        lines.append("=" * 60)

        return "\n".join(lines)

    @staticmethod
    def format_evaluation_text(
        evaluation: Evaluation,
        agent: Agent,
        question: Question
    ) -> str:
        """
        Format a single evaluation as readable text.

        Args:
            evaluation: Evaluation object
            agent: Agent who performed evaluation
            question: Question that was evaluated

        Returns:
            Formatted evaluation text
        """
        lines = []
        lines.append("-" * 60)
        lines.append(f"Agent: {agent.name}")
        lines.append(f"Question: {question.text}")
        lines.append("")

        lines.append("API Response:")
        lines.append(f"  {evaluation.api_response}")
        lines.append("")

        if evaluation.rating is not None:
            lines.append(f"Rating: {evaluation.rating}/10")
            lines.append("")

        if evaluation.likes:
            lines.append("Likes:")
            for like in evaluation.likes:
                lines.append(f"  ✓ {like}")
            lines.append("")

        if evaluation.dislikes:
            lines.append("Dislikes:")
            for dislike in evaluation.dislikes:
                lines.append(f"  ✗ {dislike}")
            lines.append("")

        if evaluation.suggestions:
            lines.append("Suggestions:")
            for suggestion in evaluation.suggestions:
                lines.append(f"  → {suggestion}")
            lines.append("")

        if evaluation.agent_perspective:
            lines.append("Agent Perspective:")
            lines.append(f"  {evaluation.agent_perspective}")
            lines.append("")

        lines.append("-" * 60)

        return "\n".join(lines)

    @staticmethod
    def export_to_json(
        evaluations: List[Evaluation],
        aggregated_results: Dict[str, Any],
        output_file: str
    ):
        """
        Export results to JSON file.

        Args:
            evaluations: List of evaluations
            aggregated_results: Aggregated results
            output_file: Output file path
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "generated_at": datetime.utcnow().isoformat(),
            "summary": aggregated_results,
            "evaluations": [e.model_dump(mode='json') for e in evaluations]
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)

    @staticmethod
    def export_to_csv(
        evaluations: List[Evaluation],
        output_file: str
    ):
        """
        Export evaluations to CSV file.

        Args:
            evaluations: List of evaluations
            output_file: Output file path
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to list of dicts
        rows = []
        for eval in evaluations:
            row = {
                "test_id": eval.test_id,
                "question_id": eval.question_id,
                "agent_id": eval.agent_id,
                "api_response": eval.api_response[:200] + "..." if len(eval.api_response) > 200 else eval.api_response,
                "rating": eval.rating,
                "num_likes": len(eval.likes),
                "num_dislikes": len(eval.dislikes),
                "num_suggestions": len(eval.suggestions),
                "likes": "; ".join(eval.likes),
                "dislikes": "; ".join(eval.dislikes),
                "suggestions": "; ".join(eval.suggestions),
                "timestamp": eval.timestamp
            }
            rows.append(row)

        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False)

    @staticmethod
    def export_summary_to_text(
        aggregated_results: Dict[str, Any],
        output_file: str
    ):
        """
        Export summary to text file.

        Args:
            aggregated_results: Aggregated results
            output_file: Output file path
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        summary_text = ResultsFormatter.format_summary_text(aggregated_results)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"Generated: {datetime.utcnow().isoformat()}\n\n")
            f.write(summary_text)

    @staticmethod
    def create_detailed_report(
        evaluations: List[Evaluation],
        agents: Dict[str, Agent],
        questions: Dict[str, Question],
        aggregated_results: Dict[str, Any],
        output_file: str
    ):
        """
        Create a detailed text report with all evaluations.

        Args:
            evaluations: List of evaluations
            agents: Dict mapping agent_id to Agent
            questions: Dict mapping question_id to Question
            aggregated_results: Aggregated results
            output_file: Output file path
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            # Header
            f.write("CONVERSATIONIQ - DETAILED TEST REPORT\n")
            f.write(f"Generated: {datetime.utcnow().isoformat()}\n")
            f.write("\n")

            # Summary
            f.write(ResultsFormatter.format_summary_text(aggregated_results))
            f.write("\n\n")

            # Detailed Evaluations
            f.write("=" * 60)
            f.write("\nDETAILED EVALUATIONS\n")
            f.write("=" * 60)
            f.write("\n\n")

            for eval in evaluations:
                agent = agents.get(eval.agent_id)
                question = questions.get(eval.question_id)

                if agent and question:
                    eval_text = ResultsFormatter.format_evaluation_text(
                        eval, agent, question
                    )
                    f.write(eval_text)
                    f.write("\n")
