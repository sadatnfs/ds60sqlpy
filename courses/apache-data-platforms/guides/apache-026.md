# apache-026: Capacity and operational decisions

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-023`, `apache-025`, `apache-018`.

## Capacity is constrained by the workload's critical path

A distributed engine can use more executors only when its plan and source layout
expose useful parallel work. More workers add task slots but can also add
coordination, exchange and memory overhead. The useful question is whether a
specific workload's limiting stage becomes faster under a controlled allocation,
not whether the task-slot count is numerically larger.

The workshop exposes one-slot and two-slots actions over the same source
fixture. Its processes share one fixed container CPU and memory allocation, so these are
comparisons of task capacity within a fixed single host. They are not equivalent
to doubling physical cores or adding a second machine. The small fixture primarily
checks correct behavior and records measurements for interpretation.

A capacity record should include source identity, row/byte counts, query text,
versions, requested partitions, active task-slot count, available CPU and memory,
trial count, warmup and whether result collection is included. Missing one of
these can make two timing numbers incomparable. Do not save a performance claim
without the conditions that give it meaning.

## Worked case A: one and two task-slot allocations

Run one-slot, check, two-slots and check in sequence. Each correctness
result must match the same independent oracle. The project records elapsed time
for the bounded action and the actual active child-process identities. A result
that changes with task-slot count is a correctness defect, not an expected scaling
tradeoff.

The fixture is intentionally small enough that scheduling noise can dominate.
One measured invocation is not a reliable speedup estimate. A benchmark extension
would repeat trials under comparable warmup and resource conditions, retain all
observations and report a distribution rather than only the fastest sample.
Changing the input size while changing executors would confound the comparison.

A simple idealized speedup bound is \(S(p)\leq1/(s+(1-s)/p)\), where \(s\)
is the serial fraction and \(p\) the effective parallel capacity. Real execution
also pays coordination and I/O costs, so this bound is a model for reasoning,
not a prediction from the tiny fixture. A bottlenecked source or final collection
can make additional executor slots largely irrelevant.

## Worked case B: bound output before collecting

A second query asks for a deliberately small ordered subset and validates the
maximum returned rows and serialized bytes. The client does not accept arbitrary
SQL or unbounded collection through the workshop command interface. It records
whether execution completed and whether output validation succeeded as separate
observations.

LIMIT restricts returned rows, but a global sort or aggregate can still scan and
process substantial input. The project therefore also bounds fixture size,
container resources and client wall time. A complete resource policy needs these
layers together; a two-row result does not imply a two-row computation.

Inspect scheduler logs and retained plan evidence beside the timing. The selected
Python wrapper does not automatically expose every history-server or metrics
feature described by newer development documentation. The project reports the
interfaces it actually prepared and does not fabricate missing task telemetry.
Adding a history service would require its own image, configuration, persistence
and acceptance checks.

## Mistakes, diagnosis and interview discussion

Compare row skew, byte skew, CPU work, memory state and I/O independently. A query
that spills can trade memory for disk and may need a different tuning approach
from one dominated by network exchange. Keep observed peak usage separate from
a configured limit: a container allowing three GiB is not evidence that it used
three GiB or that every larger input will fit.

**Interview discussion: when would you choose embedded DataFusion over Ballista?**
When the data and concurrency fit one process and the distributed coordination
cost is unnecessary, embedding can simplify deployment and failure handling.
Ballista becomes attractive when actual partitioned workloads benefit from its
execution model and the team can operate its dependencies. The two allocation
and bounded-output cases provide concrete evidence to discuss that tradeoff
without claiming that a tutorial benchmark proves production capacity.

The [complete Ballista workshop](../projects/ballista/README.md) provides the maintained files, preparation, lifecycle and exact qualification boundaries for these cases.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Fixed-host capacity comparison and bounded output

```bash
bash run.sh one-slot
bash run.sh check
bash run.sh two-slots
bash run.sh check
bash run.sh bounded-output
bash run.sh evidence
```

The container's CPU/memory allocation stays fixed. Record all timings and exact
source identity; do not interpret one tiny trial as a scaling benchmark. Source
and output bounds, process readiness and actual result checks are independent.

```bash
bash run.sh status
bash run.sh logs
bash run.sh down
```

Down retains the named data/evidence volume. Destructive deletion is a separately
confirmed action documented in the project README.

## Primary references

- [Ballista tuning guide](https://datafusion.apache.org/ballista/user-guide/tuning-guide.html)
- [Ballista configuration](https://datafusion.apache.org/ballista/user-guide/configs.html)
