#!/usr/bin/env python3
"""Qualify declared scientific figures and read their original receipts after replacement.

Uses the standard-library HTTP client and reviewed source-bound expectations.
No plotting library, package installation, Docker operation or publication runs here.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import struct
import sys
import time
import uuid
import zlib
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
from ds60sqlpy.plot_artifacts import validate_artifacts  # noqa: E402
from scripts.check_classroom_profiles import ClassroomClient  # noqa: E402

# Reviewed against actual reference programs, not inferred from language or title.
# A reference edit requires a deliberate contract review and digest refresh.
CONTRACTS: dict[str, dict[str, Any]] = {
    "viz-001": {
        "profile": "python-core",
        "source_path": "courses/data-visualization/references/viz-001.py",
        "source_sha256": "786a9e25caa56a4591983fe2d583df2d87a3e635d8175e6dc7730fcc6fdf62b7",
        "kinds": ["plotly"],
        "table_rows": 3,
    },
    "viz-002": {
        "profile": "python-core",
        "source_path": "courses/data-visualization/references/viz-002.py",
        "source_sha256": "ba2fc101ae8e10c0e23f7a6e007f0de3da98656dfcef8f080177c532103c0c1d",
        "kinds": ["plotly"],
        "table_rows": 4,
    },
    "viz-003": {
        "profile": "python-core",
        "source_path": "courses/data-visualization/references/viz-003.py",
        "source_sha256": "e5d4ea457276ad4af3867b9a8d2b07393d01af64278eb2490e1645c717324a22",
        "kinds": ["plotly"],
        "table_rows": 3,
    },
    "viz-004": {
        "profile": "python-core",
        "source_path": "courses/data-visualization/references/viz-004.py",
        "source_sha256": "8fbf614e4c40b390c2ced375e0587bcf8fcef0f4c6e100a6599757ae65c21987",
        "kinds": ["plotly"],
        "table_rows": 8,
    },
    "viz-005": {
        "profile": "python-core",
        "source_path": "courses/data-visualization/references/viz-005.py",
        "source_sha256": "f042ff1a92d1c7bfd19f7cd2e288bcd2b5377663412f8c7997e8c699396e865f",
        "kinds": ["plotly"],
        "table_rows": 3,
    },
    "viz-006": {
        "profile": "python-core",
        "source_path": "courses/data-visualization/references/viz-006.py",
        "source_sha256": "c5692aca552c0bdfab3ff321ea28215022cf0840d2492c94ca278de79bcf8d43",
        "kinds": ["plotly"],
        "table_rows": 8,
    },
    "viz-007": {
        "profile": "python-core",
        "source_path": "courses/data-visualization/references/viz-007.py",
        "source_sha256": "c4db4aa03fb12da06032b9a356b866002b43c06ccb12423bf661ff2c8658b6a4",
        "kinds": ["plotly"],
        "table_rows": 3,
    },
    "viz-008": {
        "profile": "python-core",
        "source_path": "courses/data-visualization/references/viz-008.py",
        "source_sha256": "5782ce25877a01e05c9b058970eb16d4a7c80bb8e2bebd4894ddada5b20e2efd",
        "kinds": ["plotly"],
        "table_rows": 3,
    },
    "r-051": {
        "profile": "r-statistics",
        "source_path": "courses/r/solutions/r-051_reference.R",
        "source_sha256": "e1d9a0769bacef666b1164023dd48b3fbf6bb7c11693b6cf481a8fb8f3093ab3",
        "kinds": ["png"],
    },
    "r-052": {
        "profile": "r-statistics",
        "source_path": "courses/r/solutions/r-052_reference.R",
        "source_sha256": "4584b3306e1dbd64f06ff1f5d68b39e854eabbf17ec70bdd00fa705eba04471b",
        "kinds": ["png"],
    },
    "r-053": {
        "profile": "r-statistics",
        "source_path": "courses/r/solutions/r-053_reference.R",
        "source_sha256": "993ee8050eeb7dd43b4e587499f035d87b45bb9a47e5953fa8499bcf64ecdeb3",
        "kinds": ["png", "png"],
    },
    "r-054": {
        "profile": "r-statistics",
        "source_path": "courses/r/solutions/r-054_reference.R",
        "source_sha256": "0c72af64ca6c2c24a30d181ff5708d155673a3fe738fad0a9a9b7d83b6aa805a",
        "kinds": ["png", "png"],
    },
    "r-055": {
        "profile": "r-statistics",
        "source_path": "courses/r/solutions/r-055_reference.R",
        "source_sha256": "9346b386a63ec5faff7a8a153c530f71600951f8caeaafc320956233a8bc3e85",
        "kinds": ["png", "png"],
    },
    "r-056": {
        "profile": "r-statistics",
        "source_path": "courses/r/solutions/r-056_reference.R",
        "source_sha256": "4be59d865dc50d6b1b3330f1e38dbd12a64cff68d984b172fa4fa5c34043492c",
        "kinds": ["png", "png"],
    },
    "r-057": {
        "profile": "r-statistics",
        "source_path": "courses/r/solutions/r-057_reference.R",
        "source_sha256": "4df3ebba63ec5bc66c30c81617bd328afb7f4d288f3210c8583026a7aa14072c",
        "kinds": ["plotly", "plotly"],
    },
    "r-058": {
        "profile": "r-statistics",
        "source_path": "courses/r/solutions/r-058_reference.R",
        "source_sha256": "5c6cdc46f98a0025402da216e58aa141e11cbbed75308c6f078c4dbcef11a3f0",
        "kinds": ["plotly"],
    },
    "r-059": {
        "profile": "r-statistics",
        "source_path": "courses/r/solutions/r-059_reference.R",
        "source_sha256": "f93bb9a4c3c2b1e5250a018287251ce95e6f22e3e9275d6f2a2f3d2dda2f178a",
        "kinds": ["png", "plotly"],
    },
    "r-060": {
        "profile": "r-statistics",
        "source_path": "courses/r/solutions/r-060_reference.R",
        "source_sha256": "00389d9fc843c93064e690e31352d74e1582f4709474063c66d66eea34422a05",
        "kinds": ["png", "plotly"],
    },
}


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def source_digest(source: str) -> str:
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def validate_png(encoded: str) -> None:
    """Check actual complete PNG chunks and checksums, not just a plausible header."""
    raw = base64.b64decode(encoded, validate=True)
    offset = 8
    kinds = []
    while offset < len(raw):
        if offset + 12 > len(raw):
            raise ValueError("Truncated scientific PNG chunk.")
        size = struct.unpack(">I", raw[offset : offset + 4])[0]
        stop = offset + size + 12
        if stop > len(raw):
            raise ValueError("Truncated scientific PNG payload.")
        kind = raw[offset + 4 : offset + 8]
        payload = raw[offset + 8 : stop - 4]
        crc = struct.unpack(">I", raw[stop - 4 : stop])[0]
        if zlib.crc32(kind + payload) & 0xFFFFFFFF != crc:
            raise ValueError("Scientific PNG checksum mismatch.")
        kinds.append(kind)
        offset = stop
        if kind == b"IEND":
            break
    if (
        not kinds
        or kinds[0] != b"IHDR"
        or b"IDAT" not in kinds
        or kinds[-1] != b"IEND"
        or offset != len(raw)
    ):
        raise ValueError("Scientific PNG must contain a complete image.")


def verify_figures(identity: str, source: str, artifacts: Any) -> dict[str, Any] | None:
    contract = CONTRACTS.get(identity)
    if contract is None:
        return None
    if source_digest(source) != contract["source_sha256"]:
        raise ValueError(f"{identity}: scientific figure contract is stale for this source.")
    checked = validate_artifacts(artifacts)
    if Counter(item["kind"] for item in checked) != Counter(contract["kinds"]):
        raise ValueError(f"{identity}: expected figures were lost or changed kind.")
    for artifact in checked:
        if artifact["kind"] == "png":
            validate_png(artifact["data"])
            continue
        traces = artifact["figure"]["data"]
        if not traces or any(not trace.get("type") for trace in traces):
            raise ValueError(f"{identity}: Plotly traces are missing.")
        rows = contract.get("table_rows")
        if rows is not None:
            table = artifact.get("table", {})
            if len(table.get("rows", [])) != rows or not artifact.get("description"):
                raise ValueError(f"{identity}: accessible figure description/table is missing.")
    return {
        "kinds": [item["kind"] for item in checked],
        "artifacts_sha256": digest(checked),
        "count": len(checked),
    }


def references(profiles: list[str], root: Path = ROOT) -> list[Any]:
    from scripts.check_module_references import collect_cases

    if not profiles or set(profiles) - {"python-core", "r-statistics"}:
        raise ValueError("Select python-core and/or r-statistics for scientific figures.")
    cases, _ = collect_cases(root, profiles)
    selected = [case for case in cases if case.lesson_id in CONTRACTS]
    expected = {key for key, value in CONTRACTS.items() if value["profile"] in profiles}
    if {case.lesson_id for case in selected} != expected:
        raise ValueError("The admitted scientific figure inventory changed.")
    for case in selected:
        contract = CONTRACTS[case.lesson_id]
        if (
            case.source_path != contract["source_path"]
            or case.source_sha256 != contract["source_sha256"]
            or case.profile != contract["profile"]
        ):
            raise ValueError(f"{case.lesson_id}: review the scientific source contract.")
    return selected


def pad_digest(session: dict[str, Any]) -> str:
    return digest(
        {key: session.get(key, "") for key in ("source", "prediction", "explanation", "review")}
    )


def receipt(case: Any, job: dict[str, Any], job_id: str) -> dict[str, Any]:
    from scripts.check_module_references import verify_result

    verify_result(case, job_id, job)
    figures = verify_figures(case.lesson_id, case.source, job.get("artifacts"))
    if figures is None:
        raise ValueError("A scientific receipt needs an explicit figure contract.")
    return {
        "lesson_id": case.lesson_id,
        "profile": case.profile,
        "job_id": job_id,
        "source_sha256": case.source_sha256,
        "output_sha256": source_digest(job.get("output", "")),
        **figures,
    }


def verify_persistence(
    client: Any, prior: dict[str, Any], profiles: list[str], root: Path = ROOT
) -> dict[str, Any]:
    cases = references(profiles, root)
    expected = [case.lesson_id for case in cases]
    if (
        prior.get("passed") is not True
        or prior.get("profiles") != sorted(set(profiles))
        or [row.get("lesson_id") for row in prior.get("receipts", [])] != expected
        or [row.get("lesson_id") for row in prior.get("pads", [])] != expected
    ):
        raise ValueError("Persistence requires the complete successful scientific report.")
    for case, saved, pad in zip(cases, prior["receipts"], prior["pads"], strict=True):
        job = client.call("module-job", job_id=saved["job_id"])
        if receipt(case, job, saved["job_id"]) != saved:
            raise ValueError("Saved scientific evidence changed after replacement.")
        lesson = client.call("module-lesson", lesson_id=case.lesson_id)
        if pad_digest(lesson["session"]) != pad["sha256"] or not any(
            row["job_id"] == saved["job_id"] for row in lesson["history"]
        ):
            raise ValueError("Restored scientific source/history changed after replacement.")
    return {
        "passed": True,
        "receipts": len(cases),
        "method": "read original jobs and restored pads without execution or writes",
    }


def qualify(
    client: Any,
    profiles: list[str],
    root: Path = ROOT,
    *,
    report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    from scripts.check_module_references import (
        cancel_unconfirmed_job,
        confirmed_terminal_receipt,
        validate_remote_lesson,
        wait_for_job,
    )

    cases = references(profiles, root)
    ready = {
        row["profile"] for row in client.call("module-readiness")["profiles"] if row.get("ready")
    }
    if set(profiles) - ready:
        raise ValueError("A selected scientific runtime is unavailable.")
    report = report if report is not None else {}
    report.update(
        {
            "schema_version": 1,
            "profiles": sorted(set(profiles)),
            "passed": False,
            "receipts": [],
            "pads": [],
        }
    )
    for case in cases:
        original = client.call("module-lesson", lesson_id=case.lesson_id)
        validate_remote_lesson(case, original)
        fields = {
            key: original["session"].get(key, original.get("source", "") if key == "source" else "")
            for key in ("source", "prediction", "explanation", "review")
        }
        job: dict[str, Any] = {}
        job_id = uuid.uuid4().hex
        report["active_case"] = {"lesson_id": case.lesson_id, "job_id": job_id}
        try:
            client.call("module-save", lesson_id=case.lesson_id, fields={"source": case.source})
            submitted = client.call(
                "module-run",
                lesson_id=case.lesson_id,
                source=case.source,
                timeout_seconds=120,
                request_id=job_id,
            )
            if submitted.get("job_id") != job_id:
                raise ValueError("Scientific submission identity changed.")
            job = wait_for_job(client, job_id, time.monotonic() + 150)
            report["receipts"].append(receipt(case, job, job_id))
        finally:
            try:
                if not confirmed_terminal_receipt(case, job_id, job):
                    cleanup = cancel_unconfirmed_job(client, case, job_id)
                    report["active_case"]["cleanup"] = cleanup
                    if not cleanup["confirmed"]:
                        raise ValueError(
                            "Scientific job cleanup was not confirmed; no later case started."
                        )
            finally:
                client.call("module-save", lesson_id=case.lesson_id, fields=fields)
                restored = client.call("module-lesson", lesson_id=case.lesson_id)["session"]
                if pad_digest(restored) != pad_digest(fields):
                    raise ValueError("Scientific source/notes were not restored.")
                report["pads"].append({"lesson_id": case.lesson_id, "sha256": pad_digest(restored)})
        print(f"PASS: {case.lesson_id}: expected figures captured and source restored", flush=True)
    report["passed"] = True
    report.pop("active_case", None)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--profiles", required=True)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--confirm-disposable", action="store_true")
    parser.add_argument("--check-persistence", action="store_true")
    args = parser.parse_args(argv)
    if not args.confirm_disposable:
        parser.error(
            "This gate writes disposable pads and run receipts; pass --confirm-disposable."
        )
    report: dict[str, Any] = {"passed": False}
    try:
        client = ClassroomClient(args.url)
        if args.check_persistence:
            report = json.loads(args.report.read_text("utf-8"))
            report["persistence"] = verify_persistence(client, report, args.profiles.split())
        else:
            qualify(client, args.profiles.split(), report=report)
    except (OSError, ValueError, KeyError, TypeError, TimeoutError) as error:
        report.update(passed=False, failure=f"{type(error).__name__}: {error}")
        print(report["failure"], file=sys.stderr)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", "utf-8")
    return int(report.get("passed") is not True)


if __name__ == "__main__":
    raise SystemExit(main())
