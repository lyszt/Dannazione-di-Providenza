"""Conversation operations for long-term memory"""
from typing import List, Optional
from datetime import datetime
from .models import Conversation


class ConversationOperations:
    """Operations for managing conversation history"""

    @staticmethod
    def save(
        user_input: str,
        ai_response: str,
        context_type: Optional[str] = None,
        tags: Optional[str] = None
    ) -> Conversation:
        """Save a conversation exchange"""
        return Conversation.create(
            user_input=user_input,
            ai_response=ai_response,
            context_type=context_type,
            tags=tags
        )

    @staticmethod
    def get_recent(limit: int = 10) -> List[Conversation]:
        """Get recent conversations"""
        return list(Conversation.select().order_by(Conversation.timestamp.desc()).limit(limit))

    @staticmethod
    def get_by_type(context_type: str, limit: int = 20) -> List[Conversation]:
        """Get conversations filtered by context type"""
        return list(
            Conversation.select()
            .where(Conversation.context_type == context_type)
            .order_by(Conversation.timestamp.desc())
            .limit(limit)
        )

    @staticmethod
    def search(query: str, limit: int = 20) -> List[Conversation]:
        """Search conversations by user input or AI response"""
        return list(
            Conversation.select()
            .where(
                (Conversation.user_input.contains(query)) |
                (Conversation.ai_response.contains(query))
            )
            .order_by(Conversation.timestamp.desc())
            .limit(limit)
        )

    @staticmethod
    def delete_old(days: int = 30) -> int:
        """Delete conversations older than specified days"""
        cutoff = datetime.now().timestamp() - (days * 86400)
        query = Conversation.delete().where(Conversation.timestamp < datetime.fromtimestamp(cutoff))
        return query.execute()

    @staticmethod
    def count() -> int:
        """Get total conversation count"""
        return Conversation.select().count()

