import subprocess
import uuid
from pathlib import Path


def render_video(background_path: str, voice_path: str, captions_path: str, output_dir: str) -> str:
    """
    Combines a background video, a voice track, and burned-in captions
    into one final .mp4. Returns the path to the rendered file.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_path = Path(output_dir) / f"{uuid.uuid4()}_output.mp4"

    # FFmpeg needs forward slashes even on Windows for the subtitles filter,
    # and the path can't contain a raw ':' from a drive letter without escaping.
    captions_for_filter = captions_path.replace("\\", "/").replace(":", "\\:")

    subprocess.run(
        [
            "ffmpeg",
            "-y",  # overwrite output if it already exists
            "-i", background_path,
            "-i", voice_path,
            "-vf", f"subtitles={captions_for_filter}",
            "-map", "0:v",
            "-map", "1:a",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-shortest",
            str(output_path),
        ],
        check=True,
        capture_output=True,
    )

    return str(output_path)