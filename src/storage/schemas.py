"""
Pydantic schemas for data validation and serialization.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class TestStatus(str, Enum):
    """Test execution status"""
    DRAFT = "draft"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentBase(BaseModel):
    """Base schema for Agent"""
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    demographics: Dict[str, Any] = Field(default_factory=dict)
    personality_traits: List[str] = Field(default_factory=list)
    expertise_areas: List[str] = Field(default_factory=list)
    evaluation_criteria_weights: Dict[str, float] = Field(default_factory=dict)


class AgentCreate(AgentBase):
    """Schema for creating an agent"""
    pass


class AgentUpdate(BaseModel):
    """Schema for updating an agent"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    demographics: Optional[Dict[str, Any]] = None
    personality_traits: Optional[List[str]] = None
    expertise_areas: Optional[List[str]] = None
    evaluation_criteria_weights: Optional[Dict[str, float]] = None


class Agent(AgentBase):
    """Schema for agent with database fields"""
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class APIConfigBase(BaseModel):
    """Base schema for API Configuration"""
    name: str = Field(..., min_length=1, max_length=200)
    endpoint: str = Field(..., min_length=1)
    api_key: str = Field(..., min_length=1)
    headers: Dict[str, str] = Field(default_factory=dict)
    example_response: Optional[str] = None


class APIConfigCreate(APIConfigBase):
    """Schema for creating API configuration"""
    pass


class APIConfig(APIConfigBase):
    """Schema for API configuration with database fields"""
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuestionBase(BaseModel):
    """Base schema for Question"""
    text: str = Field(..., min_length=1)
    category: Optional[str] = None
    priority: int = Field(default=1, ge=1, le=10)
    expected_tone: Optional[str] = None
    meta_data: Dict[str, Any] = Field(default_factory=dict)


class QuestionCreate(QuestionBase):
    """Schema for creating a question"""
    pass


class Question(QuestionBase):
    """Schema for question with database fields"""
    id: str

    model_config = ConfigDict(from_attributes=True)


class TestConfigBase(BaseModel):
    """Base schema for Test Configuration"""
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    task_context: str = Field(..., min_length=1)
    api_config_id: str
    agent_ids: List[str] = Field(default_factory=list)
    questions: List[QuestionCreate] = Field(default_factory=list)


class TestConfigCreate(TestConfigBase):
    """Schema for creating test configuration"""
    pass


class TestConfigUpdate(BaseModel):
    """Schema for updating test configuration"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    task_context: Optional[str] = None
    api_config_id: Optional[str] = None
    agent_ids: Optional[List[str]] = None
    questions: Optional[List[QuestionCreate]] = None
    status: Optional[TestStatus] = None


class TestConfig(TestConfigBase):
    """Schema for test configuration with database fields"""
    id: str
    status: TestStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EvaluationBase(BaseModel):
    """Base schema for Evaluation"""
    test_id: str
    question_id: str
    agent_id: str
    api_response: str
    likes: List[str] = Field(default_factory=list)
    dislikes: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    rating: Optional[float] = Field(None, ge=0, le=10)
    agent_perspective: Optional[str] = None
    raw_evaluation: Dict[str, Any] = Field(default_factory=dict)


class EvaluationCreate(EvaluationBase):
    """Schema for creating an evaluation"""
    pass


class Evaluation(EvaluationBase):
    """Schema for evaluation with database fields"""
    id: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class TestResultsSummary(BaseModel):
    """Summary of test results"""
    test_id: str
    test_name: str
    total_questions: int
    total_evaluations: int
    average_rating: Optional[float]
    common_likes: List[tuple[str, int]]  # (theme, count)
    common_dislikes: List[tuple[str, int]]  # (theme, count)
    top_suggestions: List[str]
    completed_at: datetime
