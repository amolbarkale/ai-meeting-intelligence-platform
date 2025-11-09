import uuid
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel
from datetime import datetime
from app.db.models import MeetingStatus

class MeetingBase(BaseModel):
    original_filename: str

# Model for the initial upload response
class MeetingResponse(MeetingBase):
    id: uuid.UUID
    status: MeetingStatus
    created_at: datetime

    class Config:
        from_attributes = True

class JobStatusResponse(BaseModel):
    meeting_id: uuid.UUID
    status: MeetingStatus
    message: str


class MeetingDetailsResponse(MeetingResponse):
    transcript: Optional[str] = None
    summary: Optional[str] = None
    key_points: Optional[str] = None
    action_items: Optional[str] = None
    sentiment: Optional[str] = None
    tags: Optional[str] = None
    knowledge_graph: Optional[str] = None

    class Config:
        from_attributes = True

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class MeetingChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []

class MeetingChatResponse(BaseModel):
    meeting_id: uuid.UUID
    reply: str
    context: Dict[str, Any]

class SearchResult(BaseModel):
    content: str
    metadata: Dict[str, Any]
    distance: float

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]