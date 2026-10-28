"""Bounded fixture/state handling; no Flink execution is simulated here."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import uuid
from pathlib import Path

ROOT = Path("/state")
SOURCE = Path(__file__).resolve().parent
NAMES = ("orders.csv", "timeline.txt")


def source_identity() -> dict[str, str]:
    result = {}
    for name in NAMES:
        path = SOURCE / "fixtures" / name
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 8192:
            raise ValueError("Invalid fixed source fixture")
        result[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def atomic_json(path: Path, value: object, *, replace: bool = False) -> None:
    if path.parent.is_symlink() or not path.parent.is_dir() or path.is_symlink():
        raise ValueError("Expected a regular owned state path")
    temporary = path.with_name("." + uuid.uuid4().hex + ".pending")
    created = False
    try:
        with temporary.open("x") as handle:
            created = True
            json.dump(value, handle, indent=2, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        if replace:
            temporary.replace(path)
        else:
            path.hardlink_to(temporary)
    finally:
        if created:
            temporary.unlink(missing_ok=True)


def initialize() -> None:
    identity = {"schema_version": 1, "product": "flink-2.3.0", "sources": source_identity()}
    marker = ROOT / "identity.json"
    directories = (
        "input",
        "artifacts",
        "results",
        "receipts",
        "requests",
        "checkpoints",
        "savepoints",
        "logs",
        "history",
    )
    if marker.exists():
        if (
            marker.is_symlink()
            or marker.stat().st_size > 4096
            or json.loads(marker.read_text()) != identity
        ):
            raise ValueError("Retained fixture identity differs; no reset performed")
        if any((ROOT / name).is_symlink() or not (ROOT / name).is_dir() for name in directories):
            raise ValueError("Retained state is incomplete; no reset performed")
        for name, digest in source_identity().items():
            path = ROOT / "input" / name
            if (
                path.is_symlink()
                or not path.is_file()
                or path.stat().st_size > 8192
                or hashlib.sha256(path.read_bytes()).hexdigest() != digest
            ):
                raise ValueError("Retained input bytes differ; no replacement performed")
        return
    if list(ROOT.iterdir()):
        raise ValueError("Unidentified retained state; no reset performed")
    for name in directories:
        (ROOT / name).mkdir(mode=0o700)
    for name in NAMES:
        (ROOT / "input" / name).write_bytes((SOURCE / "fixtures" / name).read_bytes())
    atomic_json(marker, identity)
    for path in [ROOT, *ROOT.rglob("*")]:
        if path.is_symlink():
            raise ValueError("Unexpected initialized symbolic link")
        path.chmod(0o700 if path.is_dir() else 0o600)
        if os.geteuid() == 0:
            os.chown(path, 1000, 1000)


def source_code_identity() -> dict[str, str]:
    files = [
        *sorted((SOURCE / "src").glob("*.java")),
        SOURCE / "binary-image/artifact-lock.json",
        SOURCE / "workshop.py",
        SOURCE / "project_state.py",
        SOURCE / "conf/config.yaml",
        SOURCE / "compose.yaml",
        SOURCE / "start-flink.sh",
        *[SOURCE / "fixtures" / name for name in NAMES],
    ]
    if len(files) > 24 or any(
        path.is_symlink() or not path.is_file() or path.stat().st_size > 100_000 for path in files
    ):
        raise ValueError("Source-code inventory exceeds the fixed project contract")
    return {
        str(path.relative_to(SOURCE)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in files
    }


def result_rows(request: str) -> tuple[list[list[str]], dict[str, str]]:
    if re.fullmatch(r"[a-f0-9]{32}", request) is None:
        raise ValueError("Invalid owned result identity")
    folder = ROOT / "results" / request
    if folder.is_symlink() or not folder.is_dir():
        raise ValueError("Expected owned result directory")
    paths = sorted(
        path
        for path in folder.rglob("*")
        if path.is_file()
        and (path.name.startswith("part-") or path.name == "sql-rows.csv")
        and ".inprogress" not in path.name
    )
    if len(paths) > 128 or any(
        path.is_symlink() or path.stat().st_size > 100_000 for path in paths
    ):
        raise ValueError("Result file bounds exceeded")
    if sum(path.stat().st_size for path in paths) > 384_000:
        raise ValueError("Combined result bytes exceed the fixture budget")
    rows = []
    hashes = {}
    for path in paths:
        rows.extend(list(csv.reader(path.read_text().splitlines())))
        hashes[str(path.relative_to(folder))] = hashlib.sha256(path.read_bytes()).hexdigest()
    if len(rows) > 1000:
        raise ValueError("Result row bound exceeded")
    return rows, hashes


def verify_result(mode: str, rows: list[list[str]]) -> dict[str, object]:
    if mode == "bounded":
        expected = [
            ["update", "east", "1", "4"],
            ["update", "west", "2", "9"],
            ["update", "east", "3", "11"],
        ]
        if sorted(rows) != sorted(expected):
            raise ValueError("Actual source identities, regions or running totals differ")
        return {
            "source_records": 3,
            "final_key_totals": {"east": 11, "west": 9},
            "running_updates": 3,
        }
    if mode == "sql":
        if sorted(rows) != [["east", "11"], ["west", "9"]]:
            raise ValueError("Actual SQL rows differ")
        return {"groups": 2, "final_key_totals": {"east": 11, "west": 9}}
    if mode == "windows":
        expected = [
            ["window", "east", "0", "2000", "2", "11"],
            ["window", "west", "0", "2000", "1", "9"],
            ["window", "east", "2000", "4000", "1", "3"],
            ["late", "east", "4", "1000", "5"],
        ]
        if sorted(rows) != sorted(expected):
            raise ValueError("Actual event-time windows or late output differ")
        return {"windows": 3, "late_ids": [4], "watermark_units": "milliseconds"}
    if mode == "state":
        expected = [
            ["update", "east", "1", "4"],
            ["update", "east", "3", "11"],
            ["update", "west", "2", "9"],
            ["timer", "west", "1000", "9"],
            ["timer", "east", "2000", "11"],
            ["late", "east", "4", "1000", "5"],
            ["update", "east", "5", "3"],
            ["timer", "east", "3000", "3"],
        ]
        if sorted(rows) != sorted(expected):
            raise ValueError("Actual keyed state, timer replacement or cleanup differs")
        return {"updates": 4, "timers": 3, "late_ids": [4], "inactive_state_cleared": True}
    if mode == "pressure":
        if len(rows) != 500 or sorted(int(row[0]) for row in rows) != list(range(500)):
            raise ValueError("Pressure experiment lost or duplicated source IDs")
        return {"source_records": 500, "exact_id_set": True, "artificial_delay_ms": 10}
    if mode == "checkpointed":
        if (
            len(rows) != 100
            or sorted(int(row[0]) for row in rows) != list(range(100))
            or max(int(row[1]) for row in rows) != 5050
        ):
            raise ValueError("Recovered source IDs or managed final sum differ")
        return {"source_records": 100, "exact_id_set": True, "final_total": 5050}
    raise ValueError("Unknown fixed result mode")


if __name__ == "__main__":
    initialize()
