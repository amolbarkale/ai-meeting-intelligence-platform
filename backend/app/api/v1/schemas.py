import uuid
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
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

class GraphParticipant(BaseModel):
    id: Optional[str] = None
    name: str
    role: Optional[str] = None
    organization: Optional[str] = None

class GraphDecision(BaseModel):
    id: Optional[str] = None
    title: str
    description: Optional[str] = None
    owner: Optional[str] = None
    due_date: Optional[str] = None

class GraphTimelineEntry(BaseModel):
    id: Optional[str] = None
    label: str
    summary: Optional[str] = None
    start_time: Optional[str] = None

class GraphContextResponse(BaseModel):
    meeting_id: uuid.UUID
    summary: Optional[str] = None
    key_points: Optional[str] = None
    action_items: Optional[str] = None
    sentiment: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)
    participants: List[GraphParticipant] = Field(default_factory=list)
    decisions: List[GraphDecision] = Field(default_factory=list)
    timeline: List[GraphTimelineEntry] = Field(default_factory=list)
    key_points_structured: List[Dict[str, Any]] = Field(default_factory=list)
    action_items_structured: List[Dict[str, Any]] = Field(default_factory=list)
    concepts: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    title: Optional[str] = None

class SearchResult(BaseModel):
    content: str
    metadata: Dict[str, Any]
    distance: float

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]