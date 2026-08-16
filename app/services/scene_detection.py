import re
import statistics
import subprocess


def _get_scene_scores(input_path: str) -> list[tuple[float, float]]:
    """
    Runs ffmpeg and returns a list of (timestamp, scene_score) for every frame.
    scene_score is how visually different this frame is from the previous one.
    """
    result = subprocess.run(
        [
            "ffmpeg", "-i", input_path,
            "-vf", "select='gte(scene,0)',metadata=print:key=lavfi.scene_score",
            "-f", "null", "-",
        ],
        capture_output=True,
        text=True,
    )

    log = result.stderr
    # showinfo's metadata print interleaves frame info and score lines;
    # we only need pts_time (timestamp) and the score that follows it.
    timestamps = [float(x) for x in re.findall(r"pts_time:([\d.]+)", log)]
    scores = [float(x) for x in re.findall(r"scene_score=([\d.]+)", log)]

    return list(zip(timestamps, scores))


def detect_cuts(input_path: str, min_gap: float = 0.3, absolute_floor: float = 0.1) -> list[float]:
    frames = _get_scene_scores(input_path)

    if len(frames) < 2:
        return []

    scores = [score for _, score in frames]
    mean = statistics.mean(scores)
    stdev = statistics.stdev(scores) if len(scores) > 1 else 0.0

    adaptive_threshold = mean + (4 * stdev)
    # A real cut must clear BOTH bars: stand out from this video's own
    # baseline, AND be a meaningfully large change in absolute terms.
    threshold = max(adaptive_threshold, absolute_floor)

    raw_cuts = [ts for ts, score in frames if score > threshold]
    raw_cuts = [ts for ts in raw_cuts if ts > 0.5]

    clean_cuts = []
    for ts in raw_cuts:
        if not clean_cuts or ts - clean_cuts[-1] > min_gap:
            clean_cuts.append(ts)

    return clean_cuts