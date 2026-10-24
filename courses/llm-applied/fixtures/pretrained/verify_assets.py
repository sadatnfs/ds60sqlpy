"""Verify the exact local artifact inventory without loading model code."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any


def verify_assets(directory: Path) -> dict[str, Any]:
    directory = directory.resolve()
    manifest = json.loads((directory / "course-assets.json").read_text())
    if not isinstance(manifest, dict):
        raise ValueError("Asset manifest must be an object")
    contract = json.loads((Path(__file__).parent / "asset_contract.json").read_text())
    for key in ("model_id", "revision", "model_card_license"):
        if manifest.get(key) != contract[key]:
            raise ValueError(f"Pinned asset identity mismatch: {key}")
    files = manifest.get("files")
    if not isinstance(files, dict) or not files:
        raise ValueError("Nonempty asset hash inventory required")
    for relative, expected in files.items():
        if not isinstance(relative, str) or not isinstance(expected, str):
            raise ValueError("Asset paths and hashes must be strings")
        parts = PurePosixPath(relative)
        if parts.is_absolute() or ".." in parts.parts or not parts.parts or "\\" in relative:
            raise ValueError("Unsafe asset path")
        if not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise ValueError("Invalid SHA256 asset hash")
        candidate = directory
        for part in parts.parts:
            candidate = candidate / part
            if candidate.is_symlink():
                raise ValueError("Unsafe asset path")
        if not candidate.resolve().is_relative_to(directory) or not candidate.is_file():
            raise ValueError("Unsafe or missing asset path")
        with candidate.open("rb") as handle:
            actual_hash = hashlib.file_digest(handle, "sha256").hexdigest()
        if actual_hash != expected:
            raise ValueError(f"Asset hash mismatch: {relative}")
    actual_files = {
        path.relative_to(directory).as_posix()
        for path in directory.rglob("*")
        if path.is_file()
        and ".cache" not in path.relative_to(directory).parts
        and path.relative_to(directory).as_posix() != "course-assets.json"
    }
    if actual_files != set(files):
        raise ValueError(
            "Unlisted or missing model artifacts; preserve the exact verified snapshot"
        )
    if not any(name.endswith(".safetensors") for name in files):
        raise ValueError("Safetensors model weights required")
    return dict(manifest)
