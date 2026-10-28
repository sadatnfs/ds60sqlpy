"""One-writer bounded durable records; completed reads never execute or rewrite."""

from __future__ import annotations

import fcntl
import hashlib
import os
import re
import uuid
from pathlib import Path
from typing import Any, BinaryIO

from serving_contract import (
    HASH_PATTERN,
    ID_PATTERN,
    MAX_EVENTS,
    MAX_RECORD,
    MAX_RECORDS,
    TERMINAL,
    ContractError,
    RequestSpec,
    event,
    exact_json,
    finite_number,
    validate_event,
)
from serving_tokenizer import canonical_json


class StoreFull(RuntimeError):
    pass


def validate_record(value: Any, identity: str) -> dict[str, Any]:
    fields = {
        "format",
        "id",
        "request",
        "request_sha256",
        "model_sha256",
        "tokenizer_sha256",
        "created_unix",
        "events",
    }
    if (
        not isinstance(value, dict)
        or set(value) != fields
        or value["format"] != "ds60-inference-record-v1"
        or value["id"] != identity
        or ID_PATTERN.fullmatch(identity) is None
    ):
        raise ContractError("Stored record identity or fields changed")
    spec = RequestSpec.parse(value["request"])
    if value["request_sha256"] != spec.digest:
        raise ContractError("Stored source hash changed")
    for field in ("model_sha256", "tokenizer_sha256"):
        if not isinstance(value[field], str) or HASH_PATTERN.fullmatch(value[field]) is None:
            raise ContractError("Stored model/tokenizer identity is malformed")
    if not finite_number(value["created_unix"], 0, 1e12):
        raise ContractError("Stored timestamp is malformed")
    events = value["events"]
    if not isinstance(events, list) or not 1 <= len(events) <= MAX_EVENTS:
        raise ContractError("Stored event count exceeds its bounds")
    started = False
    token_index = 0
    terminal = False
    for index, item in enumerate(events, 1):
        validate_event(item, index)
        if terminal:
            raise ContractError("Events followed a terminal record")
        kind = item["event"]
        if index == 1 and kind != "queued" or index > 1 and kind == "queued":
            raise ContractError("Admission event is missing or repeated")
        if kind == "started":
            if started or index != 2:
                raise ContractError("Started event is repeated or misplaced")
            started = True
        if kind == "token":
            if (
                not started
                or item["data"]["index"] != token_index
                or token_index >= spec.max_new_tokens
            ):
                raise ContractError("Token sequence exceeds the submitted request")
            token_index += 1
        if kind in TERMINAL:
            if kind == "completed" and not started:
                raise ContractError("Unstarted request claimed completion")
            terminal = True
    return value


def record_bytes(record: dict[str, Any]) -> bytes:
    validate_record(record, record["id"])
    payload = canonical_json(record)
    result = canonical_json({"sha256": hashlib.sha256(payload).hexdigest(), "record": record})
    if len(result) > MAX_RECORD:
        raise ContractError("Stored record exceeds its byte budget")
    return result


def decode_record(raw: bytes, identity: str) -> dict[str, Any]:
    envelope = exact_json(raw, MAX_RECORD)
    if not isinstance(envelope, dict) or set(envelope) != {"sha256", "record"}:
        raise ContractError("Stored envelope is malformed")
    if envelope["sha256"] != hashlib.sha256(canonical_json(envelope["record"])).hexdigest():
        raise ContractError("Stored record checksum mismatch")
    return validate_record(envelope["record"], identity)


