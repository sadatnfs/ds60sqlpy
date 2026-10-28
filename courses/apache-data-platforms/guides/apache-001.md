# apache-001: A platform is a set of contracts

Tutorial mode. Stage: beginner. Direct prerequisites: .

## Start from a question and a contract

Suppose an analyst asks for paid revenue by region. Before choosing a platform,
identify the records, the unit of money, the meaning of paid, and the time period.
A system can return a beautifully formatted number that answers the wrong question.
Infrastructure does not repair an undefined metric. This chapter follows three
synthetic orders through real Arrow, IPC, Parquet and DataFusion operations so
each transformation has a visible input and output contract.

A data platform separates responsibilities. Storage preserves bytes. A file
format describes their structure. A query engine plans and executes a calculation.
Transport moves data between processes. A catalog identifies tables and their
metadata. Orchestration determines which work should run and when. Governance
records ownership, classifications and policy context. One product may implement
several responsibilities, but that does not make those responsibilities identical.

In the worked program, Arrow supplies an in-memory table, IPC carries typed
batches, Parquet provides a persisted columnar file, and DataFusion executes SQL.
There is no broker, distributed scheduler or external catalog in this first case.
Calling it a local analytical pipeline states exactly what has been demonstrated.
Later workshops add real services to specific boundaries without changing the
meaning of the underlying order fixture.

## Worked case A: preserve meaning across three representations

The first case declares a schema with order ID, region, amount in integer minor
units, and paid status. It writes the table to an IPC buffer and reads it back.
It then writes the restored table to Parquet and registers that file with a
DataFusion session. The SQL query filters paid orders and groups by region.
The independent expected answer comes from the original Python records, not a
second invocation of the same SQL engine.

This distinction is important for testing. Comparing two identical engine calls
only checks repeatability; both calls could make the same mistake. A small fixture
lets a separate, simple calculation act as an oracle. The expected east revenue
is 1100 minor units, while an unpaid west order contributes nothing. The result
also retains the denominator: two paid east orders contributed to that total.

At each boundary, the example checks a different property. The IPC round-trip
preserves table values and types. The persisted file can be reopened. The engine
returns the expected IDs, group and amount. Passing all three checks supports the
local pipeline's correctness for this fixture. It does not prove that a network
transport is authenticated, that a file publication is transactional, or that a
query will meet a large production latency objective.

## Worked case B: a correct sum can still use the wrong population

The second case deliberately removes the paid filter. The query now includes
an additional west total of 900. The engine executed valid SQL correctly, but the
result violates the original question. A compiler cannot reject this semantic
mistake because both queries are legal. The test compares the two answers and
makes the population change explicit instead of treating a zero exit code as
sufficient evidence.

The relevant quantity is
\[R_g=\sum_i a_i\,\mathbf{1}(r_i=g)\,\mathbf{1}(p_i=1),\]
where \(a_i\) is an amount in a declared unit, \(r_i\) the region, and
\(p_i\) the paid indicator. Omitting the final indicator changes the estimand.
Multiplying the final total by a display conversion cannot repair the wrong
population. The chapter therefore keeps monetary values in integer minor units
until presentation and explains why the unit belongs in the contract.

A late correction creates another question: should a rerun represent the original
published data or the most recently corrected data? A versioned table can support
both, but only if the chosen version is recorded. This first temporary Parquet
file has no historical transaction log. Its scope is intentionally narrower.

## Failure interpretation and next steps

An invalid column name is an engine/schema failure. A missing Parquet path is a
storage or configuration failure. A valid query over the wrong population is an
analytical specification failure. These require different remedies. Logging only
'pipeline failed' or 'query succeeded' hides the boundary needed for diagnosis.

**Interview discussion: why not choose the largest distributed platform first?**
Start with the workload's correctness, volume, latency, concurrency and recovery
requirements. A local engine can be the appropriate implementation for a bounded
analytical task. Distribution adds coordination, network and state-management
costs that require justification. The goal is to preserve the data contract while
selecting the smallest architecture that meets the measured requirements, then
add capabilities where evidence shows they are needed.

## Complete worked source

This is a complete editable worked program for the declared prepared runtime. It uses bounded local fixtures and does not install packages or start distributed services.

```python
import tempfile
from pathlib import Path

import pyarrow as pa
import pyarrow.ipc as ipc
import pyarrow.parquet as pq
from datafusion import SessionConfig, SessionContext

records = [
    {"id": 1, "region": "east", "amount_minor": 400, "paid": True},
    {"id": 2, "region": "west", "amount_minor": 900, "paid": False},
    {"id": 3, "region": "east", "amount_minor": 700, "paid": True},
]
schema = pa.schema(
    [
        ("id", pa.int64()),
        ("region", pa.string()),
        ("amount_minor", pa.int64()),
        ("paid", pa.bool_()),
    ]
)
table = pa.Table.from_pylist(records, schema=schema)
sink = pa.BufferOutputStream()
with ipc.new_stream(sink, schema) as writer:
    writer.write_table(table)
restored = ipc.open_stream(sink.getvalue()).read_all()
assert restored.equals(table)
with tempfile.TemporaryDirectory(prefix="platform-contract-") as temporary:
    path = Path(temporary) / "orders.parquet"
    pq.write_table(restored, path)
    context = SessionContext(SessionConfig().with_target_partitions(2))
    context.register_parquet("orders", str(path))
    paid = (
        context.sql(
            "SELECT region, SUM(amount_minor) AS total, COUNT(*) AS orders "
            "FROM orders WHERE paid GROUP BY region ORDER BY region"
        )
        .to_arrow_table()
        .to_pylist()
    )
    expected = [
        {
            "region": "east",
            "total": sum(r["amount_minor"] for r in records if r["paid"]),
            "orders": sum(r["paid"] for r in records),
        }
    ]
    assert paid == expected == [{"region": "east", "total": 1100, "orders": 2}]
    unfiltered = (
        context.sql(
            "SELECT region, SUM(amount_minor) AS total FROM orders GROUP BY region ORDER BY region"
        )
        .to_arrow_table()
        .to_pylist()
    )
    assert unfiltered == [{"region": "east", "total": 1100}, {"region": "west", "total": 900}]
    print("Paid population:", paid)
    print("Different question without the filter:", unfiltered)
```

## Primary references

- [Arrow Python data model](https://arrow.apache.org/docs/python/data.html)
- [DataFusion Python introduction](https://datafusion.apache.org/python/user-guide/introduction.html)
