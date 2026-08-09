import subprocess
import uuid
from pathlib import Path

MODEL_PATH = Path("models/en_US-lessac-medium.onnx")


def generate_voice(text: str, output_dir: str) -> str:
    """
    Turns text into a .wav file using Piper, saved inside output_dir.
    Returns the path to the generated file.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_path = Path(output_dir) / f"{uuid.uuid4()}_voice.wav"

    subprocess.run(
        ["piper", "--model", str(MODEL_PATH), "--output_file", str(output_path)],
        input=text.encode("utf-8"),
        check=True,
    )

    return str(output_path)