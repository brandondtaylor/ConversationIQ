"""
Test configuration management.
"""
from typing import Optional, List
from sqlalchemy.orm import Session

from ..storage.database import TestConfigModel, QuestionModel, get_db_manager
from ..storage.schemas import (
    TestConfig, TestConfigCreate, TestConfigUpdate,
    TestStatus, QuestionCreate, Question
)


class TestConfigManager:
    """Manages test configurations in the database"""

    def __init__(self, session: Optional[Session] = None):
        """
        Initialize test config manager.

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

    def create(self, config: TestConfigCreate) -> TestConfig:
        """
        Create a new test configuration.

        Args:
            config: Test configuration data

        Returns:
            Created test configuration
        """
        # Create test config
        db_config = TestConfigModel(
            name=config.name,
            description=config.description,
            task_context=config.task_context,
            api_config_id=config.api_config_id,
            agent_ids=config.agent_ids,
            status=TestStatus.DRAFT
        )

        self.session.add(db_config)
        self.session.flush()  # Get the ID

        # Add questions
        for question_data in config.questions:
            db_question = QuestionModel(
                test_config_id=db_config.id,
                text=question_data.text,
                category=question_data.category,
                priority=question_data.priority,
                expected_tone=question_data.expected_tone,
                metadata=question_data.metadata
            )
            self.session.add(db_question)

        self.session.commit()
        self.session.refresh(db_config)

        return TestConfig.model_validate(db_config)

    def get(self, config_id: str) -> Optional[TestConfig]:
        """
        Get test configuration by ID.

        Args:
            config_id: Configuration ID

        Returns:
            Test configuration or None if not found
        """
        db_config = self.session.query(TestConfigModel).filter(
            TestConfigModel.id == config_id
        ).first()

        if db_config:
            return TestConfig.model_validate(db_config)
        return None

    def get_by_name(self, name: str) -> Optional[TestConfig]:
        """
        Get test configuration by name.

        Args:
            name: Configuration name

        Returns:
            Test configuration or None if not found
        """
        db_config = self.session.query(TestConfigModel).filter(
            TestConfigModel.name == name
        ).first()

        if db_config:
            return TestConfig.model_validate(db_config)
        return None

    def list(self, status: Optional[TestStatus] = None) -> List[TestConfig]:
        """
        List all test configurations.

        Args:
            status: Filter by status (optional)

        Returns:
            List of test configurations
        """
        query = self.session.query(TestConfigModel)

        if status:
            query = query.filter(TestConfigModel.status == status)

        db_configs = query.all()
        return [TestConfig.model_validate(config) for config in db_configs]

    def update(self, config_id: str, update: TestConfigUpdate) -> Optional[TestConfig]:
        """
        Update a test configuration.

        Args:
            config_id: Configuration ID
            update: Update data

        Returns:
            Updated configuration or None if not found
        """
        db_config = self.session.query(TestConfigModel).filter(
            TestConfigModel.id == config_id
        ).first()

        if not db_config:
            return None

        # Update only provided fields
        update_data = update.model_dump(exclude_unset=True)

        # Handle questions separately
        questions = update_data.pop('questions', None)

        for key, value in update_data.items():
            if hasattr(db_config, key) and value is not None:
                setattr(db_config, key, value)

        # Update questions if provided
        if questions is not None:
            # Delete existing questions
            self.session.query(QuestionModel).filter(
                QuestionModel.test_config_id == config_id
            ).delete()

            # Add new questions
            for question_data in questions:
                if isinstance(question_data, dict):
                    question_data = QuestionCreate(**question_data)
                db_question = QuestionModel(
                    test_config_id=config_id,
                    text=question_data.text,
                    category=question_data.category,
                    priority=question_data.priority,
                    expected_tone=question_data.expected_tone,
                    metadata=question_data.metadata
                )
                self.session.add(db_question)

        self.session.commit()
        self.session.refresh(db_config)

        return TestConfig.model_validate(db_config)

    def delete(self, config_id: str) -> bool:
        """
        Delete a test configuration and its questions.

        Args:
            config_id: Configuration ID

        Returns:
            True if deleted, False if not found
        """
        db_config = self.session.query(TestConfigModel).filter(
            TestConfigModel.id == config_id
        ).first()

        if not db_config:
            return False

        # Delete questions first
        self.session.query(QuestionModel).filter(
            QuestionModel.test_config_id == config_id
        ).delete()

        # Delete config
        self.session.delete(db_config)
        self.session.commit()
        return True

    def get_questions(self, config_id: str) -> List[Question]:
        """
        Get all questions for a test configuration.

        Args:
            config_id: Configuration ID

        Returns:
            List of questions
        """
        db_questions = self.session.query(QuestionModel).filter(
            QuestionModel.test_config_id == config_id
        ).order_by(QuestionModel.priority.desc()).all()

        return [Question.model_validate(q) for q in db_questions]

    def add_questions(self, config_id: str, questions: List[QuestionCreate]) -> bool:
        """
        Add questions to an existing test configuration.

        Args:
            config_id: Configuration ID
            questions: Questions to add

        Returns:
            True if successful, False if config not found
        """
        # Check if config exists
        if not self.get(config_id):
            return False

        # Add questions
        for question_data in questions:
            db_question = QuestionModel(
                test_config_id=config_id,
                text=question_data.text,
                category=question_data.category,
                priority=question_data.priority,
                expected_tone=question_data.expected_tone,
                metadata=question_data.metadata
            )
            self.session.add(db_question)

        self.session.commit()
        return True

    def update_status(self, config_id: str, status: TestStatus) -> Optional[TestConfig]:
        """
        Update test status.

        Args:
            config_id: Configuration ID
            status: New status

        Returns:
            Updated configuration or None if not found
        """
        return self.update(config_id, TestConfigUpdate(status=status))
