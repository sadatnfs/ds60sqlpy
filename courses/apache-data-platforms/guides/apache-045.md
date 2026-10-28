# apache-045: Streams, operators and a running job

Tutorial mode. Stage: intermediate. Direct prerequisites: `apache-008`, `apache-004`, `java-001`.

## A stream job is an execution graph

Flink executes a job as connected sources, transformations and sinks. A source
produces records; operators transform or maintain state over them; sinks make
results visible outside the graph. The JobManager coordinates a job and its
checkpoints, while TaskManagers execute its subtasks. A Java client constructs
and submits the graph but is not necessarily the process that performs the work.

Boundedness describes whether a source eventually finishes. A bounded file can
be processed through streaming operators, and a table query can represent a
continuously changing result. Execution mode and API syntax are therefore separate
choices. Do not assume Java means streaming, SQL means batch, or a small input
means all work happened locally in the client.

The [Flink workshop](../projects/flink/README.md) prepares released Flink 2.3.0
on a native Java 17 environment. It uses one owned JobManager and one TaskManager
on a single Docker host. This is actual Flink execution with bounded fixtures,
not a Python model of a scheduler. The selected topology has no JobManager high
availability or cross-machine recovery claim.

## Worked case A: submit a bounded Java stream

The first source contains three identified orders: east amount 4, west amount 9,
and east amount 7. The Java program reads the prepared fixture, keys records by
region and maintains a running total. Its sink writes bounded source-bound output
that the independent checker reconciles to the original IDs and final region
totals, east 11 and west 9. The job must actually reach a terminal successful state;
client submission alone is not accepted as execution evidence.

A running aggregate can emit several updates for one key. The first east record
produces one partial total and the later east record advances it. Those updates
are not duplicate final table rows. They are an observable stream of state changes.
The complete example keeps identifiers and update semantics visible instead of
silently treating every emitted line as a separate independent business fact.

The project separates source files, compiled job artifacts, service processes,
result files and receipts. Compiling the JAR validates syntax and linkage against
the selected libraries; submitting it validates another boundary; inspecting exact
output validates its data behavior. Each can fail for a different reason, and
none should be replaced with an unlabelled local fallback.

## Worked case B: ask the same question through Flink SQL

The SQL case registers the same logical order contract and runs a bounded grouped
query. It writes final rows for east and west, which must equal the independent
sum oracle. The result has two final groups even though the stream case can expose
three incremental updates. This difference illustrates result semantics rather
than a disagreement about the source amounts.

A Table API or SQL planner can choose physical operators that differ from the
handwritten Java graph. The user still needs compatible connectors, formats,
source visibility and sink commit behavior. A supported SQL keyword does not
prove that an arbitrary external connector JAR is installed. The base workshop
uses prepared local files and included format/runtime components only.

The client and workers see one explicitly shared source location. A path that
exists only in the client would not become visible to TaskManagers merely because
it appears in a submitted plan. The launcher and configuration make these mounts
and service addresses explicit, following the earlier data-visibility and network
namespace chapters.

## Diagnosis and interview discussion

Inspect client compilation, submission response, actual job state, TaskManager
registration and data readback separately. Keep the selected Java and Flink
versions in the receipt. A healthy REST endpoint does not establish that the job
had a slot, completed its sink or produced the intended population.

**Interview discussion: what changes when moving from a stream of updates to a
final SQL table?** The result contract changes: intermediate changes can be
represented as inserts, updates or retractions, while a bounded final table
contains the final grouped values. These two actual execution routes use one
small source to make that distinction precise before introducing event time,
state recovery and external transactional sinks.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Real Flink stream and SQL entry points

From the repository root, copy the complete project into a fresh owned directory.
Prepare the native Java17 base and selected pinned runtime as documented there.

```bash
mkdir -p work
cp -R courses/apache-data-platforms/projects/flink work/flink
cd work/flink
bash run.sh prepare --binary
bash run.sh start
bash run.sh check
bash run.sh check-sql
bash run.sh readback
```

The code is compiled inside the prepared container; no host Java, Maven or SDK is
required. The check distinguishes compilation, actual submitted job completion,
exact source identity and output rows. See the qualification ledger before
interpreting a prepared extension as an exercised runtime path.

## Primary references

- [Flink DataStream overview](https://nightlies.apache.org/flink/flink-docs-release-2.3/docs/dev/datastream/overview/)
- [Flink architecture](https://nightlies.apache.org/flink/flink-docs-release-2.3/docs/concepts/flink-architecture/)
