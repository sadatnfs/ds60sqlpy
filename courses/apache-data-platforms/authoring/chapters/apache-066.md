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
amount. The independent result is east 11 and west 9. Inspect the partition
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

## Worked case B: challenge a map-side join assumption

Prepare a separate owned dimension with one row per region and join it to orders.
First verify uniqueness and the expected three enriched fact identities. Then
inspect whether the actual plan uses a broadcast/map-side strategy or another
join. A small dimension is a reason to investigate that strategy, not a guarantee
that a particular release and configuration will choose it.

Now deliberately duplicate the east dimension key in an isolated comparison.
The join may multiply east facts even if its physical strategy remains efficient.
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
