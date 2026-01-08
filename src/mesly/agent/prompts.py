from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class PromptTemplate(BaseModel):
    text_selected: Optional[str] = Field(default="", description="Text selected by user in browser")
    visited_pages: List[Dict[str, str]] = Field(default_factory=list, description="Recently visited pages agent")
    ocr_text: Optional[str] = Field(default="", description="Text extracted from screenshot via OCR")
    basic_instructions: str = Field(description="System instructions for the AI")
    user_question: str = Field(description="User's question or request")
    date: datetime = Field(default_factory=datetime.now, description="Timestamp of the prompt")

