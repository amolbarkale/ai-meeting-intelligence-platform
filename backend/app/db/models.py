import uuid
from sqlalchemy import Column, String, DateTime, func, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from .database import Base
import enum

class MeetingStatus(enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_filename = Column(String, nullable=False)
    saved_filename = Column(String, unique=True, nullable=False)
    file_path = Column(String, nullable=False)
    status = Column(SQLEnum(MeetingStatus), nullable=False, default=MeetingStatus.PENDING)
    
    transcript = Column(String, nullable=True)
    summary = Column(String, nullable=True)
    key_points = Column(String, nullable=True)
    action_items = Column(String, nullable=True)
    sentiment = Column(String, nullable=True)
    tags = Column(String, nullable=True) # To store comma-separated tags
    knowledge_graph = Column(String, nullable=True) # To store JSON as a string
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
