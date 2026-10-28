import tempfile
from pathlib import Path

import pyarrow as pa
from datafusion import RuntimeEnvBuilder, SessionConfig, SessionContext

rows = [{"id": i, "group_id": i % 10, "value": i % 37} for i in range(4000)]
table = pa.Table.from_pylist(rows)
expected = [
    {"group_id": g, "n": 400, "total": sum(r["value"] for r in rows if r["group_id"] == g)}
    for g in range(10)
]
outputs = []
with tempfile.TemporaryDirectory() as temporary:
    for count in [1, 4]:
        spill = Path(temporary) / f"spill-{count}"
        spill.mkdir()
        runtime = (
            RuntimeEnvBuilder()
            .with_disk_manager_specified(str(spill))
            .with_fair_spill_pool(32 * 1024 * 1024)
        )
        config = SessionConfig().with_target_partitions(count)
        ctx = SessionContext(config, runtime)
        ctx.register_record_batches("events", [table.to_batches(max_chunksize=500)])
        query = ctx.sql(
            "SELECT group_id,COUNT(*) AS n,SUM(value) AS total FROM events "
            "GROUP BY group_id ORDER BY group_id"
        )
        result = query.to_arrow_table().to_pylist()
        assert result == expected
        outputs.append(result)
        filtered = (
            ctx.sql("SELECT id,value FROM events WHERE value<2 ORDER BY value,id")
            .to_arrow_table()
            .to_pylist()
        )
        oracle = sorted(
            [{"id": r["id"], "value": r["value"]} for r in rows if r["value"] < 2],
            key=lambda r: (r["value"], r["id"]),
        )
        assert filtered == oracle
        print("Target partitions:", count, "retained rows:", len(filtered))
        print(str(query.execution_plan()))
        print(
            "Files remaining after execution, not a historical spill count:",
            len(list(spill.iterdir())),
        )
assert outputs[0] == outputs[1]
