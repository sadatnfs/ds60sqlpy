# apache-049: Backpressure and capacity

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-048`, `apache-005`.

## Backpressure propagates a downstream constraint

A pipeline cannot sustainably run faster than its limiting stage. When a sink or
operator consumes data more slowly than upstream produces it, buffers fill and
upstream work can become backpressured. This propagation is useful feedback, but
it can also increase end-to-end latency and influence checkpoint behavior. A
busy source is not necessarily the stage that needs more CPU.

Throughput, latency, busy time, idle time and backpressured time answer different
questions. A task that waits for input can be idle because its source is slow,
while a task waiting for downstream capacity can be backpressured. A long GC
pause or an overloaded external system can produce a different pattern. Inspect
actual task and buffer metrics before selecting a remedy.

The small project keeps workload and container limits explicit. It records the
source population and exact results beside any observed runtime metrics. Configured
memory or slots are limits and capabilities, not measured usage. One local run
cannot establish production capacity or linear scaling.

## Worked case A: constrain a prepared downstream operator

The backpressure route introduces an explicitly bounded delay in a downstream
operator and separates it from its upstream stage. The purpose is to observe the
actual effect on the running job's counters and backpressure metrics. The checker
must distinguish a nonzero observed metric from a prediction based only on the
presence of sleep in source code.

A tiny input can fit entirely in buffers and never create measurable pressure.
The route therefore declares its finite payload size, pacing and observation
window. If the selected machine does not produce the intended metric within the
bound, the result must state that the pressure mechanism was not demonstrated;
it cannot invent a chart or substitute an in-memory queue model.

The same identifiers must still appear in the output. A throttled job that drops
records is incorrect, even if its latency looks smaller. The observation also
keeps the artificial delay out of any claim about the intrinsic efficiency of a
Flink operator or the machine's network hardware.

## Worked case B: change capacity through compatible state

The advanced capacity case starts from an explicit retained state point and
changes parallelism within the prepared topology. Stable operator UIDs, state
names, serializers and maximum parallelism determine whether keyed state can be
assigned compatibly to the new subtasks. A larger integer in the configuration
is not evidence that state was restored correctly.

The checker reconciles the complete finite source-ID set and final total after
the compatible restore. Different subtasks can interleave output, so a global
arrival order is not assumed. A single hot key still belongs to one key group
and cannot be split simply by adding task slots. This relates the actual restore
case to the partition/skew foundations.

A simple bound is \(T\geq\max_i W_i/r_i\), with work \(W_i\) and effective
rate \(r_i\) for stage or partition \(i\). It explains a critical path without
predicting a benchmark number. The project reports only the actual metrics and
correctness observations its selected fixture establishes; optional larger
experiments need their own resource and recovery plan.

## Diagnosis and interview discussion

Trace source rate, operator work, sink behavior, buffer occupancy and checkpoint
durations together. More slots can increase simultaneous state and memory overhead,
while a database connection limit may require less concurrency. Preserve the
original source and receipt when comparing runs, and change one factor at a time.
Do not recover from a capacity error by deleting checkpoint or learner volumes.

**Interview discussion: why might upstream CPU usage fall when the sink slows?**
Upstream can spend time waiting for downstream buffers rather than doing useful
computation. CPU alone is therefore insufficient to locate the bottleneck. These
two cases connect actual pressure observation and state-compatible capacity change
to exact source correctness, while separating the local demonstration from an
unsupported production performance forecast.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Bounded pressure observation and compatible capacity changes

```bash
bash run.sh backpressure
bash run.sh readback
```

The receipt identifies payload, pacing, observation window and actual task metrics.
A configured delay is not itself evidence of measured pressure. The finite output
population still has to match its independent oracle.

```bash
bash run.sh savepoint
bash run.sh readback
```

The compatible restore route records the selected parallelism and state identity.
Read its acceptance ledger before interpreting a prepared extension as an executed
rescale or claiming a speedup from one small run.

## Primary references

- [Flink backpressure monitoring](https://nightlies.apache.org/flink/flink-docs-release-2.3/docs/ops/monitoring/back_pressure/)
- [Flink state and rescaling](https://nightlies.apache.org/flink/flink-docs-release-2.3/docs/concepts/stateful-stream-processing/)
