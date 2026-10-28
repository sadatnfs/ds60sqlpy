## Recovery must compare durable source and serving identities

Pinot state is distributed across coordination metadata, controller storage,
server segment storage and, for real-time tables, source-consumption state.
Keeping one directory is not automatically a complete recovery strategy.
Identify which components contain authoritative metadata, durable segment copies
and reconstructible caches before designing backup or replacement procedures.

The owned offline workshop separates coordination, controller, server and
staging volumes. A container image contains software; it does not contain the
learner's ingested table. The project's `.env` keeps the random ownership marker
and project identity associated with those volumes. Copying only the image to a
new machine does not transfer the data or establish a disaster-recovery plan.

A live health endpoint checks a narrow availability condition. Correct recovery
also requires the expected table schema, segment identity and exact row results.
Read-only identity checks must not initialize an empty table, replay ingestion
or overwrite an unexpected fixture. Otherwise a recovery test can accidentally
measure successful reconstruction from its test source rather than persistence.

## Worked case A: exact stop and resume

Initialize the three-order table once and save every service container identity,
image identity, table configuration and read-only query result. Stop the owned
services with the launcher, then resume. The resume path starts the exact saved
containers without build or pull. Compare their identities before accepting the
same IDs 1/2/3 and totals east 11, west 9.

Startup can require time for coordination membership and segment availability.
Poll under a finite deadline and retain the first failure diagnostics if the
service does not become queryable. Re-running initialization is not a health
check. A controller answering before a server finishes loading segments is an
example of partial readiness that a broker query can detect.

The result should include source and logical table identity as well as row values.
A coincidentally identical table created under another project would not prove
that the original owned state survived. The launcher verifies resource ownership
before changing any container, network or volume, preventing unrelated projects
from becoming convenient substitutes for a failed experiment.

## Worked case B: replace containers over retained volumes

Use down to remove only owned containers and network while keeping all state
volumes. Start creates replacement containers with the same pinned image and
saved project identity. Run only the read-only checker. Require different
container IDs, unchanged expected image identities and the original rows and
metadata. Export the evidence before any explicit data destruction.

This boundary is stronger than an in-process reconnect, yet weaker than losing
the Docker engine's disk. All four volumes still reside on one physical host.
A remote backup plan needs consistent metadata/segment transfer, access checks,
retention rules and a restore on an independent target. A three-row local
replacement cannot qualify that different failure domain.

Compare source identity sets rather than relying on throughput or a healthy
process count. If one ID is missing, inspect segment assignment and load errors.
If an ID is duplicated, inspect ingestion replay and overlapping publication.
If all results are unavailable, inspect coordination, controller and broker
connectivity before interpreting it as data loss.

## Diagnosis and interview discussion

Retain segment lists, query exceptions, source IDs, service identities and
ownership labels. State whether the incident caused loss, duplication, stale
results or temporary unavailability; those are different outcomes. Avoid deleting
volumes as a diagnostic step because that destroys both persistence and the
information needed to explain the failure.

**Interview discussion: why can a successful restart fail to prove recovery?** The
application may have regenerated its fixture, connected to another project or
only checked an open port. These cases require exact process reuse and then
replacement over retained state, with independent row-level readback and no
hidden initialization at either boundary.
