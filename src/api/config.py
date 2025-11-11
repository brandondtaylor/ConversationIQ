"""
API configuration management.
"""
from typing import Optional, List
from sqlalchemy.orm import Session

from ..storage.database import APIConfigModel, get_db_manager
from ..storage.schemas import APIConfig, APIConfigCreate
from .client import ChatAPIClient


class APIConfigManager:
    """Manages API configurations in the database"""

    def __init__(self, session: Optional[Session] = None):
        """
        Initialize API config manager.

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

    def create(self, config: APIConfigCreate) -> APIConfig:
        """
        Create a new API configuration.

        Args:
            config: API configuration data

        Returns:
            Created API configuration
        """
        db_config = APIConfigModel(
            name=config.name,
            endpoint=config.endpoint,
            api_key=config.api_key,
            headers=config.headers,
            example_response=config.example_response
        )

        self.session.add(db_config)
        self.session.commit()
        self.session.refresh(db_config)

        return APIConfig.model_validate(db_config)

    def get(self, config_id: str) -> Optional[APIConfig]:
        """
        Get API configuration by ID.

        Args:
            config_id: Configuration ID

        Returns:
            API configuration or None if not found
        """
        db_config = self.session.query(APIConfigModel).filter(
            APIConfigModel.id == config_id
        ).first()

        if db_config:
            return APIConfig.model_validate(db_config)
        return None

    def get_by_name(self, name: str) -> Optional[APIConfig]:
        """
        Get API configuration by name.

        Args:
            name: Configuration name

        Returns:
            API configuration or None if not found
        """
        db_config = self.session.query(APIConfigModel).filter(
            APIConfigModel.name == name
        ).first()

        if db_config:
            return APIConfig.model_validate(db_config)
        return None

    def list(self) -> List[APIConfig]:
        """
        List all API configurations.

        Returns:
            List of API configurations
        """
        db_configs = self.session.query(APIConfigModel).all()
        return [APIConfig.model_validate(config) for config in db_configs]

    def update(self, config_id: str, **kwargs) -> Optional[APIConfig]:
        """
        Update an API configuration.

        Args:
            config_id: Configuration ID
            **kwargs: Fields to update

        Returns:
            Updated configuration or None if not found
        """
        db_config = self.session.query(APIConfigModel).filter(
            APIConfigModel.id == config_id
        ).first()

        if not db_config:
            return None

        for key, value in kwargs.items():
            if hasattr(db_config, key) and value is not None:
                setattr(db_config, key, value)

        self.session.commit()
        self.session.refresh(db_config)

        return APIConfig.model_validate(db_config)

    def delete(self, config_id: str) -> bool:
        """
        Delete an API configuration.

        Args:
            config_id: Configuration ID

        Returns:
            True if deleted, False if not found
        """
        db_config = self.session.query(APIConfigModel).filter(
            APIConfigModel.id == config_id
        ).first()

        if not db_config:
            return False

        self.session.delete(db_config)
        self.session.commit()
        return True

    def create_client(self, config_id: str) -> Optional[ChatAPIClient]:
        """
        Create a ChatAPIClient from a configuration.

        Args:
            config_id: Configuration ID

        Returns:
            ChatAPIClient or None if configuration not found
        """
        config = self.get(config_id)
        if not config:
            return None

        return ChatAPIClient(
            endpoint=config.endpoint,
            api_key=config.api_key,
            headers=config.headers
        )

    def test_config(self, config_id: str) -> tuple[bool, str]:
        """
        Test an API configuration.

        Args:
            config_id: Configuration ID

        Returns:
            Tuple of (success: bool, message: str)
        """
        client = self.create_client(config_id)
        if not client:
            return False, "Configuration not found"

        return client.test_connection()
