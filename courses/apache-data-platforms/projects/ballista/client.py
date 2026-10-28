"""Bounded actual Ballista requests with independent semantic oracles."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import signal
import tempfile
import time
import uuid
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
from ballista import BallistaSessionContext
from datafusion import SessionContext
from fixture import LOGICAL_SHA, ROOT, ROWS, read
from receipts import emit_report

QUERY = (
    "SELECT region, COUNT(*) AS n, SUM(amount) AS total FROM orders GROUP BY region ORDER BY region"
)


def context() -> BallistaSessionContext:
    return BallistaSessionContext(
        "df://localhost:50050", cluster_config={"datafusion.execution.target_partitions": "2"}
    )


def expected(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["region"]].append(row["amount"])
    return [
        {"region": key, "n": len(values), "total": sum(values)}
        for key, values in sorted(grouped.items())
    ]


def execute(mode: str) -> dict[str, object]:
    read()
    ctx = context()
    ctx.register_parquet("orders", str(ROOT / "orders.parquet"))
    distributed = ctx.sql(QUERY).to_arrow_table().to_pylist()
    oracle = expected(ROWS)
    if distributed != oracle:
        raise AssertionError("Actual Ballista result differs from fixture oracle")
    local = SessionContext()
    local.register_parquet("orders", str(ROOT / "orders.parquet"))
    if local.sql(QUERY).to_arrow_table().to_pylist() != oracle:
        raise AssertionError("Embedded control differs")
    result: dict[str, object] = {
        "rows": distributed,
        "actual_ballista": True,
        "embedded_control": True,
    }
    if mode == "paths":
        with tempfile.TemporaryDirectory(prefix="ballista-missing-") as temporary:
            missing = Path(temporary) / "removed.parquet"
            pq.write_table(pa.Table.from_pylist(ROWS[:3]), missing)
            ctx.register_parquet("removed_source", str(missing))
            missing.unlink()
            try:
                selected = (
                    ctx.sql("SELECT id, region, amount FROM removed_source ORDER BY id")
                    .to_arrow_table()
                    .to_pylist()
                )
            except Exception as error:
                text = str(error).lower()
                if not any(
                    word in text for word in ["not found", "no such file", "does not exist"]
                ):
                    raise AssertionError(
                        "Failure was not the intended missing-file category"
                    ) from error
                result["removed_source_rejected"] = True
            else:
                if selected == ROWS[:3]:
                    raise AssertionError("Removed source unexpectedly retained original rows")
                if selected:
                    raise AssertionError("Unexpected replacement rows after source removal")
                result["removed_source_rejected"] = True
                result["detection_boundary"] = "application row-identity oracle"
                result["observed_removed_source_rows"] = selected
        read()
    if mode == "plans":
        plan = str(ctx.sql("EXPLAIN " + QUERY).to_arrow_table().to_pylist())
        if len(plan.encode()) > 50_000:
            raise ValueError("Plan evidence exceeds budget")
        result["plan"] = plan
        hot = [
            {"id": i, "region": "hot" if i < 180 else f"rare-{i}", "amount": 1} for i in range(200)
        ]
        with tempfile.TemporaryDirectory(prefix="ballista-hot-", dir=ROOT) as temporary:
            path = Path(temporary) / "hot.parquet"
            pq.write_table(pa.Table.from_pylist(hot), path)
            ctx.register_parquet("hot_source", str(path))
            actual = (
                ctx.sql(QUERY.replace("FROM orders", "FROM hot_source"))
                .to_arrow_table()
                .to_pylist()
            )
            if actual != expected(hot):
                raise AssertionError("Hot-key aggregate differs")
            result["hot_key_rows"] = actual
    if mode == "clients":
        frame = ctx.table("orders").select("id", "region", "amount").sort("id").limit(3)
        if frame.to_arrow_table().to_pylist() != ROWS[:3]:
            raise AssertionError("Supported DataFrame action differs")
        result["dataframe_rows"] = 3
    if mode == "bounded-output":
        records = (
            ctx.sql("SELECT id, amount FROM orders ORDER BY id LIMIT 3")
            .to_arrow_table()
            .to_pylist()
        )
        if records != [{"id": row["id"], "amount": row["amount"]} for row in ROWS[:3]]:
            raise AssertionError("Bounded output differs")
        if len(json.dumps(records).encode()) > 2048:
            raise ValueError("Output exceeds byte budget")
        result["bounded_rows"] = records
    return result


def receipts() -> list[Path]:
    folder = ROOT / "receipts"
    if folder.is_symlink() or not folder.is_dir():
        raise ValueError("Expected regular owned receipt directory")
    if list(folder.glob("*.pending")):
        raise ValueError("A pending receipt needs reconciliation; no query was replayed")
    paths = sorted(folder.glob("*.json"))
    if len(paths) > 64 or any(p.is_symlink() or p.stat().st_size > 100_000 for p in paths):
        raise ValueError("Receipt storage bounds exceeded")
    return sorted(paths, key=lambda path: json.loads(path.read_text())["timestamp"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode",
        choices=[
            "check",
            "paths",
            "plans",
            "clients",
            "bounded-output",
            "capacity-failure",
            "evidence",
        ],
    )
    args = parser.parse_args()
    if args.mode == "evidence":
        print(json.dumps([json.loads(p.read_text()) for p in receipts()[-10:]], indent=2))
        return
    if len(receipts()) >= 64:
        raise ValueError("Retain or export the 64 existing receipts before further runs")

    def deadline(*_: object) -> None:
        raise TimeoutError("Bounded query deadline exceeded; outcome needs inspection")

    signal.signal(signal.SIGALRM, deadline)
    signal.alarm(45)
    started = time.monotonic()
    identity = uuid.uuid4().hex
    report = {
        "schema_version": 1,
        "request_id": identity,
        "mode": args.mode,
        "source_sha256": LOGICAL_SHA,
        "timestamp": datetime.now(UTC).isoformat(),
        "versions": {
            name: importlib.metadata.version(name) for name in ["ballista", "datafusion", "pyarrow"]
        },
    }
    try:
        report.update(execute(args.mode))
        if args.mode == "capacity-failure":
            raise AssertionError("Query unexpectedly completed without an executor")
        report["passed"] = True
    except Exception as error:
        report.update(
            {"passed": False, "error_type": type(error).__name__, "error": str(error)[:2000]}
        )
        if args.mode == "capacity-failure" and isinstance(error, TimeoutError):
            report["expected_no_capacity_failure"] = True
            report["scheduler_outcome"] = "unknown; no replay performed"
            return
        raise
    finally:
        signal.alarm(0)
        report["elapsed_seconds"] = time.monotonic() - started
        destination = ROOT / "receipts" / (identity + ".json")
        if not emit_report(report, destination):
            raise RuntimeError(
                "The actual execution outcome was printed with a receipt-storage warning"
            )


if __name__ == "__main__":
    main()
