"""Owned local service contracts and safe JSON model inference."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path

STATE = Path(os.environ.get("DS60_STATE_DIR", "/state"))
FEATURES = ["usage", "tickets", "north"]


def decode_document(raw: bytes) -> dict:
    if len(raw) > 200_000:
        raise ValueError("State document exceeds its bound")
    value = json.loads(raw, parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)))
    if not isinstance(value, dict):
        raise ValueError("State document must be an object")
    return value


def bounded_bytes(path: Path) -> bytes:
    with path.open("rb") as stream:
        raw = stream.read(200_001)
    if len(raw) > 200_000:
        raise ValueError("State document exceeds its bound")
    return raw


def read_json(path: Path) -> dict:
    return decode_document(bounded_bytes(path))


def ownership() -> str:
    marker = read_json(STATE / "owner.json")
    expected = os.environ.get("DS60_WORKSHOP_OWNER", "")
    if not expected or marker.get("owner") != expected:
        raise ValueError("Workshop state ownership mismatch")
    return expected


def validate_model(model: dict, version: str) -> None:
    if (
        model.get("features") != FEATURES
        or model.get("version") != version
        or model.get("feature_schema") != "customer-v1"
    ):
        raise ValueError("Model contract mismatch")
    for key in ("mean", "scale", "coefficients"):
        values = model.get(key)
        if (
            not isinstance(values, list)
            or len(values) != len(FEATURES)
            or not all(type(x) in (int, float) and math.isfinite(x) for x in values)
        ):
            raise ValueError("Invalid numeric model state")
    if not all(x > 0 for x in model["scale"]):
        raise ValueError("Invalid model scaling")
    if type(model.get("intercept")) not in (int, float) or not math.isfinite(model["intercept"]):
        raise ValueError("Invalid model intercept")
    if model.get("approved_for_local_demo") is not True:
        raise ValueError("Model has no accepted local validation decision")


def model_bytes(version: str) -> tuple[bytes, dict]:
    if re.fullmatch(r"v[1-9][0-9]*", version) is None:
        raise ValueError("Invalid model version")
    path = STATE / "models" / version / "model.json"
    raw = bounded_bytes(path)
    model = decode_document(raw)
    validate_model(model, version)
    return raw, model


def load_model() -> tuple[dict, dict]:
    ownership()
    pointer = read_json(STATE / "current.json")
    version = pointer.get("version", "")
    if not isinstance(version, str):
        raise ValueError("Invalid model version")
    raw, model = model_bytes(version)
    if hashlib.sha256(raw).hexdigest() != pointer.get("sha256"):
        raise ValueError("Model integrity check failed")
    return pointer, model


def probability(model: dict, feature: dict) -> float:
    usage, tickets, region = feature["usage"], feature["tickets"], feature["region"]
    if not all(type(x) in (int, float) and math.isfinite(x) for x in (usage, tickets)):
        raise ValueError("Features must be finite")
    if not 0 <= usage <= 10_000 or not 0 <= tickets <= 100 or region not in {"north", "south"}:
        raise ValueError("Feature domain mismatch")
    values = [usage, tickets, float(region == "north")]
    z = float(model["intercept"]) + sum(
        (value - mean) / scale * weight
        for value, mean, scale, weight in zip(
            values, model["mean"], model["scale"], model["coefficients"], strict=True
        )
    )
    if not math.isfinite(z):
        raise ValueError("Non-finite inference")
    return 1 / (1 + math.exp(-z)) if z >= 0 else math.exp(z) / (1 + math.exp(z))


def activate(version: str) -> dict:
    ownership()
    if re.fullmatch(r"v[1-9][0-9]*", version) is None:
        raise ValueError("Invalid version")
    raw, _ = model_bytes(version)
    pointer = {"version": version, "sha256": hashlib.sha256(raw).hexdigest()}
    temporary = STATE / "current.pending"
    temporary.write_text(json.dumps(pointer, sort_keys=True), "utf-8")
    temporary.replace(STATE / "current.json")
    load_model()
    return pointer
