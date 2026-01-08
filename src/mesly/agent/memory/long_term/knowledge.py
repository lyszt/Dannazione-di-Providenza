"""Knowledge management operations for long-term memory"""
from typing import List, Optional
from datetime import datetime
from .models import KnowledgeItem


class KnowledgeOperations:
    """Operations for managing knowledge items"""

    @staticmethod
    def save(
        key: str,
        value: str,
        category: Optional[str] = None,
        context: Optional[str] = None,
        confidence: float = 1.0
    ) -> KnowledgeItem:
        """Save a knowledge item about the user or their preferences"""
        existing = KnowledgeOperations.get(key)
        if existing:
            existing.value = value
            existing.category = category or existing.category
            existing.context = context or existing.context
            existing.confidence = confidence
            existing.updated_at = datetime.now()
            existing.save()
            return existing

        return KnowledgeItem.create(
            key=key,
            value=value,
            category=category,
            context=context,
            confidence=confidence
        )

    @staticmethod
    def get(key: str) -> Optional[KnowledgeItem]:
        """Get a specific knowledge item"""
        try:
            return KnowledgeItem.get(KnowledgeItem.key == key)
        except KnowledgeItem.DoesNotExist:
            return None

    @staticmethod
    def get_by_category(category: str, limit: int = 100) -> List[KnowledgeItem]:
        """Get all knowledge items for a specific category"""
        return list(
            KnowledgeItem.select()
            .where(KnowledgeItem.category == category)
            .order_by(KnowledgeItem.updated_at.desc())
            .limit(limit)
        )

    @staticmethod
    def search(query: str, limit: int = 20) -> List[KnowledgeItem]:
        """Search knowledge items by key or value"""
        return list(
            KnowledgeItem.select()
            .where(
                (KnowledgeItem.key.contains(query)) |
                (KnowledgeItem.value.contains(query))
            )
            .order_by(KnowledgeItem.updated_at.desc())
            .limit(limit)
        )

    @staticmethod
    def delete(key: str) -> bool:
        """Delete a knowledge item"""
        try:
            item = KnowledgeItem.get(KnowledgeItem.key == key)
            item.delete_instance()
            return True
        except KnowledgeItem.DoesNotExist:
            return False

    @staticmethod
    def get_all() -> List[KnowledgeItem]:
        """Get all knowledge items"""
        return list(KnowledgeItem.select().order_by(KnowledgeItem.updated_at.desc()))

    @staticmethod
    def count() -> int:
        """Get total knowledge item count"""
        return KnowledgeItem.select().count()

    @staticmethod
    def get_categories() -> List[str]:
        """Get all unique categories"""
        return [cat[0] for cat in KnowledgeItem.select(KnowledgeItem.category).distinct().tuples() if cat[0]]

