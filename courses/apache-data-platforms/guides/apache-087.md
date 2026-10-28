# apache-087: Capacity, costs and architectural tradeoffs

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-020`, `apache-049`, `apache-061`.

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

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Integration apache-087 complete worked notebook

Measure one actual supported path with source/image/native identity, input distribution, CPU/memory/storage/time definitions and sampling window. Keep configured limits and larger capacity forecasts distinct from measured values.

## Receipt fields and independent oracle

- Source revision/hashes and exact declared input IDs, values, schema and time units.
- Actual native platform, package/image identities and owned resource namespace.
- Selected table snapshot/version, source positions or process/lineage identity as appropriate.
- Positive result against an independent oracle and a typed negative observation.
- Read-only retained-state comparison after the selected lifecycle transition.
- Cleanup/evidence-storage result and any separate prepared or unavailable feature.

For the common three-order fixture, require IDs 1/2/3 with amounts 4/9/7, total 20,
east 11 and west 9. A later fourth west order of2changes current total to22 and west
to11while an earlier pinned snapshot remains unchanged. Do not use this simple
oracle to claim correctness for a different pipeline without defining its
deduplication, correction and visibility semantics.

Read the selected project README and qualification ledger before commands. The
classroom does not execute Docker commands in this Markdown pad. Prepared
configuration, unit policy fixtures, successful compilation and actual service
acceptance remain different observations. Never include credentials or signed URLs.

## Concrete source inspection

From the copied integration directory, with sibling project copies when selected:

```bash
docker info --format "{{.OSType}}/{{.Architecture}} {{.MemTotal}}"
docker system df
```

These inspections do not start or qualify a service. Execute only the chosen
project's complete documented owned route and retain its actual receipt.

## Primary references

- [Iceberg reliability and table state](https://iceberg.apache.org/docs/latest/reliability/)
- [Arrow data format](https://arrow.apache.org/docs/format/Columnar.html)
- [Flink stateful stream processing](https://nightlies.apache.org/flink/flink-docs-release-2.3/docs/concepts/stateful-stream-processing/)
- [Kafka delivery/transaction design](https://kafka.apache.org/44/design/design/)
- [Atlas API and metadata boundaries](https://atlas.apache.org/api/v2/index.html)
- [Delta Sharing protocol](https://github.com/delta-io/delta-sharing/blob/v1.4.1/PROTOCOL.md)
