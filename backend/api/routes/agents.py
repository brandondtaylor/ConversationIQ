"""
Agent management API endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from src.agents.manager import AgentManager
from src.agents.generator import AgentGenerator
from src.storage.schemas import Agent, AgentCreate, AgentUpdate

router = APIRouter()


@router.get("", response_model=List[Agent])
async def list_agents(
    expertise: Optional[str] = Query(None, description="Filter by expertise area"),
    search: Optional[str] = Query(None, description="Search by name or description")
):
    """List all agents with optional filters"""
    with AgentManager() as manager:
        if search:
            agents = manager.search(search)
        elif expertise:
            agents = manager.list(expertise_area=expertise)
        else:
            agents = manager.list()

        return agents


@router.post("", response_model=Agent, status_code=201)
async def create_agent(agent: AgentCreate):
    """Create a new agent"""
    with AgentManager() as manager:
        created_agent = manager.create(agent)
        return created_agent


@router.get("/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str):
    """Get agent by ID"""
    with AgentManager() as manager:
        agent = manager.get(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return agent


@router.put("/{agent_id}", response_model=Agent)
async def update_agent(agent_id: str, update: AgentUpdate):
    """Update an agent"""
    with AgentManager() as manager:
        updated_agent = manager.update(agent_id, update)
        if not updated_agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return updated_agent


@router.delete("/{agent_id}", status_code=204)
async def delete_agent(agent_id: str):
    """Delete an agent"""
    with AgentManager() as manager:
        deleted = manager.delete(agent_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Agent not found")


@router.post("/generate", response_model=List[Agent], status_code=201)
async def generate_agents(
    task_description: str = Query(..., description="Task description for agent generation"),
    num_agents: int = Query(3, ge=1, le=10, description="Number of agents to generate"),
    target_demographics: Optional[List[str]] = Query(None, description="Target demographics"),
    diversity_focus: bool = Query(True, description="Prioritize diverse perspectives")
):
    """Generate agents for a specific task"""
    generator = AgentGenerator()

    # Generate agent templates
    agent_templates = generator.generate_agents_for_task(
        task_description=task_description,
        target_demographics=target_demographics,
        num_agents=num_agents,
        diversity_focus=diversity_focus
    )

    # Create agents in database
    created_agents = []
    with AgentManager() as manager:
        for template in agent_templates:
            agent = manager.create(template)
            created_agents.append(agent)

    return created_agents


@router.get("/by-name/{name}", response_model=Agent)
async def get_agent_by_name(name: str):
    """Get agent by name"""
    with AgentManager() as manager:
        agent = manager.get_by_name(name)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return agent
