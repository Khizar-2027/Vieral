import subprocess
import uuid
from pathlib import Path


def burn_captions(video_path: str, captions_path: str, output_dir: str) -> str:
    """
    Burns captions onto a video, keeping the video's own existing audio track.
    Returns the path to the final file.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_path = Path(output_dir) / f"{uuid.uuid4()}_final.mp4"

    captions_for_filter = captions_path.replace("\\", "/").replace(":", "\\:")

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-vf", f"subtitles={captions_for_filter}",
            "-c:v", "libx264",
            "-c:a", "copy",
            str(output_path),
        ],
        check=True,
        capture_output=True,
    )

    return str(output_path)