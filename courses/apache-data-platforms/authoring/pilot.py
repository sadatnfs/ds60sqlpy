#!/usr/bin/env python3
"""Exercise real local APIs before admitting the proposed Python runtime.

This is a compatibility probe, not a distributed-service qualification. It does
not contact a sharing server, start a broker or write outside its temporary path.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
import tempfile
from decimal import Decimal
from pathlib import Path


def run() -> dict[str, object]:
    import datafusion
    import delta_sharing
    import pyarrow as pa
    import pyarrow.compute as pc
    import pyarrow.dataset as ds
    import pyarrow.ipc as ipc
    import pyarrow.parquet as pq
    from pyiceberg.catalog import load_catalog
    from pyiceberg.exceptions import CommitFailedException
    from pyiceberg.types import LongType

    checks: list[str] = []
    amounts = pa.array([Decimal("12.50"), None, Decimal("7.25")], type=pa.decimal128(10, 2))
    assert pc.sum(amounts).as_py() == Decimal("19.75")
    values = pa.array([10, None, 30, 40], type=pa.int64())
    sliced = values.slice(1, 2)
    assert sliced.offset == 1 and sliced.to_pylist() == [None, 30]
    assert sliced.buffers()[1].address == values.buffers()[1].address
    checks.append("arrow_decimal_null_and_slice_buffer_identity")
    schema = pa.schema([("id", pa.int64()), ("region", pa.string()), ("value", pa.int64())])
    table = pa.Table.from_pylist(
        [
            {"id": 1, "region": "east", "value": 4},
            {"id": 2, "region": "west", "value": 9},
            {"id": 3, "region": "east", "value": 7},
        ],
        schema=schema,
    )
    sink = pa.BufferOutputStream()
    with ipc.new_stream(sink, schema) as writer:
        writer.write_table(table, max_chunksize=2)
    restored = ipc.open_stream(sink.getvalue()).read_all()
    assert restored.equals(table)
    checks.append("arrow_ipc_stream_exact_round_trip")
    context = datafusion.SessionContext()
    context.register_record_batches("events", [table.to_batches()])
    result = context.sql(
        "SELECT region, SUM(value) AS total FROM events GROUP BY region ORDER BY region"
    ).to_arrow_table()
    assert result.to_pylist() == [{"region": "east", "total": 11}, {"region": "west", "total": 9}]
    checks.append("datafusion_real_sql_aggregate")
    context.register_udf(
        datafusion.udf(
            lambda x: pc.multiply(x, 2), [pa.int64()], pa.int64(), "immutable", "double_value"
        )
    )
    assert context.sql("SELECT double_value(value) AS v FROM events ORDER BY id").to_arrow_table()[
        "v"
    ].to_pylist() == [8, 18, 14]
    checks.append("datafusion_typed_arrow_udf")
    with tempfile.TemporaryDirectory(prefix="ds60-platform-pilot-") as temporary:
        root = Path(temporary)
        parquet = root / "events.parquet"
        pq.write_table(table, parquet, row_group_size=1)
        dataset = ds.dataset(parquet, format="parquet")
        selected = dataset.to_table(columns=["id", "value"], filter=ds.field("region") == "east")
        assert selected.to_pylist() == [{"id": 1, "value": 4}, {"id": 3, "value": 7}]
        checks.append("arrow_parquet_project_and_filter")
        catalog = load_catalog(
            "pilot",
            type="sql",
            uri="sqlite:///" + str(root / "catalog.db"),
            warehouse=(root / "warehouse").as_uri(),
        )
        catalog.create_namespace("lesson")
        iceberg = catalog.create_table("lesson.events", schema=schema)
        iceberg.append(table)
        first_snapshot = iceberg.current_snapshot()
        assert first_snapshot is not None
        snapshot_id = first_snapshot.snapshot_id
        stale = catalog.load_table("lesson.events")
        with iceberg.update_schema() as update:
            update.rename_column("value", "amount")
        try:
            with stale.update_schema() as update:
                update.add_column("stale_added", LongType())
        except CommitFailedException:
            checks.append("iceberg_stale_schema_commit_rejected")
        else:
            raise AssertionError("A stale schema commit unexpectedly succeeded")
        assert iceberg.scan(snapshot_id=snapshot_id).to_arrow().num_rows == 3
        assert iceberg.schema().find_field("amount").field_id == 3
        checks.append("iceberg_append_snapshot_and_field_identity")
        profile_path = root / "fixture.share"
        profile_path.write_text(
            json.dumps(
                {
                    "shareCredentialsVersion": 1,
                    "endpoint": "http://127.0.0.1:1/delta-sharing",
                    "bearerToken": "synthetic-noncredential",
                }
            ),
            encoding="utf-8",
        )
        profile = delta_sharing.protocol.DeltaSharingProfile.read_from_file(str(profile_path))
        assert profile.endpoint == "http://127.0.0.1:1/delta-sharing"
        checks.append("delta_sharing_local_profile_parse_only")
    return {
        "schema_version": 1,
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "versions": {
            name: importlib.metadata.version(name)
            for name in ["pyarrow", "datafusion", "pyiceberg", "delta-sharing"]
        },
        "checks": checks,
        "passed": True,
        "limits": [
            "Local library API probe only",
            "No Delta Sharing server exchange",
            "No distributed or cross-platform runtime qualification",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run()
    encoded = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