class RecordStore:
    """Use one record per request, with atomic snapshots and immutable terminal bytes."""

    def __init__(self, directory: Path, maximum_records: int = MAX_RECORDS) -> None:
        if type(maximum_records) is not int or not 1 <= maximum_records <= MAX_RECORDS:
            raise ValueError("Record count must fit the workshop storage budget")
        if directory.is_symlink():
            raise ValueError("State directory cannot be a symlink")
        directory.mkdir(parents=True, exist_ok=True)
        self.directory = directory
        self.maximum_records = maximum_records
        lock = directory / ".writer.lock"
        descriptor = os.open(lock, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        self.lock_file: BinaryIO = os.fdopen(descriptor, "r+b")
        try:
            fcntl.flock(self.lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            self.lock_file.close()
            raise RuntimeError(
                "Another service process already owns this state; use exactly one worker"
            ) from exc
        self.closed = False

    def close(self) -> None:
        if not self.closed:
            fcntl.flock(self.lock_file, fcntl.LOCK_UN)
            self.lock_file.close()
            self.closed = True

    def path(self, identity: str) -> Path:
        if not isinstance(identity, str) or ID_PATTERN.fullmatch(identity) is None:
            raise ContractError("Unknown request ID")
        return self.directory / (identity + ".json")

    def inventory(self) -> list[str]:
        result: list[str] = []
        unpublished = 0
        for path in self.directory.iterdir():
            if path.name == ".writer.lock":
                continue
            if re.fullmatch(r"\.[0-9a-f]{32}\.[0-9a-f]{32}\.tmp", path.name):
                # A crash may leave an unpublished snapshot. Preserve bounded evidence.
                unpublished += 1
                if (
                    path.is_symlink()
                    or not path.is_file()
                    or path.stat().st_size > MAX_RECORD
                    or unpublished > MAX_RECORDS
                ):
                    raise ContractError("Unpublished recovery files exceed their bounded contract")
                continue
            if (
                path.suffix != ".json"
                or ID_PATTERN.fullmatch(path.stem) is None
                or path.is_symlink()
                or not path.is_file()
            ):
                raise ContractError("Unexpected file in the dedicated inference state directory")
            result.append(path.stem)
        if len(result) > self.maximum_records:
            raise StoreFull("Stored request count exceeds the configured limit")
        return sorted(result)

    def read_raw(self, identity: str) -> bytes:
        path = self.path(identity)
        if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_RECORD:
            raise ContractError("Expected a regular bounded request record")
        raw = path.read_bytes()
        decode_record(raw, identity)
        return raw

    def read(self, identity: str) -> dict[str, Any]:
        return decode_record(self.read_raw(identity), identity)

    def write(self, record: dict[str, Any]) -> None:
        if self.closed:
            raise RuntimeError("Record store is closed")
        raw = record_bytes(record)
        path = self.path(record["id"])
        if path.exists() or path.is_symlink():
            prior_raw = self.read_raw(record["id"])
            prior = decode_record(prior_raw, record["id"])
            if prior["events"][-1]["event"] in TERMINAL:
                if prior_raw != raw:
                    raise ContractError("Terminal records are immutable")
                return
            if {key: value for key, value in prior.items() if key != "events"} != {
                key: value for key, value in record.items() if key != "events"
            } or record["events"][: len(prior["events"])] != prior["events"]:
                raise ContractError("Record update changed its original source or event prefix")
        elif len(self.inventory()) >= self.maximum_records:
            raise StoreFull(
                "History storage is full; archive this owned project before creating more requests"
            )
        temporary = self.directory / f".{record['id']}.{uuid.uuid4().hex}.tmp"
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
            temporary.replace(path)
            directory_fd = os.open(self.directory, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        finally:
            temporary.unlink(missing_ok=True)

    def recover(self) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        keys: set[str] = set()
        for identity in self.inventory():
            record = self.read(identity)
            key = record["request"]["idempotency_key"]
            if key in keys:
                raise ContractError("Duplicate persisted idempotency key")
            keys.add(key)
            if record["events"][-1]["event"] not in TERMINAL:
                text = "".join(
                    item["data"]["text"] for item in record["events"] if item["event"] == "token"
                )
                record["events"].append(
                    event(
                        len(record["events"]) + 1,
                        "error",
                        {
                            "reason": "interrupted_by_restart",
                            "text": text,
                            "metrics": {},
                            "durable": True,
                            "warning": (
                                "Unfinished work was not replayed; "
                                "create a new explicit request to run again."
                            ),
                        },
                    )
                )
                self.write(record)
            result.append(record)
        return result
