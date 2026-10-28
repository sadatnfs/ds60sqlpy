"""Strict request and event contracts, independent of HTTP and model execution."""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import asdict, dataclass
from typing import Any

from serving_tokenizer import Tokenizer, canonical_json

ID_PATTERN = re.compile(r"[0-9a-f]{32}")
KEY_PATTERN = re.compile(r"[A-Za-z0-9_-]{8,80}")
HASH_PATTERN = re.compile(r"[0-9a-f]{64}")
MAX_BODY = 8000
MAX_RECORD = 160_000
MAX_RECORDS = 128
MAX_EVENTS = 100
MAX_EVENT_BYTES = 8000
MAX_TERMINAL_EVENT_BYTES = 32768
TERMINAL = frozenset({"completed", "cancelled", "error"})
EVENT_KINDS = TERMINAL | {"queued", "started", "token"}


class ContractError(ValueError):
    """A bounded request, event or stored document violates its contract."""


def finite_number(value: Any, low: float, high: float) -> bool:
    if type(value) is int:
        return low <= value <= high
    return type(value) is float and math.isfinite(value) and low <= value <= high


def exact_json(data: bytes, maximum: int = MAX_BODY) -> Any:
    if len(data) > maximum:
        raise ContractError("JSON exceeds the byte budget")

    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ContractError("Duplicate JSON field")
            result[key] = value
        return result

    def invalid(value: str) -> Any:
        raise ContractError("Nonfinite JSON number")

    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=pairs, parse_constant=invalid)
    except ContractError:
        raise
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise ContractError("Expected bounded UTF-8 JSON") from exc


@dataclass(frozen=True)
class RequestSpec:
    prompt: str
    max_new_tokens: int
    temperature: float
    top_k: int
    seed: int
    stops: tuple[str, ...]
    idempotency_key: str

    @classmethod
    def parse(cls, value: Any) -> RequestSpec:
        fields = {
            "prompt",
            "max_new_tokens",
            "temperature",
            "top_k",
            "seed",
            "stops",
            "idempotency_key",
        }
        if not isinstance(value, dict) or set(value) != fields:
            raise ContractError(
                "Supply exactly prompt, max_new_tokens, temperature, top_k, seed, "
                "stops and idempotency_key"
            )
        prompt = value["prompt"]
        try:
            if not isinstance(prompt, str) or not 1 <= len(prompt.encode("utf-8")) <= 2048:
                raise ContractError("Prompt must contain 1 through 2048 UTF-8 bytes")
        except UnicodeError as exc:
            raise ContractError("Prompt contains an invalid Unicode surrogate") from exc
        if any(ord(char) < 32 and char not in "\n\t" for char in prompt) or "\x7f" in prompt:
            raise ContractError("Prompt contains unsupported control characters")
        if type(value["max_new_tokens"]) is not int or not 1 <= value["max_new_tokens"] <= 64:
            raise ContractError("Choose 1 through 64 new tokens")
        temperature = value["temperature"]
        if not finite_number(temperature, 0, 2) or 0 < temperature < 0.05:
            raise ContractError("Temperature must be zero or 0.05 through 2")
        if type(value["top_k"]) is not int or not 1 <= value["top_k"] <= 64:
            raise ContractError("Choose top_k from 1 through 64")
        if type(value["seed"]) is not int or not 0 <= value["seed"] <= 2**31 - 1:
            raise ContractError("Seed must be an integer from zero through 2147483647")
        stops = value["stops"]
        if (
            not isinstance(stops, list)
            or len(stops) > 4
            or any(not isinstance(stop, str) or not 1 <= len(stop) <= 32 for stop in stops)
        ):
            raise ContractError("Use at most four bounded nonempty stop strings")
        if len(set(stops)) != len(stops):
            raise ContractError("Stop strings must be distinct")
        try:
            if any(
                len(stop.encode("utf-8")) > 128 or any(ord(char) < 32 for char in stop)
                for stop in stops
            ):
                raise ContractError("Stop strings must be printable bounded UTF-8")
        except UnicodeError as exc:
            raise ContractError("Stop string contains an invalid Unicode surrogate") from exc
        key = value["idempotency_key"]
        if not isinstance(key, str) or KEY_PATTERN.fullmatch(key) is None:
            raise ContractError(
                "Idempotency key needs 8 through 80 letters, digits, underscores or hyphens"
            )
        return cls(
            prompt,
            value["max_new_tokens"],
            float(temperature),
            value["top_k"],
            value["seed"],
            tuple(stops),
            key,
        )

    def record(self) -> dict[str, Any]:
        result = asdict(self)
        result["stops"] = list(self.stops)
        return result

    @property
    def digest(self) -> str:
        return hashlib.sha256(canonical_json(self.record())).hexdigest()

    def admit(self, tokenizer: Tokenizer, context: int) -> list[int]:
        tokens = tokenizer.encode(self.prompt, add_bos=True)
        if len(tokens) + self.max_new_tokens > context:
            raise ContractError(
                f"Prompt has {len(tokens)} tokens including BOS; "
                f"prompt plus requested output exceeds context {context}"
            )
        return tokens


