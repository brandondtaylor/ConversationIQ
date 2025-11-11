"""
Agent management - CRUD operations for virtual agents.
"""
from typing import Optional, List
from sqlalchemy.orm import Session

from ..storage.database import AgentModel, get_db_manager
from ..storage.schemas import Agent, AgentCreate, AgentUpdate


class AgentManager:
    """Manages virtual agents in the database"""

    def __init__(self, session: Optional[Session] = None):
        """
        Initialize agent manager.

        Args:
            session: SQLAlchemy session (optional, will create if not provided)
        """
        self.session = session
        self._owns_session = session is None

        if self._owns_session:
            db_manager = get_db_manager()
            self.session = db_manager.get_session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._owns_session and self.session:
            self.session.close()

    def create(self, agent: AgentCreate) -> Agent:
        """
        Create a new agent.

        Args:
            agent: Agent data

        Returns:
            Created agent
        """
        db_agent = AgentModel(
            name=agent.name,
            description=agent.description,
            demographics=agent.demographics,
            personality_traits=agent.personality_traits,
            expertise_areas=agent.expertise_areas,
            evaluation_criteria_weights=agent.evaluation_criteria_weights
        )

        self.session.add(db_agent)
        self.session.commit()
        self.session.refresh(db_agent)

        return Agent.model_validate(db_agent)

    def get(self, agent_id: str) -> Optional[Agent]:
        """
        Get agent by ID.

        Args:
            agent_id: Agent ID

        Returns:
            Agent or None if not found
        """
        db_agent = self.session.query(AgentModel).filter(
            AgentModel.id == agent_id
        ).first()

        if db_agent:
            return Agent.model_validate(db_agent)
        return None

    def get_by_name(self, name: str) -> Optional[Agent]:
        """
        Get agent by name.

        Args:
            name: Agent name

        Returns:
            Agent or None if not found
        """
        db_agent = self.session.query(AgentModel).filter(
            AgentModel.name == name
        ).first()

        if db_agent:
            return Agent.model_validate(db_agent)
        return None

    def list(self, expertise_area: Optional[str] = None) -> List[Agent]:
        """
        List all agents, optionally filtered by expertise area.

        Args:
            expertise_area: Filter by expertise area (optional)

        Returns:
            List of agents
        """
        query = self.session.query(AgentModel)

        # Note: Filtering on JSON fields is database-specific
        # This simple version gets all and filters in Python
        db_agents = query.all()

        agents = [Agent.model_validate(agent) for agent in db_agents]

        if expertise_area:
            agents = [
                agent for agent in agents
                if expertise_area in agent.expertise_areas
            ]

        return agents

    def update(self, agent_id: str, update: AgentUpdate) -> Optional[Agent]:
        """
        Update an agent.

        Args:
            agent_id: Agent ID
            update: Update data

        Returns:
            Updated agent or None if not found
        """
        db_agent = self.session.query(AgentModel).filter(
            AgentModel.id == agent_id
        ).first()

        if not db_agent:
            return None

        # Update only provided fields
        update_data = update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(db_agent, key):
                setattr(db_agent, key, value)

        self.session.commit()
        self.session.refresh(db_agent)

        return Agent.model_validate(db_agent)

    def delete(self, agent_id: str) -> bool:
        """
        Delete an agent.

        Args:
            agent_id: Agent ID

        Returns:
            True if deleted, False if not found
        """
        db_agent = self.session.query(AgentModel).filter(
            AgentModel.id == agent_id
        ).first()

        if not db_agent:
            return False

        self.session.delete(db_agent)
        self.session.commit()
        return True

    def get_multiple(self, agent_ids: List[str]) -> List[Agent]:
        """
        Get multiple agents by their IDs.

        Args:
            agent_ids: List of agent IDs

        Returns:
            List of agents (may be fewer than requested if some not found)
        """
        db_agents = self.session.query(AgentModel).filter(
            AgentModel.id.in_(agent_ids)
        ).all()

        return [Agent.model_validate(agent) for agent in db_agents]

    def search(self, query: str) -> List[Agent]:
        """
        Search agents by name or description.

        Args:
            query: Search query

        Returns:
            List of matching agents
        """
        search_pattern = f"%{query}%"
        db_agents = self.session.query(AgentModel).filter(
            (AgentModel.name.like(search_pattern)) |
            (AgentModel.description.like(search_pattern))
        ).all()

        return [Agent.model_validate(agent) for agent in db_agents]
