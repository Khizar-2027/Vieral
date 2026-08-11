import subprocess
import uuid
from pathlib import Path


def trim_video(input_path: str, start: float, duration: float, output_dir: str) -> str:
    """
    Trims a video to [start, start+duration] seconds, frame-accurate (re-encoded).
    Returns the path to the trimmed file.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_path = Path(output_dir) / f"{uuid.uuid4()}_trimmed.mp4"

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i", input_path,
            "-ss", str(start),
            "-t", str(duration),
            "-c:v", "libx264",
            "-c:a", "aac",
            str(output_path),
        ],
        check=True,
        capture_output=True,
    )

    return str(output_path)