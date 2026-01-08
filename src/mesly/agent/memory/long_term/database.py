"""Database initialization and configuration for long-term memory"""
from pathlib import Path
from peewee import SqliteDatabase

# Initialize SQLite database for agent's long-term memory
db_path = Path(__file__).parent / "agent_memory.db"
db = SqliteDatabase(str(db_path))


def initialize_database():
    """Initialize database connection and create tables"""
    # Import models here to avoid circular import
    from .models import Conversation, KnowledgeItem, UserPreference, BrowserHistory

    db.connect()
    db.create_tables([Conversation, KnowledgeItem, UserPreference, BrowserHistory])


def close_database():
    """Close database connection"""
    if not db.is_closed():
        db.close()
