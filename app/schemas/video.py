from datetime import datetime

from pydantic import BaseModel

from app.models.video import VideoStatus


class VideoOut(BaseModel):
    id: str
    project_id: str
    title: str
    status: VideoStatus
    script_text: str | None
    output_file_path: str | None
    error_message: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class VideoStatusOut(BaseModel):
    id: str
    status: VideoStatus
    error_message: str | None

    class Config:
        from_attributes = True