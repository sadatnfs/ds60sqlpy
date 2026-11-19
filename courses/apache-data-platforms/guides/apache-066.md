# apache-066: Hive SQL and execution plans

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-065`, `apache-063`.

## A SQL plan describes work, not just a desired answer

Hive SQL expresses a relational result. The selected execution engine, optimizer,
statistics and storage readers determine how that result is produced. EXPLAIN
exposes a planned structure that can include scans, filters, aggregations,
exchanges and joins. A plan is valuable evidence, but actual runtime counters
are needed to establish which work occurred and where time was spent.

The prepared local workshop deliberately uses a bounded execution path and a
three-row Parquet fixture. It is not a YARN cluster, a distributed Tez benchmark
or a demonstration of production resource management. The full official image
contains compatible Hadoop/Tez components, but their presence does not establish
that a specific query selected or exercised a distributed execution route.

Statistics summarize input properties for planning. Stale or missing row counts,
size estimates and column distributions can lead to poor decisions. A correct
result can therefore coexist with an inefficient plan. Conversely, a plausible
fast result can still be wrong if input completeness or join cardinality was
never checked independently.

## Worked case A: explain a selective aggregate

The prepared explain.sql filters the day partition, groups by region and sums
amount:

From [`projects/hive/explain.sql`](../projects/hive/explain.sql):

```sql
EXPLAIN
SELECT
  region,
  SUM(amount)
FROM
  ds60.orders
WHERE
  day = '2026-01-01'
GROUP BY
  region;

SELECT
  region,
  SUM(amount)
FROM
  ds60.orders
WHERE
  day = '2026-01-01'
GROUP BY
  region
ORDER BY
  region;
```

`bash run.sh explain` runs both statements against the external `ds60.orders`
table, which has one `day='2026-01-01'` partition holding orders 1 (east, 4),
2 (west, 9) and 3 (east, 7). The independent result is east 11 and west 9. Inspect the partition
predicate and aggregation stages in the actual plan, then run the query. Keep
the SQL text, schema, partition inventory and result together so the plan can be
interpreted against the input it describes.

A local sum can be reasoned about as partial aggregation followed by combination:
\(\sum_i x_i=\sum_j\sum_{i\in P_j}x_i\) for disjoint partitions. That algebra
explains why an engine may reduce data before an exchange. It does not prove
that the selected Hive plan used that optimization, nor does it make distinct
count, median or an arbitrary user function equally decomposable.

On the tiny fixture, execution time is largely startup and scheduling overhead.
Measure repeated comparable runs on a representative distribution before making
capacity or engine recommendations. Retain data shape and selected configuration
beside timings; a query name alone is insufficient context for a performance
comparison.

## Worked case B: challenge a map-side join assumption (design exercise)

The workshop has no dimension table and `run.sh` has no join command, so this case
is a design exercise with a written answer rather than an executed example. In a
copied workshop, the dimension and the plan request would be:

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS ds60.regions (region STRING, manager STRING)
STORED AS PARQUET LOCATION 'file:///warehouse/regions';
INSERT INTO ds60.regions VALUES ('east', 'Avery'), ('west', 'Blake');

EXPLAIN
SELECT o.region, COUNT(*) AS orders, SUM(o.amount) AS total
FROM ds60.orders o
JOIN ds60.regions r ON o.region = r.region
WHERE o.day = '2026-01-01'
GROUP BY o.region;
```

With one row per region, the written answer is east 11 from two orders and west 9
from one order. In the plan, a map-side join appears as a `Map Join Operator`
whose small side is loaded into a hash table; a shuffle join appears as a
`Merge Join Operator` or `Join Operator` after an exchange.

Prepare a separate owned dimension with one row per region and join it to orders.
First verify uniqueness and the expected three enriched fact identities. Then
inspect whether the actual plan uses a broadcast/map-side strategy or another
join. A small dimension is a reason to investigate that strategy, not a guarantee
that a particular release and configuration will choose it.

Now deliberately duplicate the east dimension key in an isolated comparison.
The join may multiply east facts even if its physical strategy remains efficient.
After inserting `('east', 'Casey')`, the written answer becomes east 22 from four
joined rows while west stays 9, and
`SELECT region, COUNT(*) FROM ds60.regions GROUP BY region HAVING COUNT(*) > 1`
returns `east 2` before the join runs.
An optimizer cannot infer an unstated business uniqueness constraint from a
three-row sample. Validate the intended many-to-one relationship before treating
the aggregate as trustworthy.

Memory estimates matter for broadcast decisions. Compressed source size is not
necessarily the in-memory hash-table size, and per-task replication can multiply
memory pressure. A hint can change planning but cannot create missing memory or
repair skew. Keep hints subordinate to a measured plan and resource contract
rather than using them as a universal remedy.

## Diagnosis and interview discussion

Compare logical result, chosen engine, explain output, statistics freshness,
actual counters and resource limits. Partition pruning, vectorized reading,
partial aggregation and broadcast are distinct mechanisms with separate evidence.
Do not infer all of them from one fast wall-clock observation or one familiar
operator label.

**Interview discussion: why can a correct Hive query become slow without changing
its SQL?** Input volume/distribution, partitions, statistics, engine settings or
available resources can change. The aggregate case ties a plan to a finite oracle,
while the join case separates physical execution choices from data-cardinality
correctness.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Hive apache-066 command notebook

Run from the copied owned Hive project, following its README. Native service
acceptance is separately recorded in QUALIFICATION.md.

```bash
cat explain.sql
bash run.sh explain
```

Inspect actual partition and aggregate plan operators before claiming a specific engine optimization. Query result correctness and physical work are separate observations.

The classroom does not execute these Docker commands. Retain source, schema,
file identities, actual responses and failure scope in an independent receipt.

## Primary references

- [Hive4.2.1 preparation and components](https://hive.apache.org/development/quickstart/)
- [Hive DDL](https://hive.apache.org/docs/latest/language/languagemanual-ddl/)
- [Hive Metastore administration](https://hive.apache.org/docs/latest/admin/adminmanual-metastore-administration/)
- [Hive/Iceberg integration](https://iceberg.apache.org/docs/latest/hive/)
- [Pinned schema tool source](https://github.com/apache/hive/tree/rel/release-4.2.1/standalone-metastore/metastore-server/src/main/java/org/apache/hadoop/hive/metastore/tools/schematool)
