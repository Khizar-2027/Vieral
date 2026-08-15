import uuid
from pathlib import Path

from faster_whisper import WhisperModel

_model = WhisperModel("small", device="cpu", compute_type="int8")

def _format_timestamp(seconds: float) -> str:
    """Converts seconds into SRT's HH:MM:SS,mmm format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def generate_captions(audio_path: str, output_dir: str) -> str:
    """
    Transcribes audio_path and writes an .srt subtitle file into output_dir.
    Returns the path to the generated .srt file.
    """
    segments, _ = _model.transcribe(audio_path)

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_path = Path(output_dir) / f"{uuid.uuid4()}_captions.srt"

    with open(output_path, "w", encoding="utf-8") as f:
        for i, segment in enumerate(segments, start=1):
            start = _format_timestamp(segment.start)
            end = _format_timestamp(segment.end)
            text = segment.text.strip()
            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")

    return str(output_path)