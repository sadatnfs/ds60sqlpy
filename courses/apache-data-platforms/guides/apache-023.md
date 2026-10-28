# apache-023: Stages, shuffle and task placement

Tutorial mode. Stage: intermediate. Direct prerequisites: `apache-021`, `apache-005`, `apache-011`.

## A stage boundary changes where intermediate state lives

A query such as group by region can perform partial aggregation near each input
partition, exchange intermediate data by grouping key, and combine final results.
A stage is a set of tasks that can run under a particular dependency boundary.
A shuffle moves or exposes intermediate partitions so downstream tasks can read
their required inputs. The scheduler coordinates these dependencies, while the
executors perform scans and operators.

An Arrow record batch is not a task, and a task is not always an entire stage.
The distinction matters when diagnosing a slow query. A large number of batches
may flow through one task, or several tasks may each handle a small partition.
Operators can fuse into one pipeline, while exchanges introduce coordination,
network or local transport, buffering and intermediate storage.

The workshop's plans command executes actual Ballista queries and retains the
returned plan observations together with source identity. It uses the selected
release's exposed explain interface. Plan text helps explain operators, but it
is not asserted as a stable byte-for-byte API across versions. Exact result
identities and sums provide the semantic oracle.

## Worked case A: a balanced aggregation

The first query groups a deterministic fixture whose region values alternate.
The expected row count in each group is 100. The program verifies counts and sums
against a separately computed Python dictionary, then captures the logical and
physical explanation exposed by the actual client. Read the exchange and aggregate
operators in terms of where state is produced and consumed.

Do not infer that two final groups imply two executor tasks or that two task slots
must both do useful work on a tiny file. The engine can choose a plan whose
parallelism depends on file partitions, configuration and optimizations. A requested
target partition count is a planning input, not an observation that every worker
was busy. The source and result remain bounded so the mechanism is inspectable.

For a sum, each input partition can send one partial sum per group. For an average,
the merge state needs both sum and count. Distinct count, quantiles and order-aware
state require different representations. Choosing an aggregate therefore changes
how much data can be reduced before an exchange and what state must cross it.

## Worked case B: a hot grouping key

A second fixture contains a large repeated key and several rare keys. Its real
Ballista aggregation must still equal the independent oracle. The checker reports
the key-frequency distribution beside the plan. It does not convert those counts
into invented task timings or claim that one specific executor was slow without
actual task-level metrics.

Key partitioning sends equal keys together, so a hot key can concentrate work or
state. Adding partitions cannot divide an indivisible key group by itself. A
mergeable sum may support preaggregation or salting followed by a second merge,
while an ordered state machine may not. The correct mitigation depends on the
operator's algebra and the system's supported execution strategy.

A simplified lower bound is \(T\geq\max_i W_i/r_i\), where partition work
\(W_i\) is processed at rate \(r_i\). This explains why idle capacity can coexist
with a long critical task. It is a reasoning model, not measured latency from the
fixture. Real execution adds barriers, data movement, startup and output costs.

## Mistakes, diagnosis and interview discussion

Keep counts, bytes, key frequencies and measured task time distinct. A few rows
with large nested payloads can create byte skew without row skew. A sort or join
can dominate even when group counts look balanced. Inspect actual plan and metrics
before changing target partitions, because extra partitions also create scheduling
and bookkeeping overhead.

**Interview discussion: why can an aggregation move less data than its input?**
Associative partial aggregation can compress each partition's records into mergeable
state before exchange. It is effective when groups repeat locally and the state
is small. The two actual queries contrast balanced and hot-key inputs while
preserving exact answers, and identify which performance conclusions still need
real task metrics and representative scale.

The [complete Ballista workshop](../projects/ballista/README.md) provides the maintained files, preparation, lifecycle and exact qualification boundaries for these cases.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Actual distributed plans with independent result checks

```bash
bash run.sh plans
bash run.sh evidence
```

Compare balanced and hot-key fixture distributions, returned results and recorded
plan text. Operator spelling can change with the selected release; exact result
checks remain mandatory. A requested partition count is not proof that all
executors were busy, and a local frequency report is not task timing telemetry.

The complete implementation is `client.py`. It uses real Ballista execution and
separate fixture-derived expected values rather than a Python scheduler model.

## Primary references

- [Ballista shuffle design](https://datafusion.apache.org/ballista/contributors-guide/shuffle.html)
- [Ballista tuning](https://datafusion.apache.org/ballista/user-guide/tuning-guide.html)
