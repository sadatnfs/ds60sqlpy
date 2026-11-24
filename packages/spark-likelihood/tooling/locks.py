# SPDX-License-Identifier: Apache-2.0
"""Read the package's exact hashed preparation locks without resolving dependencies."""

from __future__ import annotations

import importlib.metadata
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
ENTRY = re.compile(r"([A-Za-z0-9_.-]+)==([A-Za-z0-9.+!-]+)\s+((?:--hash=sha256:[0-9a-f]{64}\s*)+)")


def normalized_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def read_lock(path: Path) -> dict[str, str]:
    pending = ""
    records = {}
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        continued = line.endswith("\\")
        pending += " " + (line[:-1].strip() if continued else line)
        if continued:
            continue
        match = ENTRY.fullmatch(pending.strip())
        if match is None:
            raise ValueError(f"Require an exact version and SHA256 hashes in {path.name}")
        name, version = normalized_name(match[1]), match[2]
        if name in records:
            raise ValueError(f"Duplicate dependency in {path.name}: {name}")
        records[name] = version
        pending = ""
    if pending or not records:
        raise ValueError(f"Incomplete or empty lock: {path.name}")
    return records


def selected_lock(group: str, architecture: str) -> Path:
    if architecture not in {"arm64", "amd64"}:
        raise ValueError("Only native Linux ARM64 and AMD64 preparation is supported")
    names = {
        "cpu": f"torch.{architecture}.lock",
        "scientific": "scientific.lock",
        "build": "build.lock",
    }
    if group not in names:
        raise ValueError("Unknown preparation lock group")
    return BASE / "locks" / names[group]


PYPI_INDEX = "https://pypi.org/simple"
TORCH_CPU_PAGE = "https://download.pytorch.org/whl/cpu/torch/"


def index_arguments(group: str) -> list[str]:
    """Return pip source flags. The PyTorch page serves only the +cpu torch wheels.

    The PyTorch index lags PyPI for the other locked packages, so every group resolves
    from PyPI and the cpu group adds the PyTorch torch page; hashes still pin each file.
    """
    arguments = ["--index-url", PYPI_INDEX]
    if group == "cpu":
        arguments += ["--find-links", TORCH_CPU_PAGE]
    return arguments


def check_versions(path: Path) -> dict[str, str]:
    expected = read_lock(path)
    for name, version in expected.items():
        try:
            actual = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            raise ValueError(f"Missing prepared dependency: {name}=={version}") from None
        if actual != version:
            raise ValueError(
                f"Prepared dependency differs: {name} expected {version}, got {actual}"
            )
    return expected
