"""
SQLAlchemy database models and database connection setup.
"""
from datetime import datetime
from typing import Optional
import uuid
import json

from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, Float, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.types import TypeDecorator, TEXT

from .schemas import TestStatus


Base = declarative_base()


class JSONEncodedDict(TypeDecorator):
    """Enables JSON storage in database columns."""
    impl = TEXT
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class AgentModel(Base):
    """SQLAlchemy model for Agent"""
    __tablename__ = "agents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    demographics = Column(JSONEncodedDict, nullable=False, default=dict)
    personality_traits = Column(JSONEncodedDict, nullable=False, default=list)
    expertise_areas = Column(JSONEncodedDict, nullable=False, default=list)
    evaluation_criteria_weights = Column(JSONEncodedDict, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Agent(id={self.id}, name={self.name})>"


class APIConfigModel(Base):
    """SQLAlchemy model for API Configuration"""
    __tablename__ = "api_configs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False, index=True)
    endpoint = Column(String, nullable=False)
    api_key = Column(String, nullable=False)
    headers = Column(JSONEncodedDict, nullable=False, default=dict)
    example_response = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<APIConfig(id={self.id}, name={self.name})>"


class QuestionModel(Base):
    """SQLAlchemy model for Question"""
    __tablename__ = "questions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    test_config_id = Column(String, nullable=False, index=True)
    text = Column(Text, nullable=False)
    category = Column(String, nullable=True)
    priority = Column(Integer, nullable=False, default=1)
    expected_tone = Column(String, nullable=True)
    metadata = Column(JSONEncodedDict, nullable=False, default=dict)

    def __repr__(self):
        return f"<Question(id={self.id}, text={self.text[:50]})>"


class TestConfigModel(Base):
    """SQLAlchemy model for Test Configuration"""
    __tablename__ = "test_configs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    task_context = Column(Text, nullable=False)
    api_config_id = Column(String, nullable=False)
    agent_ids = Column(JSONEncodedDict, nullable=False, default=list)
    status = Column(SQLEnum(TestStatus), nullable=False, default=TestStatus.DRAFT)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<TestConfig(id={self.id}, name={self.name}, status={self.status})>"


class EvaluationModel(Base):
    """SQLAlchemy model for Evaluation"""
    __tablename__ = "evaluations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    test_id = Column(String, nullable=False, index=True)
    question_id = Column(String, nullable=False, index=True)
    agent_id = Column(String, nullable=False, index=True)
    api_response = Column(Text, nullable=False)
    likes = Column(JSONEncodedDict, nullable=False, default=list)
    dislikes = Column(JSONEncodedDict, nullable=False, default=list)
    suggestions = Column(JSONEncodedDict, nullable=False, default=list)
    rating = Column(Float, nullable=True)
    agent_perspective = Column(Text, nullable=True)
    raw_evaluation = Column(JSONEncodedDict, nullable=False, default=dict)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Evaluation(id={self.id}, test_id={self.test_id}, agent_id={self.agent_id})>"


class DatabaseManager:
    """Manages database connections and sessions"""

    def __init__(self, database_url: str = "sqlite:///./data/conversationiq.db"):
        """
        Initialize database manager.

        Args:
            database_url: SQLAlchemy database URL
        """
        self.engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {},
            echo=False
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self):
        """Drop all database tables (use with caution!)"""
        Base.metadata.drop_all(bind=self.engine)

    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()

    def reset_database(self):
        """Reset database by dropping and recreating all tables"""
        self.drop_tables()
        self.create_tables()


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_db_manager(database_url: str = "sqlite:///./data/conversationiq.db") -> DatabaseManager:
    """Get or create global database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(database_url)
    return _db_manager


def init_database(database_url: str = "sqlite:///./data/conversationiq.db"):
    """Initialize database with tables"""
    db_manager = get_db_manager(database_url)
    db_manager.create_tables()
    return db_manager
