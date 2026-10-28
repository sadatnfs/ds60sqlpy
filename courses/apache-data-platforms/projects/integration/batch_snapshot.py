"""Actual bounded Iceberg/Arrow/DataFusion batch with an independent dossier."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import sys
from pathlib import Path

import pyarrow as pa
from datafusion import SessionContext
from pyiceberg.catalog import load_catalog
from pyiceberg.exceptions import NoSuchTableError

BASE_ROWS = [
    {"id": 1, "region": "east", "amount": 4},
    {"id": 2, "region": "west", "amount": 9},
    {"id": 3, "region": "east", "amount": 7},
]
EXTRA = {"id": 4, "region": "west", "amount": 2}


def logical_digest(rows):
    return hashlib.sha256(
        json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def run(root: Path):
    if root.exists() or root.is_symlink():
        raise ValueError(
            "Use a new absent owned output directory; no existing evidence is replaced"
        )
    root.mkdir()
    settings = {
        "type": "sql",
        "uri": "sqlite:///" + str(root / "catalog.db"),
        "warehouse": (root / "warehouse").as_uri(),
    }
    catalog = load_catalog("capstone", **settings)
    catalog.create_namespace("demo")
    batch = pa.Table.from_pylist(BASE_ROWS)
    table = catalog.create_table("demo.orders", schema=batch.schema)
    table.append(batch)
    first = table.current_snapshot().snapshot_id
    old = table.scan(snapshot_id=first).to_arrow()
    ctx = SessionContext()
    ctx.register_record_batches("original", [old.to_batches()])

    def totals(name):
        if name not in {"original", "refreshed"}:
            raise ValueError("Only fixed capstone relations are accepted")
        return (
            ctx.sql(
                f"SELECT region,SUM(amount) AS total FROM {name} GROUP BY region ORDER BY region"
            )
            .to_arrow_table()
            .to_pylist()
        )

    expected_old = [{"region": "east", "total": 11}, {"region": "west", "total": 9}]
    if (
        sorted(old.to_pylist(), key=lambda row: row["id"]) != BASE_ROWS
        or totals("original") != expected_old
    ):
        raise AssertionError("Independent original row/aggregate oracle failed")
    table.append(pa.Table.from_pylist([EXTRA]))
    second = table.current_snapshot().snapshot_id
    new = table.scan(snapshot_id=second).to_arrow()
    ctx.register_record_batches("refreshed", [new.to_batches()])
    if first == second or sorted(new.to_pylist(), key=lambda row: row["id"]) != BASE_ROWS + [EXTRA]:
        raise AssertionError("Independent changed snapshot identity/value oracle failed")
    if totals("original") != expected_old or totals("refreshed") != [
        {"region": "east", "total": 11},
        {"region": "west", "total": 11},
    ]:
        raise AssertionError("Materialization refresh boundary failed")
    reopened = load_catalog("capstone", **settings).load_table("demo.orders")
    if (
        reopened.current_snapshot().snapshot_id != second
        or reopened.scan(snapshot_id=first).to_arrow().to_pylist() != old.to_pylist()
    ):
        raise AssertionError("Fresh catalog readback changed snapshot identity")
    try:
        load_catalog("wrong-logical-catalog", **settings).load_table("demo.orders")
    except NoSuchTableError:
        pass
    else:
        raise AssertionError("Wrong logical catalog unexpectedly resolved the table")
    result = {
        "schema_version": 1,
        "passed": True,
        "actual_libraries": {
            name: importlib.metadata.version(name)
            for name in ["pyarrow", "datafusion", "pyiceberg"]
        },
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "source_logical_sha256": logical_digest(BASE_ROWS),
        "schema": str(batch.schema),
        "snapshots": [str(first), str(second)],
        "original_rows": BASE_ROWS,
        "current_rows": BASE_ROWS + [EXTRA],
        "original_totals": expected_old,
        "current_totals": totals("refreshed"),
        "fresh_catalog_readback": True,
        "wrong_catalog_rejected": True,
        "direct_spark_or_iceberg_datafusion_connector_qualified": False,
    }
    target = root / "receipt.json"
    with target.open("x") as output:
        output.write(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Supply one absent owned absolute output directory")
    path = Path(sys.argv[1])
    if not path.is_absolute():
        raise SystemExit("Use an absolute output directory")
    print(json.dumps(run(path), sort_keys=True))
