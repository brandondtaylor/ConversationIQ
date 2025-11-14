#!/usr/bin/env python3
"""
Database migration script for ConversationIQ

This script handles schema changes and migrations for existing databases.
Run this script when upgrading to ensure your database schema is up to date.

Usage:
    python scripts/migrate_database.py [database_url]

Example:
    python scripts/migrate_database.py sqlite:///./data/conversationiq.db
"""
import sys
import logging
from pathlib import Path
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import OperationalError

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.database import Base, get_db_manager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseMigrator:
    """Handles database schema migrations"""

    def __init__(self, database_url: str = "sqlite:///./data/conversationiq.db"):
        self.database_url = database_url
        self.engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {}
        )
        self.inspector = inspect(self.engine)

    def get_table_columns(self, table_name: str):
        """Get list of columns for a table"""
        try:
            return [col['name'] for col in self.inspector.get_columns(table_name)]
        except Exception:
            return []

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists"""
        return table_name in self.inspector.get_table_names()

    def column_exists(self, table_name: str, column_name: str) -> bool:
        """Check if a column exists in a table"""
        columns = self.get_table_columns(table_name)
        return column_name in columns

    def migrate_questions_metadata_column(self):
        """
        Migrate 'metadata' column to 'meta_data' in questions table.
        This avoids conflict with SQLAlchemy's reserved 'metadata' attribute.
        """
        if not self.table_exists('questions'):
            logger.info("Questions table does not exist yet, skipping metadata migration")
            return

        has_metadata = self.column_exists('questions', 'metadata')
        has_meta_data = self.column_exists('questions', 'meta_data')

        if has_metadata and not has_meta_data:
            logger.info("Migrating 'metadata' column to 'meta_data' in questions table")
            with self.engine.begin() as conn:
                if self.database_url.startswith('sqlite'):
                    # SQLite doesn't support direct column rename, need to use ALTER TABLE
                    conn.execute(text("ALTER TABLE questions RENAME COLUMN metadata TO meta_data"))
                else:
                    # PostgreSQL/MySQL syntax
                    conn.execute(text("ALTER TABLE questions RENAME COLUMN metadata TO meta_data"))
            logger.info("✓ Successfully migrated metadata column")
        elif has_meta_data:
            logger.info("✓ Questions table already has meta_data column")
        else:
            logger.info("✓ Questions table is up to date")

    def add_response_time_column(self):
        """
        Add response_time column to evaluations table if it doesn't exist.
        """
        if not self.table_exists('evaluations'):
            logger.info("Evaluations table does not exist yet, skipping response_time migration")
            return

        if not self.column_exists('evaluations', 'response_time'):
            logger.info("Adding response_time column to evaluations table")
            with self.engine.begin() as conn:
                conn.execute(text("ALTER TABLE evaluations ADD COLUMN response_time FLOAT"))
            logger.info("✓ Successfully added response_time column")
        else:
            logger.info("✓ Evaluations table already has response_time column")

    def add_evaluation_mode_column(self):
        """
        Add evaluation_mode column to test_configs table if it doesn't exist.
        """
        if not self.table_exists('test_configs'):
            logger.info("Test configs table does not exist yet, skipping evaluation_mode migration")
            return

        if not self.column_exists('test_configs', 'evaluation_mode'):
            logger.info("Adding evaluation_mode column to test_configs table")
            with self.engine.begin() as conn:
                # Add column with default value 'single_agent'
                conn.execute(text(
                    "ALTER TABLE test_configs ADD COLUMN evaluation_mode VARCHAR(50) DEFAULT 'single_agent'"
                ))
            logger.info("✓ Successfully added evaluation_mode column")
        else:
            logger.info("✓ Test configs table already has evaluation_mode column")

    def create_missing_tables(self):
        """Create any missing tables"""
        logger.info("Creating any missing tables...")
        Base.metadata.create_all(bind=self.engine)
        logger.info("✓ All tables exist")

    def run_all_migrations(self):
        """Run all migrations in order"""
        logger.info("=" * 60)
        logger.info("Starting database migration")
        logger.info(f"Database URL: {self.database_url}")
        logger.info("=" * 60)

        try:
            # Step 1: Create any missing tables
            self.create_missing_tables()

            # Step 2: Run column migrations
            self.migrate_questions_metadata_column()
            self.add_response_time_column()
            self.add_evaluation_mode_column()

            logger.info("=" * 60)
            logger.info("✓ Database migration completed successfully!")
            logger.info("=" * 60)
            return True

        except Exception as e:
            logger.error(f"✗ Migration failed: {e}", exc_info=True)
            logger.info("=" * 60)
            return False


def main():
    """Main entry point for migration script"""
    # Get database URL from command line or use default
    database_url = sys.argv[1] if len(sys.argv) > 1 else "sqlite:///./data/conversationiq.db"

    # Ensure data directory exists for SQLite
    if database_url.startswith("sqlite"):
        db_path = database_url.replace("sqlite:///", "")
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Ensured database directory exists: {Path(db_path).parent}")

    # Run migrations
    migrator = DatabaseMigrator(database_url)
    success = migrator.run_all_migrations()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
