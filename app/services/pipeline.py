from app.core.database import SessionLocal
from app.models.video import Video, VideoStatus
from app.services.voice import generate_voice
from app.services.captions import generate_captions
from app.services.render import render_video

from app.services.crop import crop_to_vertical
from app.services.trim import trim_video
from app.services.silence import remove_silences
from app.services.captions import generate_captions
from app.services.burn_captions import burn_captions


def run_editor_pipeline(video_id: str) -> None:
    """
    Runs the editor pipeline on an uploaded video: trim (if requested),
    crop to vertical (if requested), remove silence (if requested),
    then always caption + burn. Skips any stage the user didn't ask for.
    """
    db = SessionLocal()
    try:
        video = db.get(Video, video_id)
        if video is None:
            return

        output_dir = f"storage/{video.project_id}"

        try:
            current_path = video.background_video_path

            if video.trim_start is not None and video.trim_end is not None:
                duration = video.trim_end - video.trim_start
                current_path = trim_video(current_path, video.trim_start, duration, output_dir)

            if video.crop_aspect == "9:16":
                current_path = crop_to_vertical(current_path, output_dir)

            if video.remove_silence:
                current_path = remove_silences(current_path, output_dir)

            captions_path = generate_captions(current_path, output_dir)
            video.captions_file_path = captions_path
            db.commit()

            output_path = burn_captions(current_path, captions_path, output_dir)
            video.output_file_path = output_path
            video.status = VideoStatus.done
            db.commit()

        except Exception as e:
            video.status = VideoStatus.failed
            video.error_message = str(e)
            db.commit()

    finally:
        db.close()

def run_pipeline(video_id: str) -> None:
    """
    Runs the full voice -> captions -> render pipeline for a video.
    Creates its own DB session since this runs in a background task,
    outside the request/response cycle that normally provides one.
    """
    db = SessionLocal()
    try:
        video = db.get(Video, video_id)
        if video is None:
            return

        output_dir = f"storage/{video.project_id}"

        try:
            voice_path = generate_voice(video.script_text, output_dir)
            video.voice_file_path = voice_path
            db.commit()

            captions_path = generate_captions(voice_path, output_dir)
            video.captions_file_path = captions_path
            db.commit()

            output_path = render_video(
                video.background_video_path,
                voice_path,
                captions_path,
                output_dir,
            )
            video.output_file_path = output_path
            video.status = VideoStatus.done
            db.commit()

        except Exception as e:
            video.status = VideoStatus.failed
            video.error_message = str(e)
            db.commit()

    finally:
        db.close()