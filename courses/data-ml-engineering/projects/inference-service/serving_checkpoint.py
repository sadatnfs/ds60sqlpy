"""Bounded, hash-bound NPZ checkpoints without pickle or archive extraction."""

from __future__ import annotations

import hashlib
import io
import json
import math
import zipfile
from pathlib import Path
from typing import Any

import numpy as np
from serving_model import ModelConfig, TinyTransformer
from serving_tokenizer import Tokenizer, canonical_json

MAX_WEIGHTS_BYTES = 8_000_000
MAX_JSON_BYTES = 64_000


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON field")
        result[key] = value
    return result


def json_bytes(data: bytes, maximum: int = MAX_JSON_BYTES) -> Any:
    if len(data) > maximum:
        raise ValueError("JSON document exceeds its byte budget")
    return json.loads(
        data.decode("utf-8"),
        object_pairs_hook=unique_object,
        parse_constant=lambda value: (_ for _ in ()).throw(ValueError("Nonfinite JSON")),
    )


def regular_bytes(path: Path, maximum: int) -> bytes:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > maximum:
        raise ValueError("Expected a regular bounded checkpoint file")
    data = path.read_bytes()
    if len(data) > maximum:
        raise ValueError("Checkpoint grew beyond its byte budget")
    return data


def save_checkpoint(
    directory: Path, model: TinyTransformer, tokenizer: Tokenizer, training: dict[str, Any]
) -> dict[str, Any]:
    if directory.exists() or directory.is_symlink():
        raise ValueError("Existing model assets are never overwritten")
    directory.mkdir(parents=True)
    arrays = {
        name: value.detach().cpu().numpy().astype(np.float32, copy=False)
        for name, value in model.state().items()
    }
    buffer = io.BytesIO()
    np.savez_compressed(buffer, **arrays)
    weights = buffer.getvalue()
    if len(weights) > MAX_WEIGHTS_BYTES:
        raise ValueError("Prepared checkpoint exceeds the model budget")
    tokenizer_data = canonical_json(tokenizer.record())
    (directory / "weights.npz").write_bytes(weights)
    (directory / "tokenizer.json").write_bytes(tokenizer_data)
    manifest = {
        "format": "ds60-tiny-transformer-v1",
        "model_config": model.config.__dict__,
        "parameter_count": model.parameter_count,
        "files": {"weights.npz": sha256(weights), "tokenizer.json": sha256(tokenizer_data)},
        "training": training,
        "claim": "Locally trained synthetic mechanism; no pretrained-model capability claim",
    }
    manifest_data = canonical_json(manifest)
    if len(manifest_data) > MAX_JSON_BYTES:
        raise ValueError("Checkpoint manifest exceeds its byte budget")
    (directory / "manifest.json").write_bytes(manifest_data)
    return manifest


def load_checkpoint(directory: Path) -> tuple[TinyTransformer, Tokenizer, dict[str, Any]]:
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("Model assets must be an owned directory")
    raw = regular_bytes(directory / "manifest.json", MAX_JSON_BYTES)
    manifest = json_bytes(raw)
    if (
        not isinstance(manifest, dict)
        or set(manifest)
        != {"format", "model_config", "parameter_count", "files", "training", "claim"}
        or manifest["format"] != "ds60-tiny-transformer-v1"
    ):
        raise ValueError("Unknown checkpoint manifest format")
    config = ModelConfig.from_record(manifest["model_config"])
    files = manifest["files"]
    if not isinstance(files, dict) or set(files) != {"weights.npz", "tokenizer.json"}:
        raise ValueError("Checkpoint manifest must name exactly its fixed files")
    weights = regular_bytes(directory / "weights.npz", MAX_WEIGHTS_BYTES)
    tokens = regular_bytes(directory / "tokenizer.json", MAX_JSON_BYTES)
    if files != {"weights.npz": sha256(weights), "tokenizer.json": sha256(tokens)}:
        raise ValueError("Checkpoint hash mismatch")
    tokenizer = Tokenizer.from_record(json_bytes(tokens))
    if tokenizer.vocab_size != config.vocab_size:
        raise ValueError("Tokenizer vocabulary and checkpoint disagree")
    model = TinyTransformer(config)
    expected = model.state()
    if (
        type(manifest["parameter_count"]) is not int
        or manifest["parameter_count"] != model.parameter_count
    ):
        raise ValueError("Checkpoint parameter count changed")
    names = {name + ".npy" for name in expected}
    with zipfile.ZipFile(io.BytesIO(weights)) as archive:
        members = archive.infolist()
        if len(members) != len(names) or {item.filename for item in members} != names:
            raise ValueError("Checkpoint members differ from the exact parameter set")
        if sum(item.file_size for item in members) > MAX_WEIGHTS_BYTES:
            raise ValueError("Uncompressed checkpoint exceeds its byte budget")
        for item in members:
            if item.is_dir() or item.file_size > MAX_WEIGHTS_BYTES:
                raise ValueError("Invalid checkpoint member")
            with archive.open(item) as stream:
                version = np.lib.format.read_magic(stream)
                if version == (1, 0):
                    shape, fortran, dtype = np.lib.format.read_array_header_1_0(stream)
                elif version == (2, 0):
                    shape, fortran, dtype = np.lib.format.read_array_header_2_0(stream)
                else:
                    raise ValueError("Unsupported array format")
                target = expected[item.filename[:-4]]
                if (
                    any(type(size) is not int or size < 0 for size in shape)
                    or tuple(shape) != tuple(target.shape)
                    or fortran
                    or dtype != np.dtype("float32")
                    or dtype.hasobject
                    or math.prod(shape) * dtype.itemsize != item.file_size - stream.tell()
                ):
                    raise ValueError("Checkpoint array shape or dtype changed")
    with np.load(io.BytesIO(weights), allow_pickle=False) as archive:
        state = {}
        for name, target in expected.items():
            array = archive[name]
            if (
                array.shape != tuple(target.shape)
                or array.dtype != np.float32
                or not np.isfinite(array).all()
            ):
                raise ValueError("Checkpoint needs finite exact-shape float32 arrays")
            state[name] = model.torch.from_numpy(array.copy())
        model.parts.load_state_dict(state, strict=True)
    model.eval()
    return model, tokenizer, {**manifest, "manifest_sha256": sha256(raw)}


def verify_cache(model: TinyTransformer, tokenizer: Tokenizer) -> dict[str, float]:
    torch = model.torch
    tokens = tokenizer.encode("A model learns from data.", add_bos=True)
    tokens = tokens[: min(16, model.config.context - 3)]
    whole = torch.tensor([tokens], dtype=torch.long, device=model.parts["token"].weight.device)
    full, _ = model.prefill(whole)
    first, cache = model.prefill(whole[:, :1])
    pieces = [first]
    for position in range(1, len(tokens)):
        logits, cache = model.decode(whole[:, position : position + 1], cache)
        pieces.append(logits)
    cached = torch.cat(pieces, dim=1)
    error = float((full - cached).abs().max().item())
    if error > 2e-5:
        raise ValueError("Cached logits differ from full-prefix inference")
    changed = whole.clone()
    changed[0, -1] = (int(changed[0, -1]) + 1) % model.config.vocab_size
    alternate, _ = model.prefill(changed)
    causal_error = float((full[:, :-1] - alternate[:, :-1]).abs().max().item())
    if causal_error > 2e-5:
        raise ValueError("Future-token perturbation changed earlier causal logits")
    return {"cached_full_max_error": error, "causal_prefix_max_error": causal_error}
