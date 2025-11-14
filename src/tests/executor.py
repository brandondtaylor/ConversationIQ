"""
Test execution engine - orchestrates the evaluation process.
"""
from typing import List, Dict, Any, Optional, Callable
import logging
from datetime import datetime

from sqlalchemy.orm import Session

from ..storage.database import EvaluationModel, get_db_manager
from ..storage.schemas import Evaluation, EvaluationCreate, TestStatus, Question, EvaluationMode
from ..api.config import APIConfigManager
from ..api.client import ChatAPIClient
from ..agents.manager import AgentManager
from ..agents.personas import TinyTroupePersona, TINYTROUPE_AVAILABLE
from ..agents.focus_group import FocusGroupEvaluator
from .config import TestConfigManager
from .context import TaskContext

logger = logging.getLogger(__name__)


class TestExecutionError(Exception):
    """Exception raised during test execution"""
    pass


class TestExecutor:
    """
    Orchestrates the test execution process:
    1. Load test configuration
    2. For each question, send to chat API
    3. Have each agent evaluate the response
    4. Store evaluations
    """

    def __init__(self, session: Optional[Session] = None):
        """
        Initialize test executor.

        Args:
            session: SQLAlchemy session (optional)
        """
        self.session = session or get_db_manager().get_session()
        self.test_config_manager = TestConfigManager(self.session)
        self.api_config_manager = APIConfigManager(self.session)
        self.agent_manager = AgentManager(self.session)

    def run_test(
        self,
        test_id: str,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """
        Run a complete test.

        Args:
            test_id: Test configuration ID
            progress_callback: Optional callback for progress updates

        Returns:
            Dict with execution summary

        Raises:
            TestExecutionError: If test execution fails
        """
        # Load test configuration
        test_config = self.test_config_manager.get(test_id)
        if not test_config:
            raise TestExecutionError(f"Test configuration not found: {test_id}")

        self._log_progress(progress_callback, f"Starting test: {test_config.name}")

        # Update status to running
        self.test_config_manager.update_status(test_id, TestStatus.RUNNING)

        try:
            # Load API client
            api_client = self.api_config_manager.create_client(test_config.api_config_id)
            if not api_client:
                raise TestExecutionError("Failed to create API client")

            # Load agents
            agents = self.agent_manager.get_multiple(test_config.agent_ids)
            if not agents:
                raise TestExecutionError("No agents found")

            self._log_progress(
                progress_callback,
                f"Loaded {len(agents)} agents for evaluation"
            )

            # Determine evaluation mode
            evaluation_mode = test_config.evaluation_mode
            self._log_progress(
                progress_callback,
                f"Using evaluation mode: {evaluation_mode.value}"
            )

            # Load questions
            questions = self.test_config_manager.get_questions(test_id)
            if not questions:
                raise TestExecutionError("No questions found")

            self._log_progress(
                progress_callback,
                f"Processing {len(questions)} questions"
            )

            # Create task context
            task_context = TaskContext(task_description=test_config.task_context)

            # Execute test for each question
            total_evaluations = 0
            for idx, question in enumerate(questions):
                self._log_progress(
                    progress_callback,
                    f"Question {idx + 1}/{len(questions)}: {question.text[:50]}..."
                )

                try:
                    # Send question to API
                    response = api_client.send_message(
                        question.text,
                        context=test_config.task_context
                    )
                    response_text = api_client.extract_response_text(response)

                    # Evaluate based on selected mode
                    if evaluation_mode == EvaluationMode.SINGLE_AGENT:
                        # Single-agent evaluation (original behavior)
                        total_evaluations += self._run_single_agent_evaluation(
                            test_id=test_id,
                            question=question,
                            response_text=response_text,
                            agents=agents,
                            task_context=task_context
                        )

                    elif evaluation_mode == EvaluationMode.FOCUS_GROUP:
                        # Focus group evaluation
                        total_evaluations += self._run_focus_group_evaluation(
                            test_id=test_id,
                            question=question,
                            response_text=response_text,
                            agents=agents,
                            task_context=task_context
                        )

                    elif evaluation_mode == EvaluationMode.BOTH:
                        # Run both single-agent and focus group
                        total_evaluations += self._run_single_agent_evaluation(
                            test_id=test_id,
                            question=question,
                            response_text=response_text,
                            agents=agents,
                            task_context=task_context
                        )
                        total_evaluations += self._run_focus_group_evaluation(
                            test_id=test_id,
                            question=question,
                            response_text=response_text,
                            agents=agents,
                            task_context=task_context
                        )

                except Exception as e:
                    logger.error(f"Failed to process question {question.id}: {e}")
                    continue

            # Update status to completed
            self.test_config_manager.update_status(test_id, TestStatus.COMPLETED)

            self._log_progress(
                progress_callback,
                f"Test completed! {total_evaluations} evaluations generated."
            )

            return {
                "test_id": test_id,
                "status": "completed",
                "questions_processed": len(questions),
                "total_evaluations": total_evaluations,
                "agents": len(agents),
                "completed_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            self.test_config_manager.update_status(test_id, TestStatus.FAILED)
            raise TestExecutionError(f"Test execution failed: {e}") from e

    def _run_single_agent_evaluation(
        self,
        test_id: str,
        question: Question,
        response_text: str,
        agents: List[Any],
        task_context: TaskContext
    ) -> int:
        """
        Run single-agent evaluation mode (each agent evaluates independently).

        Args:
            test_id: Test ID
            question: Question object
            response_text: API response text
            agents: List of agents
            task_context: Task context

        Returns:
            Number of evaluations created
        """
        evaluations_count = 0

        # Create personas for each agent
        personas = []
        for agent in agents:
            if TINYTROUPE_AVAILABLE:
                try:
                    persona = TinyTroupePersona(agent)
                    personas.append((agent, persona))
                except Exception as e:
                    logger.warning(f"Failed to create persona for {agent.name}: {e}")
                    personas.append((agent, None))
            else:
                personas.append((agent, None))

        # Have each agent evaluate independently
        for agent, persona in personas:
            try:
                evaluation = self._evaluate_response(
                    test_id=test_id,
                    question=question,
                    response_text=response_text,
                    agent=agent,
                    persona=persona,
                    task_context=task_context
                )

                self._store_evaluation(evaluation)
                evaluations_count += 1

            except Exception as e:
                logger.error(
                    f"Single-agent evaluation failed for {agent.name}, "
                    f"question {question.id}: {e}"
                )
                continue

        return evaluations_count

    def _run_focus_group_evaluation(
        self,
        test_id: str,
        question: Question,
        response_text: str,
        agents: List[Any],
        task_context: TaskContext
    ) -> int:
        """
        Run focus group evaluation mode (agents discuss together).

        Args:
            test_id: Test ID
            question: Question object
            response_text: API response text
            agents: List of agents
            task_context: Task context

        Returns:
            Number of evaluations created (1 for focus group)
        """
        try:
            # Create focus group evaluator
            focus_group = FocusGroupEvaluator(agents)

            # Run group discussion
            group_evaluation = focus_group.evaluate_response(
                question=question.text,
                response=response_text,
                context=task_context.to_text(),
                num_rounds=2
            )

            # Create evaluation record for the focus group
            # Use first agent's ID as representative, or create special "focus_group" ID
            evaluation = EvaluationCreate(
                test_id=test_id,
                question_id=question.id,
                agent_id="focus_group",  # Special identifier for focus group evaluations
                api_response=response_text,
                likes=group_evaluation.get("likes", []),
                dislikes=group_evaluation.get("dislikes", []),
                suggestions=group_evaluation.get("suggestions", []),
                rating=group_evaluation.get("rating"),
                agent_perspective=group_evaluation.get("agent_perspective", "Focus group consensus"),
                raw_evaluation=group_evaluation.get("raw_evaluation", {})
            )

            self._store_evaluation(evaluation)
            return 1

        except Exception as e:
            logger.error(f"Focus group evaluation failed for question {question.id}: {e}")
            return 0

    def _evaluate_response(
        self,
        test_id: str,
        question: Question,
        response_text: str,
        agent: Any,
        persona: Optional[TinyTroupePersona],
        task_context: TaskContext
    ) -> EvaluationCreate:
        """
        Evaluate a response using an agent/persona.

        Args:
            test_id: Test ID
            question: Question object
            response_text: API response text
            agent: Agent object
            persona: TinyTroupe persona (optional)
            task_context: Task context

        Returns:
            EvaluationCreate object
        """
        if persona and TINYTROUPE_AVAILABLE:
            # Use TinyTroupe persona for sophisticated evaluation
            evaluation_data = persona.evaluate_response(
                question=question.text,
                response=response_text,
                context=task_context.to_text()
            )
        else:
            # Use simple rule-based evaluation
            evaluation_data = self._simple_evaluation(
                question.text,
                response_text,
                agent
            )

        # Create evaluation record
        evaluation = EvaluationCreate(
            test_id=test_id,
            question_id=question.id,
            agent_id=agent.id,
            api_response=response_text,
            likes=evaluation_data.get("likes", []),
            dislikes=evaluation_data.get("dislikes", []),
            suggestions=evaluation_data.get("suggestions", []),
            rating=evaluation_data.get("rating"),
            agent_perspective=evaluation_data.get("agent_perspective"),
            raw_evaluation=evaluation_data.get("raw_evaluation", {})
        )

        return evaluation

    def _simple_evaluation(
        self,
        question: str,
        response: str,
        agent: Any
    ) -> Dict[str, Any]:
        """
        Simple rule-based evaluation when TinyTroupe is not available.

        Args:
            question: Question text
            response: Response text
            agent: Agent object

        Returns:
            Evaluation data dict
        """
        likes = []
        dislikes = []
        suggestions = []
        rating = 5.0  # Default neutral rating

        # Simple length check
        if len(response) < 50:
            dislikes.append("Response is very short")
            rating -= 1
        elif len(response) > 50:
            likes.append("Response provides substantial information")

        # Check if response addresses the question (simple keyword matching)
        question_words = set(question.lower().split())
        response_words = set(response.lower().split())
        overlap = len(question_words.intersection(response_words))

        if overlap > 2:
            likes.append("Response appears to address the question")
            rating += 0.5
        else:
            dislikes.append("Response may not fully address the question")
            rating -= 1

        # Suggest improvements
        if len(response) < 100:
            suggestions.append("Consider providing more detailed information")

        return {
            "likes": likes,
            "dislikes": dislikes,
            "suggestions": suggestions,
            "rating": max(1, min(10, rating)),
            "agent_perspective": f"Evaluation by {agent.name} (simple analysis)",
            "raw_evaluation": {
                "method": "simple_rule_based",
                "response_length": len(response),
                "question_words": len(question_words),
                "response_words": len(response_words),
                "word_overlap": overlap
            }
        }

    def _store_evaluation(self, evaluation: EvaluationCreate):
        """
        Store evaluation in database.

        Args:
            evaluation: Evaluation to store
        """
        db_evaluation = EvaluationModel(
            test_id=evaluation.test_id,
            question_id=evaluation.question_id,
            agent_id=evaluation.agent_id,
            api_response=evaluation.api_response,
            likes=evaluation.likes,
            dislikes=evaluation.dislikes,
            suggestions=evaluation.suggestions,
            rating=evaluation.rating,
            agent_perspective=evaluation.agent_perspective,
            raw_evaluation=evaluation.raw_evaluation
        )

        self.session.add(db_evaluation)
        self.session.commit()

    def _log_progress(
        self,
        callback: Optional[Callable[[str], None]],
        message: str
    ):
        """
        Log progress message.

        Args:
            callback: Progress callback
            message: Progress message
        """
        logger.info(message)
        if callback:
            callback(message)

    def get_test_evaluations(self, test_id: str) -> List[Evaluation]:
        """
        Get all evaluations for a test.

        Args:
            test_id: Test ID

        Returns:
            List of evaluations
        """
        db_evaluations = self.session.query(EvaluationModel).filter(
            EvaluationModel.test_id == test_id
        ).all()

        return [Evaluation.model_validate(e) for e in db_evaluations]
