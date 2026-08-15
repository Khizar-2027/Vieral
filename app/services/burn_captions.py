import subprocess
import uuid
from pathlib import Path

FONTS_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"


def burn_captions(video_path: str, captions_path: str, output_dir: str) -> str:
    """
    Burns captions onto a video, keeping the video's own existing audio track.
    Returns the path to the final file.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_path = Path(output_dir) / f"{uuid.uuid4()}_final.mp4"

    captions_for_filter = captions_path.replace("\\", "/").replace(":", "\\:")
    fonts_dir_for_filter = str(FONTS_DIR).replace("\\", "/").replace(":", "\\:")

    style = (
        "FontName=Bebas Neue,"
        "FontSize=14,"
        "PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H00000000,"
        "BorderStyle=1,"
        "Outline=1.5,"
        "Shadow=0,"
        "MarginV=80"
    )

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-vf", f"subtitles={captions_for_filter}:force_style='{style}':fontsdir='{fonts_dir_for_filter}'",
            "-c:v", "libx264",
            "-c:a", "copy",
            str(output_path),
        ],
        check=True,
        capture_output=True,
    )

    return str(output_path)