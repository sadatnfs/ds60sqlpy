# Flink qualification ledger

## Prepared environment

The explicit binary route installs the official Flink 2.3.0 Scala 2.12
release into the already-local reviewed Java 17 classroom base. The installer
checks the exact archive length and published SHA512 before bounded, path-checked
extraction. It retains upstream licenses and notices. Preparation does not disable
TLS, silently emulate another architecture or download dependencies during jobs.

The authoring machine built and exercised this route on native Linux ARM64 with
Java 17.0.21. The separately inventoried official image has AMD64/ARM64 descriptors;
manifest availability does not establish runtime acceptance of that other route.
Native AMD64 execution remains a separate native-runner gate.

## Actual native Linux ARM64 acceptance

The local qualification on 2026-10-27 exercised:

- Flink REST version 2.3.0, one actual registered TaskManager and two useful slots,
  with one JobManager and one TaskManager on a private Docker network.
- Compilation of the real Java sources against the prepared release libraries;
  three identified running updates with final east 11/west 9 totals.
- Actual remote Flink SQL with exactly two final groups from the same source.
- Real event timestamps and explicit watermarks from the nonblocking Source API,
  three expected window results and identified order 4 in late output.
- Four managed keyed-state updates, three event-time timers, replacement of the
  prior deadline and cleared state before the next east activity.
- An actual completed checkpoint with committed output before the deliberate
  interruption of the exact owned TaskManager. The same job reported a restored
  checkpoint and finished with all 100 source IDs exactly once and total 5050.
- An actual stop/savepoint, rejection specifically at changed-UID state mapping,
  unchanged earlier files after that rejection, and compatible restoration at
  parallelism two with the same complete ID and final-total oracle.
- A finite 500-record, 8192-byte-payload pressure experiment with a separate slow
  consumer, complete identified output and positive actual producer backpressure
  counters. The first accepted observation recorded 5,137 accumulated milliseconds;
  that is an observation for this run, not a machine-capacity promise.

The formatted final sources were exercised again. Independent fixture, state,
request/no-replay, archive-path, receipt-storage and metric-selection regressions
also passed. Policy tests and actual service observations remain separate evidence.

## Discovered contracts and retained failed observations

The custom configuration originally omitted the selected release's Java 17 module
options, which caused a client initialization failure. The project now preserves
the reviewed options shipped with this exact release. It does not work around the
failure by changing Java arbitrarily or disabling access checks globally.

The batch SQL job can finish successfully without exposing a streaming checkpoint
endpoint. Its observer now checks actual batch completion and exact rows without
requiring that unrelated endpoint. Explicit reconciliation finalized the known job
without submitting it again.

Pacing a downstream map did not ensure useful checkpoint state before a fast
source had already emitted everything. The recovery gate correctly rejected the
missed interruption window. The corrected route uses the bundled nonblocking
DataGeneratorSource rate limiter and requires both actual completed metadata and
committed records before interruption. A later trial restored state but exhausted
a short restart window before the TaskManager registered again. The reviewed
configuration now has a bounded six-attempt, five-second fixed-delay policy.
Earlier failed observations and request identities were retained.

A live gauge observation can miss a short pressure interval. The project also
reads the actual completed producer vertex's accumulated backpressure counter.
A configured sleep alone never passes this gate. A failed observer is reconciled
against its known completed job and retained output rather than replayed.

## Persistence and scope

Source-bound requests, versioned compiled artifacts, immutable receipts and finished
results live in the owned named volume. Exact-container resume and replacement
container acceptance compare their bytes and run the completed actions as saved
readback without submitting jobs. Only owned synthetic workshop resources are
deleted after evidence export; original classroom volumes are preserved.

The single JobManager is not configured for HA. Completed data and receipt
persistence do not promise recovery of arbitrary active jobs after whole-cluster
replacement. The checkpoint gate interrupts the TaskManager, and the savepoint
gate is an explicit compatible-state operation.

The file-sink recovery result does not qualify a transactional Kafka connector,
external object store, multi-host availability, arbitrary serializer migration or
production capacity. Those integrations require compatible separately prepared
components and their own actual failure/recovery evidence.
