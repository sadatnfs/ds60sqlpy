"""Verify local pinned artifacts using only standard-library reads."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path


def verify_assets(directory: Path) -> dict:
    directory = directory.resolve()
    manifest = json.loads((directory / 'course-assets.json').read_text())
    contract = json.loads((Path(__file__).parent / 'asset_contract.json').read_text())
    for key in ('model_id', 'revision', 'model_card_license'):
        if manifest.get(key) != contract[key]:
            raise ValueError(f'Pinned asset identity mismatch: {key}')
    files = manifest.get('files')
    if not isinstance(files, dict) or not files:
        raise ValueError('Nonempty asset hash inventory required')
    for relative, expected in files.items():
        candidate = directory / relative
        if candidate.is_symlink() or not candidate.resolve().is_relative_to(directory):
            raise ValueError('Unsafe asset path')
        if not candidate.is_file() or hashlib.sha256(candidate.read_bytes()).hexdigest() != expected:
            raise ValueError(f'Asset hash mismatch: {relative}')
    if not any(name.endswith('.safetensors') for name in files):
        raise ValueError('Safetensors model weights required')
    return manifest
