"""Read canonical, standalone and formatter-normalized CUDA lesson sources."""

from __future__ import annotations

import json
from pathlib import Path


def _programs() -> dict:
    return json.loads(Path(__file__).with_name("cpp_gpu_programs.json").read_text(encoding="utf-8"))


def references() -> dict[int, str]:
    return {int(number): entry["reference"] for number, entry in _programs().items()}


def starter(number: int) -> str:
    return _programs()[str(number)]["starter"]
