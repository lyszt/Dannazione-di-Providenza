"""Database models for long-term memory"""
from peewee import Model, CharField, TextField, DateTimeField, FloatField
from datetime import datetime
from .database import db


class BaseModel(Model):
    """Base model for all memory tables"""
    class Meta:
        database = db


class Conversation(BaseModel):
    """Stores conversation history"""
    timestamp = DateTimeField(default=datetime.now, index=True)
    user_input = TextField()
    ai_response = TextField()
    context_type = CharField(max_length=50, null=True)  # 'ocr', 'selection', 'browser', 'simple'
    tags = TextField(null=True)  # Comma-separated tags for categorization

    class Meta:
        table_name = 'conversations'


class KnowledgeItem(BaseModel):
    """Stores facts, information, and knowledge the assistant has learned about the user"""
    key = CharField(max_length=255, index=True)  # e.g., "favorite_color", "work_schedule"
    value = TextField()  # The actual information
    category = CharField(max_length=100, null=True)  # 'personal', 'work', 'preferences', etc.
    context = TextField(null=True)  # How this was learned
    confidence = FloatField(default=1.0)  # 0.0-1.0 confidence in this information
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'knowledge_items'


class UserPreference(BaseModel):
    """Stores user preferences and patterns"""
    key = CharField(max_length=100, unique=True, index=True)
    value = TextField()
    category = CharField(max_length=50, null=True)  # 'language', 'ui', 'behavior'
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'user_preferences'


class BrowserHistory(BaseModel):
    """Stores browser context history for the agent"""
    url = TextField()
    title = TextField()
    body_preview = TextField()  # First 500 chars
    visited_at = DateTimeField(default=datetime.now, index=True)
    language_detected = CharField(max_length=10, null=True)

    class Meta:
        table_name = 'browser_history'

