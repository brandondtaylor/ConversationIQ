"""
TinyTroupe persona integration for agent evaluation.
"""
from typing import Dict, Any, List, Optional
import logging

try:
    from tinytroupe.agent import TinyPerson
    TINYTROUPE_AVAILABLE = True
except ImportError:
    TINYTROUPE_AVAILABLE = False
    TinyPerson = None

from ..storage.schemas import Agent

logger = logging.getLogger(__name__)


class TinyTroupePersona:
    """
    Wrapper for TinyTroupe TinyPerson that integrates with our Agent system.
    """

    def __init__(self, agent: Agent):
        """
        Initialize TinyTroupe persona from an Agent.

        Args:
            agent: Agent configuration
        """
        if not TINYTROUPE_AVAILABLE:
            raise ImportError(
                "TinyTroupe is not installed. "
                "Please install it with: pip install tinytroupe"
            )

        self.agent = agent
        self.tiny_person = self._create_tiny_person()

    def _create_tiny_person(self) -> TinyPerson:
        """
        Create a TinyPerson from agent configuration.

        Returns:
            Configured TinyPerson instance
        """
        # Extract demographic info
        name = self.agent.name
        age = self.agent.demographics.get("age")
        nationality = self.agent.demographics.get("nationality", "American")
        occupation = self.agent.demographics.get("occupation", "Professional")

        # Build personality description
        personality_desc = self._build_personality_description()

        # Create TinyPerson
        tiny_person = TinyPerson(name=name)

        # Define the person's characteristics
        tiny_person.define("age", age if age else 35)
        tiny_person.define("nationality", nationality)
        tiny_person.define("occupation", occupation)
        tiny_person.define("personality", personality_desc)

        # Add expertise areas
        if self.agent.expertise_areas:
            expertise_str = ", ".join(self.agent.expertise_areas)
            tiny_person.define("expertise", expertise_str)

        # Add custom background
        tiny_person.define("background", self.agent.description)

        return tiny_person

    def _build_personality_description(self) -> str:
        """
        Build a personality description from traits.

        Returns:
            Personality description string
        """
        if not self.agent.personality_traits:
            return "Thoughtful and analytical"

        return ", ".join(self.agent.personality_traits)

    def evaluate_response(
        self,
        question: str,
        response: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Have the persona evaluate a chat response.

        Args:
            question: The original question
            response: The chat API response to evaluate
            context: Additional context about the task

        Returns:
            Dict containing evaluation results
        """
        # Build the evaluation prompt
        evaluation_prompt = self._build_evaluation_prompt(question, response, context)

        # Get persona's thoughts
        self.tiny_person.listen(evaluation_prompt)
        evaluation_text = self.tiny_person.act()

        # Parse the evaluation
        evaluation = self._parse_evaluation(evaluation_text)

        return evaluation

    def _build_evaluation_prompt(
        self,
        question: str,
        response: str,
        context: Optional[str]
    ) -> str:
        """
        Build the evaluation prompt for the persona.

        Args:
            question: Original question
            response: API response
            context: Task context

        Returns:
            Evaluation prompt
        """
        prompt_parts = []

        if context:
            prompt_parts.append(f"Context: {context}\n")

        prompt_parts.append(f"Question: {question}\n")
        prompt_parts.append(f"Response: {response}\n")

        prompt_parts.append(
            "\nPlease evaluate this response from your perspective. Consider:\n"
            "1. What do you LIKE about this response?\n"
            "2. What do you DISLIKE or find problematic?\n"
            "3. What SUGGESTIONS do you have for improvement?\n"
            "4. Overall, rate this response on a scale of 1-10.\n"
            "\nProvide your evaluation considering your background, expertise, and values."
        )

        return "".join(prompt_parts)

    def _parse_evaluation(self, evaluation_text: str) -> Dict[str, Any]:
        """
        Parse evaluation text into structured format.

        Args:
            evaluation_text: Raw evaluation text from persona

        Returns:
            Structured evaluation dict
        """
        # Simple parsing - look for keywords
        # In a more sophisticated version, could use NLP or structured prompts

        likes = []
        dislikes = []
        suggestions = []
        rating = None

        lines = evaluation_text.split('\n')
        current_section = None

        for line in lines:
            line_lower = line.lower().strip()

            # Detect sections
            if 'like' in line_lower and not line_lower.startswith('-'):
                current_section = 'likes'
                continue
            elif 'dislike' in line_lower and not line_lower.startswith('-'):
                current_section = 'dislikes'
                continue
            elif 'suggest' in line_lower and not line_lower.startswith('-'):
                current_section = 'suggestions'
                continue
            elif 'rate' in line_lower or 'rating' in line_lower:
                current_section = 'rating'
                # Try to extract number
                import re
                numbers = re.findall(r'\b([1-9]|10)\b', line)
                if numbers:
                    rating = float(numbers[0])
                continue

            # Add content to current section
            if line.strip() and current_section:
                cleaned_line = line.strip().lstrip('-•*').strip()
                if cleaned_line:
                    if current_section == 'likes':
                        likes.append(cleaned_line)
                    elif current_section == 'dislikes':
                        dislikes.append(cleaned_line)
                    elif current_section == 'suggestions':
                        suggestions.append(cleaned_line)

        return {
            "likes": likes,
            "dislikes": dislikes,
            "suggestions": suggestions,
            "rating": rating,
            "agent_perspective": evaluation_text,
            "raw_evaluation": {
                "full_text": evaluation_text
            }
        }


class PersonaFactory:
    """Factory for creating standard persona templates"""

    @staticmethod
    def create_default_personas() -> List[Dict[str, Any]]:
        """
        Create a set of default persona templates.

        Returns:
            List of persona configuration dicts
        """
        return [
            {
                "name": "Tech-Savvy Professional",
                "description": "A technology professional who values efficiency, accuracy, and technical depth",
                "demographics": {
                    "age": 32,
                    "occupation": "Software Engineer",
                    "education": "Bachelor's in Computer Science"
                },
                "personality_traits": [
                    "Analytical",
                    "Detail-oriented",
                    "Direct",
                    "Efficiency-focused"
                ],
                "expertise_areas": ["Technology", "Programming", "Problem-solving"],
                "evaluation_criteria_weights": {
                    "accuracy": 0.3,
                    "clarity": 0.25,
                    "completeness": 0.25,
                    "efficiency": 0.2
                }
            },
            {
                "name": "Non-Technical User",
                "description": "A general user who needs clear, simple explanations without jargon",
                "demographics": {
                    "age": 45,
                    "occupation": "Marketing Manager",
                    "education": "Bachelor's in Business"
                },
                "personality_traits": [
                    "Practical",
                    "Appreciates simplicity",
                    "Patient",
                    "Results-oriented"
                ],
                "expertise_areas": ["Business", "Marketing", "Communication"],
                "evaluation_criteria_weights": {
                    "clarity": 0.35,
                    "simplicity": 0.3,
                    "helpfulness": 0.25,
                    "friendliness": 0.1
                }
            },
            {
                "name": "Skeptical Customer",
                "description": "A cautious customer who questions claims and looks for red flags",
                "demographics": {
                    "age": 38,
                    "occupation": "Accountant",
                    "education": "Master's in Accounting"
                },
                "personality_traits": [
                    "Skeptical",
                    "Detail-oriented",
                    "Risk-averse",
                    "Thorough"
                ],
                "expertise_areas": ["Finance", "Analysis", "Risk Assessment"],
                "evaluation_criteria_weights": {
                    "trustworthiness": 0.3,
                    "accuracy": 0.3,
                    "transparency": 0.25,
                    "completeness": 0.15
                }
            },
            {
                "name": "Creative Enthusiast",
                "description": "A creative person who values engaging, inspirational communication",
                "demographics": {
                    "age": 28,
                    "occupation": "Graphic Designer",
                    "education": "Bachelor's in Fine Arts"
                },
                "personality_traits": [
                    "Creative",
                    "Enthusiastic",
                    "Open-minded",
                    "Emotionally aware"
                ],
                "expertise_areas": ["Design", "Arts", "Communication"],
                "evaluation_criteria_weights": {
                    "engagement": 0.3,
                    "tone": 0.25,
                    "creativity": 0.25,
                    "clarity": 0.2
                }
            },
            {
                "name": "Accessibility-Focused User",
                "description": "A user who needs accessible, inclusive communication",
                "demographics": {
                    "age": 52,
                    "occupation": "Teacher",
                    "education": "Master's in Education"
                },
                "personality_traits": [
                    "Patient",
                    "Inclusive",
                    "Empathetic",
                    "Thorough"
                ],
                "expertise_areas": ["Education", "Accessibility", "Communication"],
                "evaluation_criteria_weights": {
                    "inclusivity": 0.3,
                    "clarity": 0.3,
                    "simplicity": 0.25,
                    "helpfulness": 0.15
                }
            }
        ]
