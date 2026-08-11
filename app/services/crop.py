import subprocess
import uuid
from pathlib import Path


def crop_to_vertical(input_path: str, output_dir: str) -> str:
    """
    Crops/resizes a video to 9:16 vertical (1080x1920), centered.
    Returns the path to the cropped file.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_path = Path(output_dir) / f"{uuid.uuid4()}_cropped.mp4"

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i", input_path,
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
            "-c:a", "copy",
            str(output_path),
        ],
        check=True,
        capture_output=True,
    )

    return str(output_path)