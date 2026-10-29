# Flink 2.3 Java and SQL workshop

This optional owned project runs released Apache Flink 2.3.0 on native Java 17.
It has one JobManager and one TaskManager on a private Docker network, with two
configured slots. Java sources compile against the prepared release libraries;
no host JDK, Maven or Python installation is required. Read the qualification
ledger for actual acceptance and any remaining prepared extensions.

The main classroom serves the lessons at its normal browser URL. This project
keeps Flink's administrative REST endpoint private and reports actual jobs, state,
outputs and metrics through its fixed CLI. Opening a lesson starts no service.

## Prepare the native toolchain and runtime

The reviewed `scala-jvm` classroom image supplies Java 17 and Python. From the
repository root, prepare it locally or reuse a matching published Hub release:

```bash
./classroom build --profile scala-jvm
```

For a published combined manifest, replace `yourname` with its publisher:

```bash
docker pull yourname/ds60sqlpy:1.1.0-worker-scala-jvm
docker tag yourname/ds60sqlpy:1.1.0-worker-scala-jvm ds60sqlpy-worker-scala-jvm:1.1.0
```

Docker selects the native architecture. The project verifies the actual local
image before preparation; it never silently emulates AMD64 on ARM. The combined
worker tag includes `worker-`. These commands pull/tag a base and never push it.

Copy the complete project into a fresh learner-owned directory:

```bash
mkdir -p work
cp -R courses/apache-data-platforms/projects/flink work/flink
cd work/flink
bash run.sh prepare --binary
bash run.sh start
```

The explicitly selected binary route builds `ds60-apache-flink-binary:2.3.0` from
the already-local Java 17 base. It downloads the exact 604,828,545-byte official
archive, verifies its published SHA512, validates archive paths/member bounds and
preserves license/notice files. Build progress is visible. No TLS verification is
disabled. The lock is in `binary-image/artifact-lock.json`.

This is a locally prepared image containing Apache's verified distribution. The
separately pinned official Flink image has native AMD64/ARM64 descriptors in the
course inventory; descriptor availability is a different gate from executing this
binary route. No packages or connector JARs are fetched during a job or lesson.
Allow additional engine disk for archive/extraction/image layers before preparing.

## Run complete bounded examples

```bash
bash run.sh check
bash run.sh check-sql
bash run.sh event-time
bash run.sh state
bash run.sh readback
```

The Java source case observes three running updates with exact order identities
and final totals east 11/west 9. Remote Flink SQL computes two final grouped rows
from the same order contract. The checker distinguishes result-update semantics,
compilation, actual terminal job state and exact data readback.

The controlled seven-command source assigns actual event timestamps and emits
explicit watermarks. Its window job accepts out-of-order input before watermark
2000, routes identified order 4 after closure to late output, and closes the
second window at watermark 4000. The keyed-state case verifies four updates,
three event-time timers, replacement of the prior deadline and state cleanup
before fresh activity. All timestamp units are milliseconds.

`src/WorkshopJobs.java` contains the actual transformations/sinks. The separately
implemented `TimelineSource.java` uses the supported nonblocking Source API,
explicit record/watermark commands and versioned bounded split state. It does
not implement a Python imitation of Flink scheduling or state.

## Recovery, state migration and pressure

```bash
bash run.sh checkpoint
bash run.sh savepoint
bash run.sh backpressure
bash run.sh readback
```

Checkpoint acceptance requires actual completed metadata and committed output
before the deliberate owned TaskManager interruption. The client is reconciled
against its existing job ID after restart; final source IDs and managed sum must
remain exact. A fresh unrelated successful job cannot satisfy this recovery gate.

The savepoint route stops a paced finite job with an explicit owned state point.
It requires the changed counter UID to fail the actual operator/state mapping
check without dropped-state permission, then restores the compatible graph with
parallelism two. The complete source-ID set and final total are independently
reconciled. Operator UID, state name/type, maximum parallelism, source cursor and
sink commit state belong to the migration contract.

The pressure job uses a declared finite payload and an artificial 10 ms downstream
delay. It records actual task backpressure measurements and still checks every
source ID. A sleep statement alone or one tiny timing does not qualify pressure
or production capacity. Read the ledger before treating a prepared extension as
an exercised path.

The separate Kafka workshop demonstrates real Kafka transaction visibility.
A Flink transactional Kafka sink needs its own compatible connector preparation,
checkpoint/timeouts and destination recovery evidence. This local file-sink
route does not silently install or qualify that additional integration.

## Saved work and exact resume

```bash
bash run.sh stop
bash run.sh resume
bash run.sh readback
```

Resume reuses the exact retained containers without building or pulling. Input,
compiled artifact versions, source-bound requests, finished files and receipts
live in the owned named volume. `.env` keeps the independent project identity.
Keep both; moving source alone to another Docker engine does not migrate state.

A completed action with the same execution source returns its stored receipt.
`readback` only inspects retained state and never submits a job. If an observation
or receipt save failed after a backend job completed, explicitly reconcile that
known job instead of replaying it:

```bash
bash run.sh reconcile
```

Unknown submissions are not automatically resubmitted. Earlier compiled artifacts
and request diagnostics remain available for inspection and rollback planning.
Changing code during unfinished work requires explicit reconciliation first.
The small fixture retains at most sixteen compiled artifacts and bounded receipts;
reaching a storage budget is an explicit diagnostic, not automatic history deletion.

The single JobManager uses its default non-HA backend. Whole-container restart
preserves completed files/receipts, but does not promise recovery of every active
job graph. Savepoint restore is a distinct explicit operation.

```bash
bash run.sh down
bash run.sh start
bash run.sh readback
```

Down removes owned containers/network while retaining the volume. Start can
replace containers after validating retained source identity. Java 17 requires
the reviewed module options supplied by this Flink release; the custom config
preserves them for client, JobManager and TaskManager initialization.

## Limits and scoped cleanup

The JobManager container has a 1 GiB memory limit and the TaskManager 1.5 GiB,
with bounded CPU, process and temporary storage. These are configured limits,
not measured peak requirements or a production sizing recommendation. No host
ports, Docker socket, cloud credentials or unrelated state are mounted.

```bash
bash run.sh status
bash run.sh logs
bash run.sh down
```

Only after deciding this disposable workshop state is no longer needed:

```bash
bash run.sh destroy --confirm-owned-data-loss
```

Every affected container, network and volume must match the saved ownership
labels. No global prune occurs. A PID-marked host lock serializes lifecycle/job
actions; inspect an interrupted owner before removing only its stale lock files.
