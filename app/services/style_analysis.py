from app.services.scene_detection import detect_cuts
from app.services.captions import _transcribe, calculate_pacing


def analyze_video_style(video_path: str) -> dict:
    """
    Analyzes a video's editing style: cut frequency + speaking pace.
    Transcribes the video's audio exactly once, sharing that result
    across both signals instead of duplicating the (slow) Whisper call.
    """
    cuts = detect_cuts(video_path)
    segments = _transcribe(video_path)
    pacing = calculate_pacing(video_path, segments=segments)

    return {
        "cut_count": len(cuts),
        "cut_timestamps": cuts,
        "overall_wpm": pacing["overall_wpm"],
        "pacing_segments": pacing["segments"],
    }