import enum
import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class VideoStatus(str, enum.Enum):
    draft = "draft"
    processing = "processing"
    done = "done"
    failed = "failed"


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[VideoStatus] = mapped_column(Enum(VideoStatus), default=VideoStatus.draft)

    script_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    voice_file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    captions_file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    background_video_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    output_file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="videos")
    jobs = relationship("Job", back_populates="video", cascade="all, delete-orphan")