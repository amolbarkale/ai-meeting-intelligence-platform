import uuid
from pydantic import BaseModel
from datetime import datetime
from app.db.models import MeetingStatus

# Base model for meeting properties
class MeetingBase(BaseModel):
    original_filename: str

# Model for API response
class MeetingResponse(MeetingBase):
    id: uuid.UUID
    status: MeetingStatus
    created_at: datetime

    class Config:
        from_attributes = True # Formerly orm_mode

# Model for job status response
class JobStatusResponse(BaseModel):
    meeting_id: uuid.UUID
    status: MeetingStatus
    message: str