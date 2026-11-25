# apache-018: Partitions, memory and spill

Tutorial mode. Stage: intermediate. Direct prerequisites: `apache-016`, `apache-005`.

## Key terms

- **Target partitions:** The DataFusion setting for how many execution partitions a plan uses for parallel work in one process. It is not a count of machines or proof of core usage.
- **Execution partition:** One parallel stream of record batches inside a physical plan, distinct from file partitions, Arrow chunks and record-batch size.
- **Memory pool:** The runtime component that tracks memory reserved by cooperating operators and refuses or triggers spilling at a configured limit.
- **Fair spill pool:** A DataFusion memory pool that shares memory among spilling operators. It is not a hard limit on every byte the Python process allocates.
- **Spill:** Writing intermediate operator state, such as sorted runs, to temporary disk files so an operator can finish within its memory reservation.

## Logical partitions consume physical resources

DataFusion is an embedded query engine. A session can create several execution
partitions inside one process; that does not create a distributed cluster.
Target partitions influence parallel execution and repartition operators, while
record-batch size controls a different unit of vector processing. An Arrow table
with four chunks is not evidence that four CPU cores or four remote executors
were used. Inspect the physical plan and actual runtime observations separately.

A runtime environment also owns memory-pool and temporary-storage policies.
A fair spill pool lets cooperating operators spill supported state to disk under
memory pressure. It is not a hard bound on every byte allocated by the Python
process, Arrow libraries or other components. The outer container memory limit
remains an independent process boundary. Running a query successfully under a
small configured pool does not prove the process used less than that pool.

This complete example uses a bounded real DataFusion session and temporary
spill directory. It compares exact answers across partition settings and captures
physical plans for explanation. Plan text is diagnostic output, not a stable
serialized API: assertions target query results and settings rather than requiring
one release's complete operator spelling.

## Worked case A: one partition and four partitions

The input contains 4000 integer rows with ten groups. Two independent sessions
request one and four target partitions and run the same ordered aggregation.
Every group has exactly 400 rows. The program compares the full group/count/sum
output against a Python-derived oracle and between sessions. This establishes
result equivalence on the fixture, not a speedup from four partitions.

A partition count above available cores can still help with uneven tasks, but it
can also increase allocation, scheduling and merge overhead. The useful quantity
is the critical path in the physical plan, not the requested integer by itself.
A final global sort or single output collector can constrain concurrency after
parallel partial work. Explain where data is repartitioned and where it is merged
before proposing additional workers or threads.

The code prints the plan and a small diagnostic summary. It does not time a
single tiny invocation and declare a performance winner. A fair benchmark would
control warmup, repeated trials, data cache, physical core allocation, input bytes
and output materialization. Correctness comes first because a faster query that
dropped rows is not an optimization of the original question.

## Worked case B: projection and filtering before a bounded sort

The second query selects only rows with a small integer value, projects two
columns, then orders the retained result. The Python oracle applies the same
predicate and tie rule independently. A selective predicate can reduce the amount
of data entering a sort. Whether it reduces actual source I/O depends on storage
metadata and the selected physical scan, not simply the presence of a WHERE
clause in SQL.

The runtime configures a 32 MiB fair spill pool and an explicit temporary path.
The fixture is intentionally too small to require a spill. After the query, the
program reports which files exist in the spill directory and labels this as an
observation, with no assertion that spilling occurred. To prove spilling, a
separately bounded workload would need operator metrics or retained spill evidence
and a successful cleanup check. An empty directory can also mean files were
removed after use; it does not by itself prove no spill ever happened.

The difference between permitted spill, observed spill and out-of-memory failure
is operationally important. Some state may not be spillable, disk can fill, and a
query can reach the container limit before an internal pool makes a useful choice.
Resource settings are mechanisms to investigate, not a guarantee that arbitrary
SQL will always complete.

## Diagnosis and interview discussion

Record target partitions, batch size, memory policy, available cores and the
query's input/output sizes. Compare a plan change with real operator metrics and
process measurements. Keep the spill directory in bounded temporary storage and
never point it at learner source or unrelated persistent data. A failed query
should leave its original files intact.

**Interview discussion: why can increasing parallelism increase memory use?**
Several active partitions can hold simultaneous hash tables, buffers and partial
aggregate state. More exchange partitions also add bookkeeping and merge work.
The exact effect depends on the plan and operator implementation. These two cases
prove correctness under declared settings while making the unmeasured performance
and spill claims explicit.

## Worked examples

### Run the same aggregate at two partition counts

```python
import pyarrow as pa
from datafusion import SessionConfig, SessionContext

rows = pa.table({"group_id": [i % 10 for i in range(4000)], "value": [i % 37 for i in range(4000)]})
query = "SELECT group_id, COUNT(*) AS n, SUM(value) AS total FROM events GROUP BY group_id ORDER BY group_id"
results = []
for count in [1, 4]:
    ctx = SessionContext(SessionConfig().with_target_partitions(count))
    ctx.register_record_batches("events", [rows.to_batches(max_chunksize=500)])
    results.append(ctx.sql(query).to_arrow_table())
print(results[0].equals(results[1]), results[0].num_rows)
```

The comparison should print True and 10: the answer is identical at one and four target partitions, and each group holds 400 rows. Only the work layout changes, including how many hash partitions the aggregate builds and how much memory each holds. If results differ between counts, suspect a missing ORDER BY or a non-deterministic function before blaming the engine.

### Bound a sort by projecting and filtering first

```sql
SELECT
  id,
  value
FROM
  events
WHERE
  value < 2
ORDER BY
  value,
  id
```

Projecting two columns and keeping only values 0 and 1 means the sort sees roughly 2 of every 37 rows instead of the full table, which keeps it inside the memory pool without spilling. Under a small fair spill pool, a full sort of wide rows would write to the configured spill directory. When a query is slow, check for spill files in that directory; their presence shows memory pressure, not a wrong answer.

## Complete worked source

Run it as the [worked program rules](../STUDY-GUIDE.md#worked-programs) describe.

```python
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
```

## Primary references

- [DataFusion runtime configuration](https://datafusion.apache.org/python/user-guide/configuration.html)
- [DataFusion memory management](https://docs.rs/datafusion-execution/55.0.0/datafusion_execution/memory_pool/index.html)
