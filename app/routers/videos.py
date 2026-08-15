import os
import shutil
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.project import Project
from app.models.user import User
from app.models.video import Video
from app.schemas.video import VideoOut, VideoStatusOut

from fastapi import BackgroundTasks
from app.services.pipeline import run_pipeline
from app.models.video import VideoStatus
from fastapi.responses import FileResponse

from pydantic import BaseModel
from app.services.pipeline import run_editor_pipeline

router = APIRouter(prefix="/projects/{project_id}/videos", tags=["videos"])


def _get_owned_project(project_id: str, db: Session, current_user: User) -> Project:
    project = db.get(Project, project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _get_owned_video(project_id: str, video_id: str, db: Session, current_user: User) -> Video:
    _get_owned_project(project_id, db, current_user)
    video = db.get(Video, video_id)
    if not video or video.project_id != project_id:
        raise HTTPException(status_code=404, detail="Video not found")
    return video


@router.post("", response_model=VideoOut, status_code=201)
def create_video(
    project_id: str,
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    script_text: str | None = Form(None),
    background_video: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_owned_project(project_id, db, current_user)

    project_dir = os.path.join(settings.storage_dir, project_id)
    os.makedirs(project_dir, exist_ok=True)

    video_id = str(uuid.uuid4())
    ext = os.path.splitext(background_video.filename or "")[1] or ".mp4"
    background_path = os.path.join(project_dir, f"{video_id}_background{ext}")

    with open(background_path, "wb") as f:
        shutil.copyfileobj(background_video.file, f)

    video = Video(
        id=video_id,
        project_id=project_id,
        title=title,
        script_text=script_text,
        background_video_path=background_path,
        status=VideoStatus.draft,
    )
    db.add(video)
    db.commit()
    db.refresh(video)

    return video

@router.get("", response_model=list[VideoOut])
def list_videos(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_owned_project(project_id, db, current_user)
    return db.query(Video).filter(Video.project_id == project_id).all()


@router.get("/{video_id}", response_model=VideoOut)
def get_video(
    project_id: str,
    video_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _get_owned_video(project_id, video_id, db, current_user)


@router.get("/{video_id}/status", response_model=VideoStatusOut)
def get_video_status(
    project_id: str,
    video_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _get_owned_video(project_id, video_id, db, current_user)

@router.get("/{video_id}/download")
def download_video(
    project_id: str,
    video_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    video = _get_owned_video(project_id, video_id, db, current_user)
    if not video.output_file_path or not os.path.exists(video.output_file_path):
        raise HTTPException(status_code=400, detail="Video is not rendered yet")
    return FileResponse(video.output_file_path, media_type="video/mp4", filename=f"{video.title}.mp4")

class VideoEditRequest(BaseModel):
    trim_start: float | None = None
    trim_end: float | None = None
    crop_aspect: str | None = None
    remove_silence: bool = False
    add_captions: bool = True

@router.get("/{video_id}/source")
def get_video_source(
    project_id: str,
    video_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    video = _get_owned_video(project_id, video_id, db, current_user)
    if not video.background_video_path or not os.path.exists(video.background_video_path):
        raise HTTPException(status_code=400, detail="No source video uploaded")
    return FileResponse(video.background_video_path, media_type="video/mp4")


@router.patch("/{video_id}/edit", response_model=VideoOut)
def edit_video(
    project_id: str,
    video_id: str,
    payload: VideoEditRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    video = _get_owned_video(project_id, video_id, db, current_user)

    video.trim_start = payload.trim_start
    video.trim_end = payload.trim_end
    video.crop_aspect = payload.crop_aspect
    video.remove_silence = payload.remove_silence
    video.add_captions = payload.add_captions
    video.status = VideoStatus.processing
    db.commit()
    db.refresh(video)

    background_tasks.add_task(run_editor_pipeline, video.id)

    return video