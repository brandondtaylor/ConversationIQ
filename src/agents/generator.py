"""
AI-powered agent generation based on task requirements.
"""
from typing import List, Dict, Any, Optional
import json
import logging

from ..storage.schemas import AgentCreate
from .personas import PersonaFactory

logger = logging.getLogger(__name__)


class AgentGenerator:
    """
    Generates agent personas based on task requirements.
    Can use AI or templates depending on availability.
    """

    def __init__(self, llm_client=None):
        """
        Initialize agent generator.

        Args:
            llm_client: Optional LLM client for AI-powered generation
        """
        self.llm_client = llm_client

    def generate_agents_for_task(
        self,
        task_description: str,
        target_demographics: Optional[List[str]] = None,
        num_agents: int = 3,
        diversity_focus: bool = True
    ) -> List[AgentCreate]:
        """
        Generate agents suitable for evaluating a specific task.

        Args:
            task_description: Description of the task/domain
            target_demographics: Target audience demographics
            num_agents: Number of agents to generate
            diversity_focus: Whether to prioritize diverse perspectives

        Returns:
            List of AgentCreate objects
        """
        if self.llm_client:
            return self._generate_with_llm(
                task_description,
                target_demographics,
                num_agents,
                diversity_focus
            )
        else:
            return self._generate_from_templates(
                task_description,
                target_demographics,
                num_agents
            )

    def _generate_with_llm(
        self,
        task_description: str,
        target_demographics: Optional[List[str]],
        num_agents: int,
        diversity_focus: bool
    ) -> List[AgentCreate]:
        """
        Generate agents using LLM.

        Args:
            task_description: Task description
            target_demographics: Target demographics
            num_agents: Number of agents
            diversity_focus: Prioritize diversity

        Returns:
            List of generated agents
        """
        prompt = self._build_generation_prompt(
            task_description,
            target_demographics,
            num_agents,
            diversity_focus
        )

        try:
            response = self.llm_client.send_message(prompt)
            response_text = self.llm_client.extract_response_text(response)

            # Parse JSON response
            agents_data = json.loads(response_text)

            # Convert to AgentCreate objects
            agents = []
            for agent_data in agents_data.get("agents", []):
                try:
                    agent = AgentCreate(**agent_data)
                    agents.append(agent)
                except Exception as e:
                    logger.warning(f"Failed to create agent from data: {e}")
                    continue

            return agents

        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            logger.info("Falling back to template-based generation")
            return self._generate_from_templates(
                task_description,
                target_demographics,
                num_agents
            )

    def _build_generation_prompt(
        self,
        task_description: str,
        target_demographics: Optional[List[str]],
        num_agents: int,
        diversity_focus: bool
    ) -> str:
        """Build prompt for LLM agent generation"""

        demographics_str = ""
        if target_demographics:
            demographics_str = f"\nTarget Demographics: {', '.join(target_demographics)}"

        diversity_str = ""
        if diversity_focus:
            diversity_str = "\nPrioritize creating diverse personas with different perspectives, backgrounds, and viewpoints."

        prompt = f"""Generate {num_agents} virtual agent personas for evaluating responses related to this task:

Task Description: {task_description}{demographics_str}{diversity_str}

For each agent, provide:
1. name: A descriptive name for the persona
2. description: Detailed background and perspective
3. demographics: Object with age, occupation, education, etc.
4. personality_traits: Array of personality characteristics
5. expertise_areas: Array of areas of expertise
6. evaluation_criteria_weights: Object with weights for different evaluation criteria (accuracy, clarity, helpfulness, etc.)

Return ONLY a JSON object with this structure:
{{
  "agents": [
    {{
      "name": "...",
      "description": "...",
      "demographics": {{}},
      "personality_traits": [],
      "expertise_areas": [],
      "evaluation_criteria_weights": {{}}
    }}
  ]
}}
"""

        return prompt

    def _generate_from_templates(
        self,
        task_description: str,
        target_demographics: Optional[List[str]],
        num_agents: int
    ) -> List[AgentCreate]:
        """
        Generate agents from predefined templates.

        Args:
            task_description: Task description
            target_demographics: Target demographics
            num_agents: Number of agents

        Returns:
            List of agents from templates
        """
        templates = PersonaFactory.create_default_personas()

        # Simple selection - take first num_agents templates
        # In a more sophisticated version, could match templates to task
        selected = templates[:min(num_agents, len(templates))]

        agents = []
        for template in selected:
            agent = AgentCreate(**template)
            agents.append(agent)

        return agents

    def customize_agent(
        self,
        base_agent: AgentCreate,
        customization: Dict[str, Any]
    ) -> AgentCreate:
        """
        Customize an existing agent with new attributes.

        Args:
            base_agent: Base agent to customize
            customization: Dict of attributes to override

        Returns:
            Customized agent
        """
        agent_dict = base_agent.model_dump()
        agent_dict.update(customization)
        return AgentCreate(**agent_dict)

    def generate_complementary_agents(
        self,
        existing_agents: List[AgentCreate],
        task_description: str,
        num_additional: int = 2
    ) -> List[AgentCreate]:
        """
        Generate additional agents that complement existing ones.

        Args:
            existing_agents: Already selected agents
            task_description: Task description
            num_additional: Number of additional agents to generate

        Returns:
            List of complementary agents
        """
        # Get all templates
        all_templates = PersonaFactory.create_default_personas()

        # Get existing expertise areas
        existing_expertise = set()
        for agent in existing_agents:
            existing_expertise.update(agent.expertise_areas)

        # Find templates with different expertise
        complementary = []
        for template in all_templates:
            template_expertise = set(template["expertise_areas"])
            # If this template has expertise not covered by existing agents
            if not template_expertise.issubset(existing_expertise):
                complementary.append(AgentCreate(**template))

                if len(complementary) >= num_additional:
                    break

        return complementary
