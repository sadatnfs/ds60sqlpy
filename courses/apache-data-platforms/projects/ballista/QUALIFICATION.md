# Ballista qualification ledger

## Prepared environment

The supported actual route uses Ballista 54.1.0, DataFusion 54.0.0 and Arrow 23.0.1
on Python 3.12. Native Linux AMD64 and ARM64 wheel closures resolved with hashes.
The wheel requires glibc 2.39 or later. The explicit existing Swift/Noble-base image
was built and executed on native Linux ARM64. The normal pinned Trixie-base recipe
has descriptor evidence but was not runtime-qualified on this authoring machine.

## Actual Linux ARM64 acceptance

On 2026-10-27 the supported one-container route passed:

- Separate actual native scheduler/executor subprocess readiness and a separate
  Python client, without host ports or an engine socket in the container.
- Exact 200-order SQL aggregate versus an independent oracle and local DataFusion
  control: east has 100 rows, total 888; west has 100 rows, total 886.
- Source removal produced an actual empty listing, which the application rejected
  with its independent row-identity oracle. Canonical source stayed unchanged.
- Actual logical/physical plan capture, a hot-key aggregation, supported DataFrame
  action and bounded ordered output.
- One and two task-slot reconfigurations within the same fixed container allocation.
- Actual sole-executor outage, a bounded 45 second failed/unknown client receipt,
  reaping of that client, explicit native-process restart and a new request identity.
  No old query receipt was replayed.
- Exact same container after stop/resume, different container after down/start,
  unchanged source bytes and byte-identical pre-existing receipts after both.
  Evidence inspection did not execute saved requests.
- Confirmed deletion of only the synthetic owned container, network and volume
  after retaining the acceptance evidence outside maintained sources.

A health observer disconnect during reconfiguration previously caused BrokenPipe
to end the supervisor. Disconnect handling is fixed and covered by a regression;
the corrected source passed the task-slot, failure and lifecycle checks.

## Observed release limits

The released Python scheduler wrapper exposes its bind host but not the advertised
external host. Native default localhost broke executor callbacks in a three-container
attempt. Its actual failed source-bound receipt was retained. The supported route
therefore uses separate processes in one container namespace. It does not rewrite
DNS, claim cross-host shuffle or imply multi-executor high availability.

Scheduler state uses the wrapper's default backend. Saved receipts and immutable
source survival are qualified; durable scheduler job-history recovery and
transparent in-flight retry are not. Task-slot reconfiguration is quiescent and
restarts the native pair. A whole-container restart selects the one-slot default.

The native Rust extension remains a separately prepared source example, with
compilation and actual remote readback unqualified. Local runtime acceptance is
ARM64 only. AMD64 execution belongs to native GitHub runners, without local
emulation. No production capacity, performance or multi-host claim is made.
