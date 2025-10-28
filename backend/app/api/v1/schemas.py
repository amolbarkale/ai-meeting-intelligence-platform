import uuid
from pydantic import BaseModel
from datetime import datetime
from app.db.models import MeetingStatus
from typing import Optional

# Base model for meeting properties
class MeetingBase(BaseModel):
    original_filename: str

# Model for the initial upload response
class MeetingResponse(MeetingBase):
    id: uuid.UUID
    status: MeetingStatus
    created_at: datetime

    class Config:
        from_attributes = True

# Model for job status response
class JobStatusResponse(BaseModel):
    meeting_id: uuid.UUID
    status: MeetingStatus
    message: str


class MeetingDetailsResponse(MeetingResponse):
    transcript: Optional[str] = None
    summary: Optional[str] = None
    
    # Add the new fields
    key_points: Optional[str] = None
    action_items: Optional[str] = None
    sentiment: Optional[str] = None

    class Config:
        from_attributes = True