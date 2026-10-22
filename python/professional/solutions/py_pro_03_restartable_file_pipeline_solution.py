"""Single-writer, bounded-snapshot restart lab for python-pro-03."""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Callable
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field")
        result[key] = value
    return result


def read_snapshot(source: Path) -> tuple[bytes, list[dict[str, object]]]:
    raw = source.read_bytes()
    records: list[dict[str, object]] = []
    seen: dict[str, int] = {}
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("source must be UTF-8") from exc
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            raise ValueError(f"blank source row {number}")
        try:
            record = json.loads(line, object_pairs_hook=_unique_object)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON at source row {number}") from exc
        if not isinstance(record, dict) or set(record) != {"id", "quantity"}:
            raise ValueError(f"unexpected schema at source row {number}")
        identifier, quantity = record["id"], record["quantity"]
        if not isinstance(identifier, str) or not identifier or identifier != identifier.strip():
            raise ValueError(f"invalid id at source row {number}")
        if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity < 0:
            raise ValueError(f"invalid quantity at source row {number}")
        if identifier in seen and seen[identifier] != quantity:
            raise ValueError(f"conflicting id at source row {number}")
        seen[identifier] = quantity
        records.append(record)
    return raw, records


def state_for_prefix(
    raw: bytes, records: list[dict[str, object]], next_row: object
) -> dict[str, object]:
    if (
        not isinstance(next_row, int)
        or isinstance(next_row, bool)
        or not 0 <= next_row <= len(records)
    ):
        raise ValueError("invalid next_row")
    quantities: dict[str, int] = {}
    for row in records[:next_row]:
        identifier, quantity = row["id"], row["quantity"]
        if not isinstance(identifier, str) or not isinstance(quantity, int):
            raise ValueError("prefix requires validated records")
        quantities[identifier] = quantity
    return {
        "version": 1,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "source_bytes": len(raw),
        "next_row": next_row,
        "quantities": dict(sorted(quantities.items())),
        "total_quantity": sum(quantities.values()),
        "complete": next_row == len(records),
    }


def atomic_write_state(
    path: Path, state: dict[str, object], before_replace: Callable[[], None] | None = None
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            json.dump(state, handle, sort_keys=True, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        if before_replace is not None:
            before_replace()
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def run_pipeline(
    source: Path, checkpoint: Path, batch_size: int = 2, fail_before_commit_at: int | None = None
) -> dict[str, object]:
    if not isinstance(batch_size, int) or isinstance(batch_size, bool) or batch_size <= 0:
        raise ValueError("batch_size must be a positive integer")
    if source.resolve() == checkpoint.resolve():
        raise ValueError("source and checkpoint must differ")
    raw, records = read_snapshot(source)
    state: dict[str, object]
    if checkpoint.exists():
        try:
            loaded = json.loads(
                checkpoint.read_text(encoding="utf-8"), object_pairs_hook=_unique_object
            )
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ValueError("invalid checkpoint encoding or JSON") from exc
        if not isinstance(loaded, dict):
            raise ValueError("checkpoint must be an object")
        expected = state_for_prefix(raw, records, loaded.get("next_row"))
        # Canonical JSON distinguishes booleans from integers and integers from floats.
        if json.dumps(loaded, sort_keys=True) != json.dumps(expected, sort_keys=True):
            raise ValueError("checkpoint does not match this source and prefix")
        state = expected
    else:
        state = state_for_prefix(raw, records, 0)
        atomic_write_state(checkpoint, state)
    raw_offset = state["next_row"]
    assert isinstance(raw_offset, int)
    offset: int = raw_offset
    while offset < len(records):
        offset = min(offset + batch_size, len(records))
        candidate = state_for_prefix(raw, records, offset)

        def before_replace(target_offset: int = offset) -> None:
            if fail_before_commit_at == target_offset:
                raise RuntimeError(f"injected failure before committing row {target_offset}")

        atomic_write_state(checkpoint, candidate, before_replace)
        state = candidate
    return state


if __name__ == "__main__":
    with TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "source.jsonl"
        source.write_text(
            "".join(json.dumps({"id": str(i), "quantity": i}) + "\n" for i in range(5)),
            encoding="utf-8",
        )
        checkpoint = root / "checkpoint.json"
        try:
            run_pipeline(source, checkpoint, fail_before_commit_at=4)
        except RuntimeError:
            assert (
                json.loads(
                    checkpoint.read_text(encoding="utf-8"), object_pairs_hook=_unique_object
                )["next_row"]
                == 2
            )
        result = run_pipeline(source, checkpoint)
        assert (
            result["next_row"] == 5
            and result["total_quantity"] == 10
            and result["complete"] is True
        )
        print(result)
