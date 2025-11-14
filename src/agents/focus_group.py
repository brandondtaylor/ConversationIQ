"""
Focus Group evaluation using TinyTroupe's TinyWorld.
Agents discuss responses together, providing collaborative feedback.
"""
from typing import Dict, Any, List, Optional
import logging
import re

try:
    from tinytroupe.environment import TinyWorld
    from tinytroupe.agent import TinyPerson
    TINYTROUPE_AVAILABLE = True
except ImportError:
    TINYTROUPE_AVAILABLE = False
    TinyWorld = None
    TinyPerson = None

from ..storage.schemas import Agent

logger = logging.getLogger(__name__)


class FocusGroupEvaluator:
    """
    Creates a focus group using TinyTroupe's TinyWorld where agents
    discuss and evaluate chat responses collaboratively.
    """

    def __init__(self, agents: List[Agent]):
        """
        Initialize focus group with agents.

        Args:
            agents: List of Agent objects to participate in the focus group
        """
        if not TINYTROUPE_AVAILABLE:
            raise ImportError(
                "TinyTroupe is not installed. "
                "Install from GitHub: pip install git+https://github.com/microsoft/tinytroupe.git"
            )

        self.agents = agents
        self.tiny_persons = self._create_tiny_persons()
        self.world = None

    def _create_tiny_persons(self) -> List[TinyPerson]:
        """
        Create TinyPerson instances from Agent configurations.

        Returns:
            List of TinyPerson instances
        """
        tiny_persons = []
        for agent in self.agents:
            try:
                tiny_person = TinyPerson(name=agent.name)

                # Define characteristics
                if agent.demographics:
                    if "age" in agent.demographics:
                        tiny_person.define("age", agent.demographics["age"])
                    if "occupation" in agent.demographics:
                        tiny_person.define("occupation", agent.demographics["occupation"])
                    if "education" in agent.demographics:
                        tiny_person.define("education", agent.demographics["education"])
                    if "nationality" in agent.demographics:
                        tiny_person.define("nationality", agent.demographics["nationality"])

                # Define personality
                if agent.personality_traits:
                    personality_str = ", ".join(agent.personality_traits)
                    tiny_person.define("personality", personality_str)

                # Define expertise
                if agent.expertise_areas:
                    expertise_str = ", ".join(agent.expertise_areas)
                    tiny_person.define("expertise", expertise_str)

                # Define background/description
                tiny_person.define("background", agent.description)

                tiny_persons.append(tiny_person)
                logger.info(f"Created TinyPerson for agent: {agent.name}")

            except Exception as e:
                logger.error(f"Failed to create TinyPerson for {agent.name}: {e}")
                continue

        return tiny_persons

    def evaluate_response(
        self,
        question: str,
        response: str,
        context: Optional[str] = None,
        num_rounds: int = 2
    ) -> Dict[str, Any]:
        """
        Run a focus group discussion to evaluate a chat response.

        Args:
            question: The original question
            response: The chat API response to evaluate
            context: Additional context about the task
            num_rounds: Number of discussion rounds

        Returns:
            Dict containing aggregated evaluation results from all agents
        """
        # Create the focus group world
        self.world = TinyWorld(
            "Evaluation Focus Group",
            self.tiny_persons
        )

        # Broadcast the context and task
        if context:
            self.world.broadcast(f"Context: {context}")

        self.world.broadcast(f"Question: {question}")
        self.world.broadcast(f"Response from chat AI: {response}")
        self.world.broadcast(
            "Please discuss and evaluate this response. Consider:\n"
            "1. What you LIKE about the response\n"
            "2. What you DISLIKE or find problematic\n"
            "3. Your SUGGESTIONS for improvement\n"
            "4. Rate it from 1-10\n"
            "Share your perspective based on your background and expertise."
        )

        # Run the focus group discussion
        try:
            self.world.run(num_rounds)
        except Exception as e:
            logger.error(f"Focus group discussion failed: {e}")
            return self._create_fallback_evaluation(question, response)

        # Extract and aggregate evaluations
        evaluations = self._extract_evaluations_from_world()

        return evaluations

    def _extract_evaluations_from_world(self) -> Dict[str, Any]:
        """
        Extract evaluations from the focus group conversation.

        Returns:
            Dict with aggregated evaluations
        """
        all_likes = []
        all_dislikes = []
        all_suggestions = []
        ratings = []
        individual_perspectives = []

        # Get conversation history from each agent
        for tiny_person in self.tiny_persons:
            try:
                # Get the agent's thoughts and statements
                agent_evaluation = self._parse_agent_conversation(tiny_person)

                all_likes.extend(agent_evaluation["likes"])
                all_dislikes.extend(agent_evaluation["dislikes"])
                all_suggestions.extend(agent_evaluation["suggestions"])

                if agent_evaluation["rating"]:
                    ratings.append(agent_evaluation["rating"])

                individual_perspectives.append({
                    "agent_name": tiny_person.name,
                    "perspective": agent_evaluation["full_text"]
                })

            except Exception as e:
                logger.warning(f"Failed to extract evaluation from {tiny_person.name}: {e}")
                continue

        # Extract full conversation transcript
        conversation_transcript = self._extract_conversation_transcript()

        # Calculate average rating
        avg_rating = sum(ratings) / len(ratings) if ratings else None

        return {
            "likes": all_likes,
            "dislikes": all_dislikes,
            "suggestions": all_suggestions,
            "rating": avg_rating,
            "agent_perspective": f"Focus group consensus from {len(self.tiny_persons)} agents",
            "raw_evaluation": {
                "method": "focus_group_tinytroupe",
                "num_agents": len(self.tiny_persons),
                "individual_perspectives": individual_perspectives,
                "conversation_transcript": conversation_transcript,
                "conversation_rounds": len(self.world.actions if hasattr(self.world, 'actions') else [])
            }
        }

    def _extract_conversation_transcript(self) -> List[Dict[str, str]]:
        """
        Extract the full conversation transcript from the TinyWorld.

        Returns:
            List of conversation turns with speaker and message
        """
        transcript = []

        try:
            # Try to get actions from the world
            if hasattr(self.world, 'actions') and self.world.actions:
                for action in self.world.actions:
                    if hasattr(action, 'agent') and hasattr(action, 'content'):
                        transcript.append({
                            "speaker": action.agent.name if hasattr(action.agent, 'name') else str(action.agent),
                            "message": str(action.content),
                            "type": "action"
                        })
                    else:
                        transcript.append({
                            "speaker": "system",
                            "message": str(action),
                            "type": "action"
                        })

            # Also get individual agent memories if available
            for tiny_person in self.tiny_persons:
                if hasattr(tiny_person, 'episodic_memory') and hasattr(tiny_person.episodic_memory, 'retrieve_all'):
                    memories = tiny_person.episodic_memory.retrieve_all()
                    for memory in memories[-5:]:  # Last 5 memories per agent
                        transcript.append({
                            "speaker": tiny_person.name,
                            "message": str(memory),
                            "type": "memory"
                        })

        except Exception as e:
            logger.warning(f"Failed to extract conversation transcript: {e}")
            transcript.append({
                "speaker": "system",
                "message": f"Failed to extract transcript: {e}",
                "type": "error"
            })

        return transcript

    def _parse_agent_conversation(self, tiny_person: TinyPerson) -> Dict[str, Any]:
        """
        Parse an individual agent's conversation to extract structured feedback.

        Args:
            tiny_person: TinyPerson instance

        Returns:
            Dict with parsed evaluation
        """
        # Get agent's recent actions/statements
        conversation_text = ""
        if hasattr(tiny_person, 'episodic_memory') and hasattr(tiny_person.episodic_memory, 'retrieve_all'):
            memories = tiny_person.episodic_memory.retrieve_all()
            conversation_text = " ".join([str(m) for m in memories])
        elif hasattr(tiny_person, '_actions'):
            conversation_text = " ".join([str(a) for a in tiny_person._actions])

        likes = []
        dislikes = []
        suggestions = []
        rating = None

        # Simple parsing - look for keywords
        lines = conversation_text.split('.')

        for line in lines:
            line_lower = line.lower().strip()

            # Extract ratings
            rating_match = re.search(r'\b([1-9]|10)\s*(?:/\s*10|out of 10)\b', line_lower)
            if rating_match and not rating:
                rating = float(rating_match.group(1))

            # Extract sentiment
            if any(word in line_lower for word in ['like', 'good', 'excellent', 'appreciate', 'well done']):
                if line.strip():
                    likes.append(line.strip())

            if any(word in line_lower for word in ['dislike', 'problem', 'issue', 'concern', 'lacking', 'missing']):
                if line.strip():
                    dislikes.append(line.strip())

            if any(word in line_lower for word in ['suggest', 'recommend', 'should', 'could improve', 'better if']):
                if line.strip():
                    suggestions.append(line.strip())

        return {
            "likes": likes[:3],  # Limit to top 3
            "dislikes": dislikes[:3],
            "suggestions": suggestions[:3],
            "rating": rating,
            "full_text": conversation_text
        }

    def _create_fallback_evaluation(self, question: str, response: str) -> Dict[str, Any]:
        """
        Create a fallback evaluation if focus group fails.

        Args:
            question: Question text
            response: Response text

        Returns:
            Basic evaluation dict
        """
        return {
            "likes": ["Response provided"],
            "dislikes": ["Focus group evaluation failed"],
            "suggestions": ["Unable to get group feedback"],
            "rating": 5.0,
            "agent_perspective": "Fallback evaluation - focus group failed",
            "raw_evaluation": {
                "method": "fallback",
                "error": "Focus group evaluation failed"
            }
        }
