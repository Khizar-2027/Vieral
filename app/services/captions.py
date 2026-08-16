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

def _transcribe(audio_path: str) -> list:
    """
    Runs Whisper once and returns the segments as a list (not a generator,
    since generators can only be consumed once — we need to reuse this
    data for both captions and pacing).
    """
    segments, _ = _model.transcribe(audio_path)
    return list(segments)

def generate_captions(audio_path: str, output_dir: str, segments: list | None = None) -> str:
    """
    Transcribes audio_path (unless segments are already provided) and
    writes an .srt subtitle file into output_dir.
    """
    if segments is None:
        segments = _transcribe(audio_path)

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_path = Path(output_dir) / f"{uuid.uuid4()}_captions.srt"

    with open(output_path, "w", encoding="utf-8") as f:
        for i, segment in enumerate(segments, start=1):
            start = _format_timestamp(segment.start)
            end = _format_timestamp(segment.end)
            text = segment.text.strip()
            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")

    return str(output_path)


def calculate_pacing(audio_path: str, segments: list | None = None) -> dict:
    """
    Calculates speaking pace (words per minute), either from provided
    segments or by transcribing audio_path if none are given.
    """
    if segments is None:
        segments = _transcribe(audio_path)

    segment_data = []
    total_words = 0
    total_duration = 0.0

    for segment in segments:
        word_count = len(segment.text.strip().split())
        duration = segment.end - segment.start
        wpm = (word_count / duration) * 60 if duration > 0 else 0

        segment_data.append({
            "start": segment.start,
            "end": segment.end,
            "word_count": word_count,
            "wpm": round(wpm, 1),
        })

        total_words += word_count
        total_duration += duration

    overall_wpm = (total_words / total_duration) * 60 if total_duration > 0 else 0

    return {
        "overall_wpm": round(overall_wpm, 1),
        "segments": segment_data,
    }