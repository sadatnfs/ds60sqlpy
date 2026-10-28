"""Pure bounded data operations, independent of the orchestration SDK."""

from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path("/state")
DAYS = ("2026-01-01", "2026-01-02")
SOURCE = [
    {"id": 1, "day": DAYS[0], "region": "east", "amount": 4},
    {"id": 2, "day": DAYS[0], "region": "west", "amount": 9},
    {"id": 3, "day": DAYS[1], "region": "east", "amount": 7},
]


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def atomic(path: Path, value: object) -> None:
    if path.is_symlink() or path.parent.is_symlink() or not path.parent.is_dir():
        raise ValueError("Expected regular owned output path")
    temporary = path.with_name("." + uuid.uuid4().hex + ".tmp")
    try:
        with temporary.open("xb") as handle:
            handle.write(canonical(value))
            handle.flush()
            os.fsync(handle.fileno())
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def validate_interval(start_text: str, end_text: str) -> str:
    start = datetime.fromisoformat(start_text)
    end = datetime.fromisoformat(end_text)
    if (
        start.utcoffset() != timedelta(0)
        or end.utcoffset() != timedelta(0)
        or (start.hour, start.minute, start.second, start.microsecond) != (0, 0, 0, 0)
        or end - start != timedelta(days=1)
    ):
        raise ValueError("Expected one full UTC day, not a zero-duration trigger interval")
    day = start.date().isoformat()
    if day not in DAYS:
        raise ValueError("Interval is outside the finite fixture")
    return day


def rows_for(day: str, revision: int = 0) -> list[dict[str, object]]:
    if day not in DAYS or type(revision) is not int or revision not in (0, 1):
        raise ValueError("Unapproved fixture day or revision")
    rows = [dict(row) for row in SOURCE if row["day"] == day]
    if revision == 1:
        if day != DAYS[0]:
            raise ValueError("Correction is defined only for the first day")
        rows[0]["amount"] = 6
    return rows


def write_partition(day: str, revision: int, run_id: str) -> dict[str, object]:
    rows = rows_for(day, revision)
    content = {
        "schema_version": 1,
        "day": day,
        "revision": revision,
        "source_sha256": hashlib.sha256(canonical(rows)).hexdigest(),
        "rows": rows,
        "amount_total": sum(row["amount"] for row in rows),
    }
    path = ROOT / "outputs" / (day + ".json")
    if path.exists():
        old = read_partition(day)
        if old == content:
            return {"day": day, "path": str(path), "source_sha256": content["source_sha256"]}
        if old["revision"] >= revision:
            raise ValueError("Refusing an unexpected replacement or revision downgrade")
    atomic(path, content)
    atomic(
        ROOT / "write-receipts" / (uuid.uuid4().hex + ".json"),
        {
            "day": day,
            "revision": revision,
            "run_id": run_id,
            "source_sha256": content["source_sha256"],
        },
    )
    return {"day": day, "path": str(path), "source_sha256": content["source_sha256"]}


def read_partition(day: str) -> dict[str, object]:
    if day not in DAYS:
        raise ValueError("Unknown day")
    path = ROOT / "outputs" / (day + ".json")
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 16_384:
        raise ValueError("Invalid partition path or size")
    record = json.loads(path.read_text())
    expected_rows = rows_for(day, record["revision"])
    expected = {
        "schema_version": 1,
        "day": day,
        "revision": record["revision"],
        "source_sha256": hashlib.sha256(canonical(expected_rows)).hexdigest(),
        "rows": expected_rows,
        "amount_total": sum(row["amount"] for row in expected_rows),
    }
    if record != expected:
        raise ValueError("Partition contents or source identity differ")
    return record


def source_rows(versions: dict[str, str]) -> list[dict[str, object]]:
    if not 1 <= len(versions) <= 2:
        raise ValueError("Invalid source population")
    rows: list[dict[str, object]] = []
    for day, digest in sorted(versions.items()):
        choices = (0, 1) if day == DAYS[0] else (0,)
        matched = [
            revision
            for revision in choices
            if day in DAYS
            and hashlib.sha256(canonical(rows_for(day, revision))).hexdigest() == digest
        ]
        if len(matched) != 1:
            raise ValueError("Unknown snapshot source identity")
        rows.extend(rows_for(day, matched[0]))
    return rows


