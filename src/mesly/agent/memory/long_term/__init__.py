"""
Long-term memory package for the agent.

This package provides persistent storage for:
- Conversation history
- Knowledge items (facts about the user)
- User preferences
- Browser history

Usage:
    from mesly.agent.memory.long_term import LongTermMemory

    # Initialize memory
    memory = LongTermMemory()

    # Save a conversation
    memory.conversations.save(
        user_input="What's the weather?",
        ai_response="It's sunny today!",
        context_type="simple"
    )

    # Save knowledge
    memory.knowledge.save(
        key="favorite_color",
        value="blue",
        category="personal"
    )

    # Set preferences
    memory.preferences.set("theme", "dark", category="ui")

    # Get recent conversations
    recent = memory.conversations.get_recent(limit=5)

    # Search knowledge
    results = memory.knowledge.search("color")

    # Get stats
    stats = memory.get_stats()

    # Close when done
    memory.close()
"""

from .memory import LongTermMemory
from .models import Conversation, KnowledgeItem, UserPreference, BrowserHistory

__all__ = [
    'LongTermMemory',
    'Conversation',
    'KnowledgeItem',
    'UserPreference',
    'BrowserHistory'
]

