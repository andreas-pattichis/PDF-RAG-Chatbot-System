"""
Pydantic models for API
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class Source(BaseModel):
    """Source information for a document chunk"""
    document: str
    page: Optional[int] = None
    chunk: int

class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., description="User's message")
    history: Optional[List[Dict[str, str]]] = Field(default=None, description="Chat history")
    document_id: Optional[str] = Field(default=None, description="Specific document ID to search")

class ChatResponse(BaseModel):
    """Chat response model"""
    message_id: str = Field(..., description="Unique message ID")
    response: str = Field(..., description="LLM response")
    sources: List[Source] = Field(default_factory=list, description="Sources used for response")