def read_snapshot(reference: dict[str, str]) -> dict[str, object]:
    if set(reference) != {"path", "sha256"}:
        raise ValueError("Unexpected source-reference fields")
    path = Path(reference["path"])
    if path.parent != ROOT / "snapshots" or re.fullmatch(r"[a-f0-9]{64}\.json", path.name) is None:
        raise ValueError("Source snapshot path is outside the owned namespace")
    if (
        path.parent.is_symlink()
        or path.is_symlink()
        or not path.is_file()
        or path.stat().st_size > 16_384
    ):
        raise ValueError("Invalid source snapshot path or size")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != reference["sha256"]:
        raise ValueError("Source snapshot identity differs")
    record = json.loads(raw)
    if (
        set(record) != {"schema_version", "source_versions", "rows"}
        or record["schema_version"] != 1
    ):
        raise ValueError("Unexpected source snapshot schema")
    if record["rows"] != source_rows(record["source_versions"]):
        raise ValueError("Source snapshot values differ")
    return record


def capture_source(run_id: str) -> dict[str, str]:
    if not isinstance(run_id, str) or not 1 <= len(run_id) <= 250:
        raise ValueError("Invalid owned run identity")
    path = ROOT / "snapshots" / (hashlib.sha256(run_id.encode()).hexdigest() + ".json")
    if path.exists():
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 16_384:
            raise ValueError("Invalid retained source snapshot path or size")
        reference = {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        read_snapshot(reference)
        return reference
    records = [read_partition(day) for day in DAYS if (ROOT / "outputs" / (day + ".json")).exists()]
    versions = {record["day"]: record["source_sha256"] for record in records}
    snapshot = {"schema_version": 1, "source_versions": versions, "rows": source_rows(versions)}
    atomic(path, snapshot)
    return {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def validate_summary(record: dict[str, object]) -> None:
    """Reconcile saved observations with hand-derived per-version fixture totals."""
    if set(record) != {"run_id", "region", "source_versions", "rows", "amount_total"}:
        raise ValueError("Unexpected summary fields")
    region = record["region"]
    versions = record["source_versions"]
    if region not in ("east", "west") or type(versions) is not dict or not 1 <= len(versions) <= 2:
        raise ValueError("Invalid summary region or source population")
    hand_totals = {
        (DAYS[0], 0, "east"): (1, 4),
        (DAYS[0], 0, "west"): (1, 9),
        (DAYS[0], 1, "east"): (1, 6),
        (DAYS[0], 1, "west"): (1, 9),
        (DAYS[1], 0, "east"): (1, 7),
        (DAYS[1], 0, "west"): (0, 0),
    }
    count = total = 0
    for day, digest in versions.items():
        choices = (0, 1) if day == DAYS[0] else (0,)
        matching = [
            revision
            for revision in choices
            if day in DAYS
            and hashlib.sha256(canonical(rows_for(day, revision))).hexdigest() == digest
        ]
        if len(matching) != 1:
            raise ValueError("Unknown summary source identity")
        n, amount = hand_totals[(day, matching[0], region)]
        count += n
        total += amount
    if record["rows"] != count or record["amount_total"] != total:
        raise ValueError("Summary differs from independent per-version oracle")


def initialize() -> None:
    identity = {"schema_version": 1, "fixture": "airflow-orders-two-days-v1"}
    marker = ROOT / "identity.json"
    if marker.exists():
        if (
            marker.is_symlink()
            or marker.stat().st_size > 4096
            or json.loads(marker.read_text()) != identity
        ):
            raise ValueError("Retained installation identity differs")
        for name in (
            "airflow",
            "outputs",
            "attempts",
            "summaries",
            "write-receipts",
            "observations",
            "snapshots",
            "home",
        ):
            if (ROOT / name).is_symlink() or not (ROOT / name).is_dir():
                raise ValueError("Retained state is incomplete; no reset performed")
        passwords = ROOT / "passwords.json"
        if passwords.is_symlink() or not passwords.is_file() or passwords.stat().st_size > 4096:
            raise ValueError("Retained credential fixture is incomplete; no reset performed")
        return
    if list(ROOT.iterdir()):
        raise ValueError("Unidentified retained state; no reset performed")
    for name in (
        "airflow",
        "outputs",
        "attempts",
        "summaries",
        "write-receipts",
        "observations",
        "snapshots",
        "home",
    ):
        (ROOT / name).mkdir(mode=0o700)
    atomic(ROOT / "passwords.json", {"learner": "learner"})
    atomic(marker, identity)
    for path in [ROOT, *ROOT.iterdir()]:
        path.chmod(0o700 if path.is_dir() else 0o600)
        if os.geteuid() == 0:
            os.chown(path, 50000, 0)


if __name__ == "__main__":
    initialize()
