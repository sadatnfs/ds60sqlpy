# apache-087: Capacity, costs and architectural tradeoffs

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-020`, `apache-049`, `apache-061`.

## Key terms

- **Workload model:** The input distribution, query or update pattern, freshness target and failure contract that a capacity comparison must state.
- **Configured limit:** A CPU or memory budget set for safety. It bounds a container but is not measured usage or a production sizing recommendation.
- **Cold and warm state:** Whether caches, compiled code and materialized inputs were already present when a measurement started.
- **Architectural tradeoff:** Choosing among embedded, batch, streaming and serving systems by workload needs and operating cost rather than a single timing.

## Capacity decisions need a workload and measurement boundary

An embedded query, a batch table build, a stateful stream and an analytical
serving cluster solve different workload problems. Comparing them requires a
specified input distribution, query/update pattern, freshness target and failure
contract. A single small wall-clock timing cannot determine which architecture
is generally best.

The course fixtures are deliberately tiny and bounded. They establish mechanisms,
API compatibility and selected correctness/recovery behavior. Their CPU/memory
limits are safety budgets, not production sizing recommendations. The Docker VM's
free disk also differs from the host machine's free disk, so both preparation
and steady-state capacity must be observed separately.

Measure software/source version, native architecture, cold/warm state, concurrency,
input bytes, row/key distribution and resource counters. Keep network/download
preparation outside query execution timing. An architecture that appears fast
because its input was already materialized is answering a different comparison
from one that includes acquisition and commit.

## Worked case A: measure one actual bounded path

Choose the actual Arrow-to-DataFusion batch or one qualified service workshop.
Record input bytes/rows, exact result oracle and source/image identities. Measure
process/container CPU, peak memory, stored bytes and elapsed request time using
the supported host/Docker tools. Repeat a stated cold/warm sequence without
changing the source or silently reinitializing state.

Report the observations as measurements of that workload and machine. A
container memory limit is not its measured usage, and a sampled point can miss
a peak. CPU percentage also depends on the tool's core normalization. State the
counter definition and sampling interval before comparing values between engines.

A rough throughput model is \(T\approx n/t\) for a finite completed batch, but
streaming steady-state throughput and tail latency require different windows.
Queueing can rise rapidly as offered load approaches service capacity. The
little three-row fixture cannot estimate that knee reliably, so label any larger
capacity forecast as an assumption to validate.

## Worked case B: compare architecture tradeoffs with changed requirements

Suppose the workload initially needs a daily reproducible report over a small
snapshot. An embedded DataFusion query over a supported materialization can be
simple and appropriate. Now require continuously fresh per-key state, retained
transport positions and low-latency analytical serving. Kafka/Flink/Pinot can
supply relevant mechanisms, while introducing coordination, state, operational
and compatibility costs.

This is a requirements comparison, not a benchmark proving one stack faster.
List the exact new guarantees needed and which component owns each one. A
catalog/governance requirement can justify additional metadata services without
changing the arithmetic query engine. Avoid deploying every named product merely
to make a diagram look complete.

Preparation storage matters on small machines. Large official archives and image
layers can require temporary duplication during download/extraction/build. Starting
one heavy pack at a time and using verified owned caches can reduce contention,
but broad prune risks destroying reusable bases or unrelated state. Capacity
recovery must preserve the project's ownership and evidence boundaries.

## Diagnosis and interview discussion

Separate measured resource use, configured limits, estimated capacity and cost
forecasts. Record which costs include idle services, storage retention, network
transfer and operational work. Explain where the data distribution or failure
model differs before extrapolating a local result to another deployment.

**Interview discussion: why is an embedded query often an architectural option
rather than an inferior miniature cluster?** It can satisfy a bounded workload
with fewer moving parts, while different requirements can justify distributed
state and serving. These cases measure one supported path and then change the
requirements explicitly, keeping empirical results separate from design judgment.

## Worked examples

### Measure one bounded run with its definition

```python
import time

values = list(range(200_000))
start = time.perf_counter()
total = sum(value * 2 for value in values)
elapsed = time.perf_counter() - start
print(total, "elapsed seconds above zero:", elapsed > 0)
```

```text
39999800000 elapsed seconds above zero: True
```

The printed total is deterministic, while the elapsed time varies per machine, so only its existence is printed here. A capacity claim needs the input size, the timer used, what was inside the timed region and how many samples were taken. One run of a small fixture cannot predict a cluster's throughput; it only gives a baseline for comparing two configurations on the same machine.

### Container limits versus observed use

```bash
docker stats --no-stream --format "{{.Name}} {{.CPUPerc}} {{.MemUsage}}"
```

The output prints each container with current CPU percent and memory used over its limit. The limit is a configured ceiling, not a measurement of need; a container at 30 percent of its memory limit during a tiny fixture says little about production. Sample during the workload, record the sampling window, and keep forecasts in a separate section from what was observed.

## Complete worked source

The classroom does not execute these service commands. See the [workshop rules](../STUDY-GUIDE.md#workshop-notebooks).

# Integration apache-087 complete worked notebook

Measure one actual supported path with source/image/native identity, input distribution, CPU/memory/storage/time definitions and sampling window. Keep configured limits and larger capacity forecasts distinct from measured values.

## What this capacity receipt must hold

- The Docker engine OS, architecture and total memory, as `docker info` reports them.
- Image and build cache sizes from `docker system df`, before and after the run.
- The workload input in rows and bytes, with its exact result oracle.
- The configured container limits, such as 512 MB and one CPU for the batch path.
- Peak memory and CPU as sampled, with the sampling interval and the tool used.
- Elapsed time for each run in a stated cold and warm sequence.

The capacity oracle is a consistency check rather than a target number. A peak
memory reading above the configured limit means the counter measured something
other than the container. Elapsed time with a wrong result is not a measurement
of the workload. A warm run slower than a cold run usually means another process
competed, so record what else was running. The
[shared receipt rules](../STUDY-GUIDE.md#evidence-receipts) cover naming and storage.

## Concrete source inspection

From the copied integration directory, with sibling project copies when selected:

```bash
docker info --format "{{.OSType}}/{{.Architecture}} {{.MemTotal}}"
docker system df
```

Both commands only read engine state. `MemTotal` is the memory the Docker
engine's virtual machine sees, which on a desktop install can be far less than
the host's physical memory. `docker system df` shows reclaimable space; a large
reclaimable figure is not permission to prune shared bases or other projects.

## Primary references

- [DataFusion memory pools](https://docs.rs/datafusion-execution/55.0.0/datafusion_execution/memory_pool/index.html)
- [DataFusion Python runtime settings](https://datafusion.apache.org/python/user-guide/configuration.html)
- [Flink backpressure as a capacity signal](https://nightlies.apache.org/flink/flink-docs-release-2.3/docs/ops/monitoring/back_pressure/)
- [Ballista task slots and tuning](https://datafusion.apache.org/ballista/user-guide/tuning-guide.html)
