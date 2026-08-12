import re
import subprocess
import uuid
from pathlib import Path


def _detect_silences(input_path: str, noise_db: str = "-35dB", min_duration: float = 1.5):
    """
    Runs ffmpeg's silencedetect and returns a list of (start, end) tuples
    for each detected silent stretch.
    """
    result = subprocess.run(
        [
            "ffmpeg", "-i", input_path,
            "-af", f"silencedetect=noise={noise_db}:d={min_duration}",
            "-f", "null", "-",
        ],
        capture_output=True,
        text=True,
    )

    log = result.stderr  # ffmpeg writes this info to stderr, not stdout
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]

    return list(zip(starts, ends))


def remove_silences(input_path: str, output_dir: str, noise_db: str = "-35dB", min_duration: float = 1.5) -> str:
    """
    Removes silent stretches from a video, keeping only the parts where
    someone is actually talking. Returns the path to the trimmed file.
    """
    silences = _detect_silences(input_path, noise_db, min_duration)

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_path = Path(output_dir) / f"{uuid.uuid4()}_nosilence.mp4"

    if not silences:
        # Nothing to cut — just copy the file through untouched.
        subprocess.run(["ffmpeg", "-y", "-i", input_path, "-c", "copy", str(output_path)], check=True)
        return str(output_path)

    # Build the list of "keep" segments — the gaps BETWEEN silences.
    keep_segments = []
    cursor = 0.0
    for start, end in silences:
        if start > cursor:
            keep_segments.append((cursor, start))
        cursor = end
    keep_segments.append((cursor, None))  # from the last silence to the end of the video

    # Build an ffmpeg filter that trims each "keep" segment and glues them back together.
    filter_parts = []
    concat_inputs = ""
    for i, (seg_start, seg_end) in enumerate(keep_segments):
        if seg_end is None:
            trim = f"[0:v]trim=start={seg_start},setpts=PTS-STARTPTS[v{i}];[0:a]atrim=start={seg_start},asetpts=PTS-STARTPTS[a{i}]"
        else:
            trim = f"[0:v]trim=start={seg_start}:end={seg_end},setpts=PTS-STARTPTS[v{i}];[0:a]atrim=start={seg_start}:end={seg_end},asetpts=PTS-STARTPTS[a{i}]"
        filter_parts.append(trim)
        concat_inputs += f"[v{i}][a{i}]"

    filter_complex = ";".join(filter_parts) + f";{concat_inputs}concat=n={len(keep_segments)}:v=1:a=1[outv][outa]"

    subprocess.run(
        [
            "ffmpeg", "-y", "-i", input_path,
            "-filter_complex", filter_complex,
            "-map", "[outv]", "-map", "[outa]",
            "-c:v", "libx264", "-c:a", "aac",
            str(output_path),
        ],
        check=True,
        capture_output=True,
    )

    return str(output_path)