def event(identity: int, kind: str, data: dict[str, Any]) -> dict[str, Any]:
    value = {"id": identity, "event": kind, "data": data}
    validate_event(value, identity)
    return value


def validate_event(value: Any, expected_id: int) -> None:
    if (
        not isinstance(value, dict)
        or set(value) != {"id", "event", "data"}
        or type(value["id"]) is not int
        or value["id"] != expected_id
        or not isinstance(value["event"], str)
        or value["event"] not in EVENT_KINDS
        or not isinstance(value["data"], dict)
    ):
        raise ContractError("Malformed or nonsequential event")
    # A terminal repeats up to64decoded64-byte pieces. ASCII JSON escaping
    # can expand that text sixfold; ordinary per-token events stay tightly bounded.
    budget = MAX_TERMINAL_EVENT_BYTES if value["event"] in TERMINAL else MAX_EVENT_BYTES
    if len(canonical_json(value)) > budget:
        raise ContractError("Event exceeds its byte budget")
    data = value["data"]
    kind = value["event"]
    if kind == "queued":
        if set(data) != {"prompt_tokens", "reserved_tokens"} or any(
            type(item) is not int or not 1 <= item <= 256 for item in data.values()
        ):
            raise ContractError("Malformed admission event")
    elif kind == "started":
        if (
            set(data) != {"queue_seconds", "device"}
            or not finite_number(data["queue_seconds"], 0, 1e9)
            or data["device"] not in {"cpu", "cuda:0"}
        ):
            raise ContractError("Malformed start event")
    elif kind == "token":
        if set(data) != {"index", "token_id", "bytes_hex", "text", "compute_seconds"}:
            raise ContractError("Malformed token event fields")
        if (
            type(data["index"]) is not int
            or not 0 <= data["index"] < 64
            or type(data["token_id"]) is not int
            or not 0 <= data["token_id"] < 322
        ):
            raise ContractError("Malformed token identity")
        if (
            not isinstance(data["bytes_hex"], str)
            or re.fullmatch(r"(?:[0-9a-f]{2}){0,64}", data["bytes_hex"]) is None
            or not isinstance(data["text"], str)
            or len(data["text"]) > 128
            or not finite_number(data["compute_seconds"], 0, 1e6)
        ):
            raise ContractError("Malformed token payload")
    else:
        if (
            set(data) != {"reason", "text", "metrics", "durable", "warning"}
            or not isinstance(data["reason"], str)
            or len(data["reason"]) > 80
            or not isinstance(data["text"], str)
            or len(data["text"]) > 8192
            or type(data["durable"]) is not bool
            or not isinstance(data["warning"], str)
            or len(data["warning"]) > 200
        ):
            raise ContractError("Malformed terminal event")
        metrics = data["metrics"]
        if (
            not isinstance(metrics, dict)
            or len(metrics) > 24
            or any(
                not isinstance(key, str) or len(key) > 64 or not finite_number(item, 0, 1e9)
                for key, item in metrics.items()
            )
        ):
            raise ContractError("Malformed terminal metrics")


def sse_frame(value: dict[str, Any]) -> bytes:
    validate_event(value, value["id"])
    payload = canonical_json(value["data"]).decode().rstrip("\n")
    return f"id: {value['id']}\nevent: {value['event']}\ndata: {payload}\n\n".encode()
