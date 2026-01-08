"""User preference operations for long-term memory"""
from typing import Dict, Optional
from datetime import datetime
from .models import UserPreference


class PreferenceOperations:
    """Operations for managing user preferences"""

    @staticmethod
    def set(key: str, value: str, category: Optional[str] = None) -> UserPreference:
        """Set or update a user preference"""
        pref, created = UserPreference.get_or_create(
            key=key,
            defaults={'value': value, 'category': category}
        )
        if not created:
            pref.value = value
            if category:
                pref.category = category
            pref.updated_at = datetime.now()
            pref.save()
        return pref

    @staticmethod
    def get(key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a user preference value"""
        try:
            return UserPreference.get(UserPreference.key == key).value
        except UserPreference.DoesNotExist:
            return default

    @staticmethod
    def get_all(category: Optional[str] = None) -> Dict[str, str]:
        """Get all preferences, optionally filtered by category"""
        query = UserPreference.select()
        if category:
            query = query.where(UserPreference.category == category)
        return {pref.key: pref.value for pref in query}

    @staticmethod
    def delete(key: str) -> bool:
        """Delete a user preference"""
        try:
            pref = UserPreference.get(UserPreference.key == key)
            pref.delete_instance()
            return True
        except UserPreference.DoesNotExist:
            return False

    @staticmethod
    def count() -> int:
        """Get total preference count"""
        return UserPreference.select().count()

