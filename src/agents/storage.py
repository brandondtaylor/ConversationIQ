"""
Agent storage utilities for exporting/importing agents as files.
"""
import json
import os
from pathlib import Path
from typing import List, Optional
import logging

from ..storage.schemas import Agent, AgentCreate

logger = logging.getLogger(__name__)


class AgentStorage:
    """Handles file-based storage of agents"""

    def __init__(self, storage_dir: str = "./data/agents"):
        """
        Initialize agent storage.

        Args:
            storage_dir: Directory for storing agent files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save_agent(self, agent: Agent) -> str:
        """
        Save agent to a JSON file.

        Args:
            agent: Agent to save

        Returns:
            Path to saved file
        """
        filename = f"{agent.id}.json"
        filepath = self.storage_dir / filename

        agent_dict = agent.model_dump(mode='json')

        with open(filepath, 'w') as f:
            json.dump(agent_dict, f, indent=2, default=str)

        logger.info(f"Saved agent to {filepath}")
        return str(filepath)

    def load_agent(self, agent_id: str) -> Optional[Agent]:
        """
        Load agent from a JSON file.

        Args:
            agent_id: Agent ID

        Returns:
            Agent or None if not found
        """
        filename = f"{agent_id}.json"
        filepath = self.storage_dir / filename

        if not filepath.exists():
            logger.warning(f"Agent file not found: {filepath}")
            return None

        try:
            with open(filepath, 'r') as f:
                agent_dict = json.load(f)

            agent = Agent(**agent_dict)
            logger.info(f"Loaded agent from {filepath}")
            return agent

        except Exception as e:
            logger.error(f"Failed to load agent from {filepath}: {e}")
            return None

    def list_stored_agents(self) -> List[str]:
        """
        List IDs of all stored agents.

        Returns:
            List of agent IDs
        """
        agent_files = self.storage_dir.glob("*.json")
        agent_ids = [f.stem for f in agent_files]
        return agent_ids

    def delete_agent_file(self, agent_id: str) -> bool:
        """
        Delete agent file.

        Args:
            agent_id: Agent ID

        Returns:
            True if deleted, False if not found
        """
        filename = f"{agent_id}.json"
        filepath = self.storage_dir / filename

        if filepath.exists():
            filepath.unlink()
            logger.info(f"Deleted agent file: {filepath}")
            return True

        logger.warning(f"Agent file not found: {filepath}")
        return False

    def export_agents(self, agents: List[Agent], output_file: str):
        """
        Export multiple agents to a single JSON file.

        Args:
            agents: List of agents to export
            output_file: Output file path
        """
        agents_data = [agent.model_dump(mode='json') for agent in agents]

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(agents_data, f, indent=2, default=str)

        logger.info(f"Exported {len(agents)} agents to {output_path}")

    def import_agents(self, input_file: str) -> List[AgentCreate]:
        """
        Import agents from a JSON file.

        Args:
            input_file: Input file path

        Returns:
            List of AgentCreate objects
        """
        input_path = Path(input_file)

        if not input_path.exists():
            raise FileNotFoundError(f"Import file not found: {input_path}")

        with open(input_path, 'r') as f:
            agents_data = json.load(f)

        agents = []
        for agent_data in agents_data:
            # Remove database fields if present
            for field in ['id', 'created_at', 'updated_at']:
                agent_data.pop(field, None)

            try:
                agent = AgentCreate(**agent_data)
                agents.append(agent)
            except Exception as e:
                logger.warning(f"Failed to import agent: {e}")
                continue

        logger.info(f"Imported {len(agents)} agents from {input_path}")
        return agents
