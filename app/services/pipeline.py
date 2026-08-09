from app.core.database import SessionLocal
from app.models.video import Video, VideoStatus
from app.services.voice import generate_voice
from app.services.captions import generate_captions
from app.services.render import render_video


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