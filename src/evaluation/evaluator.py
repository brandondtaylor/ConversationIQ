"""
Main evaluator interface - combines aggregation and formatting.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from ..storage.database import get_db_manager
from ..storage.schemas import Evaluation
from ..agents.manager import AgentManager
from ..tests.config import TestConfigManager
from ..tests.executor import TestExecutor
from .aggregator import ResultsAggregator
from .formatter import ResultsFormatter


class EvaluationAnalyzer:
    """
    Main interface for analyzing test results.
    Combines aggregation and formatting capabilities.
    """

    def __init__(self, session: Optional[Session] = None):
        """
        Initialize evaluation analyzer.

        Args:
            session: SQLAlchemy session (optional)
        """
        self.session = session or get_db_manager().get_session()
        self.executor = TestExecutor(self.session)
        self.agent_manager = AgentManager(self.session)
        self.test_config_manager = TestConfigManager(self.session)

    def analyze_test(self, test_id: str) -> Dict[str, Any]:
        """
        Analyze all results for a test.

        Args:
            test_id: Test ID

        Returns:
            Dict with analysis results
        """
        # Get evaluations
        evaluations = self.executor.get_test_evaluations(test_id)

        if not evaluations:
            return {
                "error": "No evaluations found for this test",
                "test_id": test_id
            }

        # Aggregate results
        overall_results = ResultsAggregator.aggregate_test_results(evaluations)
        by_question = ResultsAggregator.aggregate_by_question(evaluations)
        by_agent = ResultsAggregator.aggregate_by_agent(evaluations)

        # Get top and bottom responses
        top_responses = ResultsAggregator.get_top_rated_responses(evaluations, top_n=5)
        bottom_responses = ResultsAggregator.get_lowest_rated_responses(evaluations, bottom_n=5)

        return {
            "test_id": test_id,
            "overall": overall_results,
            "by_question": by_question,
            "by_agent": by_agent,
            "top_responses": top_responses,
            "bottom_responses": bottom_responses,
            "evaluations": [e.model_dump() for e in evaluations]
        }

    def get_summary(self, test_id: str) -> str:
        """
        Get text summary of test results.

        Args:
            test_id: Test ID

        Returns:
            Formatted text summary
        """
        analysis = self.analyze_test(test_id)
        if "error" in analysis:
            return analysis["error"]

        return ResultsFormatter.format_summary_text(analysis["overall"])

    def export_results(
        self,
        test_id: str,
        output_format: str = "json",
        output_file: Optional[str] = None
    ) -> str:
        """
        Export test results to file.

        Args:
            test_id: Test ID
            output_format: Format (json, csv, txt, report)
            output_file: Output file path (optional, auto-generated if not provided)

        Returns:
            Path to exported file
        """
        # Get evaluations and analysis
        evaluations = self.executor.get_test_evaluations(test_id)
        analysis = self.analyze_test(test_id)

        # Generate output filename if not provided
        if not output_file:
            test_config = self.test_config_manager.get(test_id)
            test_name = test_config.name if test_config else test_id
            safe_name = "".join(c if c.isalnum() else "_" for c in test_name)
            output_file = f"./data/results/{safe_name}_results.{output_format}"

        # Export based on format
        if output_format == "json":
            ResultsFormatter.export_to_json(
                evaluations,
                analysis["overall"],
                output_file
            )
        elif output_format == "csv":
            ResultsFormatter.export_to_csv(evaluations, output_file)
        elif output_format == "txt":
            ResultsFormatter.export_summary_to_text(analysis["overall"], output_file)
        elif output_format == "report":
            # Get agents and questions for detailed report
            agents = {a.id: a for a in self.agent_manager.list()}
            questions_list = self.test_config_manager.get_questions(test_id)
            questions = {q.id: q for q in questions_list}

            ResultsFormatter.create_detailed_report(
                evaluations,
                agents,
                questions,
                analysis["overall"],
                output_file
            )
        else:
            raise ValueError(f"Unsupported format: {output_format}")

        return output_file

    def compare_agents(self, test_id: str, agent_id_1: str, agent_id_2: str) -> Dict[str, Any]:
        """
        Compare performance between two agents.

        Args:
            test_id: Test ID
            agent_id_1: First agent ID
            agent_id_2: Second agent ID

        Returns:
            Comparison results
        """
        evaluations = self.executor.get_test_evaluations(test_id)

        agent1_evals = [e for e in evaluations if e.agent_id == agent_id_1]
        agent2_evals = [e for e in evaluations if e.agent_id == agent_id_2]

        agent1_stats = ResultsAggregator.aggregate_test_results(agent1_evals)
        agent2_stats = ResultsAggregator.aggregate_test_results(agent2_evals)

        return {
            "agent_1": {
                "id": agent_id_1,
                "stats": agent1_stats
            },
            "agent_2": {
                "id": agent_id_2,
                "stats": agent2_stats
            },
            "comparison": {
                "avg_rating_diff": (
                    agent1_stats["rating_stats"]["average"] -
                    agent2_stats["rating_stats"]["average"]
                ),
                "more_critical": agent_id_1 if agent1_stats["rating_stats"]["average"] < agent2_stats["rating_stats"]["average"] else agent_id_2
            }
        }
