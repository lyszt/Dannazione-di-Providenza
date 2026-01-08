"""Main LongTermMemory class - centralized interface for all operations"""
from typing import Dict, Any
from .database import initialize_database, close_database
from .conversations import ConversationOperations
from .knowledge import KnowledgeOperations
from .preferences import PreferenceOperations
from .browser_history import BrowserHistoryOperations
from .models import Conversation, KnowledgeItem, UserPreference, BrowserHistory


class LongTermMemory:
    """
    Agent's long-term memory using SQLite via Peewee.
    Centralized interface for all memory operations.
    """

    def __init__(self):
        """Initialize database and create tables"""
        initialize_database()

        # Operation handlers
        self.conversations = ConversationOperations
        self.knowledge = KnowledgeOperations
        self.preferences = PreferenceOperations
        self.browser_history = BrowserHistoryOperations

    def close(self):
        """Close database connection"""
        close_database()

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the memory database"""
        return {
            'total_conversations': self.conversations.count(),
            'total_knowledge_items': self.knowledge.count(),
            'total_preferences': self.preferences.count(),
            'total_browser_history': self.browser_history.count(),
            'knowledge_categories': self.knowledge.get_categories()
        }

    def clear_all_data(self) -> bool:
        """WARNING: Delete all data from all tables"""
        try:
            Conversation.delete().execute()
            KnowledgeItem.delete().execute()
            UserPreference.delete().execute()
            BrowserHistory.delete().execute()
            return True
        except Exception:
            return False

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

