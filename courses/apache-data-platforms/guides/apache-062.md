# apache-062: Operations, recovery and data verification

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-061`, `apache-057`.

## Key terms

- **Deep store:** The durable storage where Pinot keeps copies of completed segments, separate from servers' local copies.
- **Health endpoint:** A narrow liveness check for one component. It does not prove that the expected schema, segments and rows are present.
- **Segment identity:** The names and metadata of the segments a table should serve, which a recovery check compares after restart.
- **Read-only verification:** A recovery check that queries the existing table and compares results with known source event identities without recreating or reingesting data.

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

## Worked examples

### Identity before and after a stop

```bash
cd work/pinot
bash run.sh identity
bash run.sh stop
bash run.sh resume
bash run.sh identity
```

Both identity reports should show the same container IDs, image IDs, segment names and exact order rows, because stop and resume keep the containers and their volumes. Identity is read-only, so it is safe to run as often as needed. If the second report has new container IDs, something replaced the containers; if the segment list is empty, the controller lost its ZooKeeper metadata and the next step is reading logs, not running initialize.

### Replace containers over retained volumes

```bash
cd work/pinot
bash run.sh identity
bash run.sh down
bash run.sh start
bash run.sh identity
```

Here the container IDs are expected to change while segment metadata and order rows stay the same, because down removes containers but keeps named volumes. That makes this the closer rehearsal for a host replacement. A segment that is listed but returns no rows usually means the server has not finished loading it from deep storage yet, so wait and query again before deciding data was lost. Running initialize here would push a fresh segment and hide exactly the retention failure this test is meant to detect.

### Compare broker results across the restart

```sql
SELECT
  id,
  region,
  amount
FROM
  ds60_orders
ORDER BY
  id
LIMIT 10
```

Save the full row list before stopping and compare it after resume and after replacement; all three should be (1, east, 4), (2, west, 9), (3, east, 7). A matching aggregate is weaker evidence than matching rows, since a lost row and a duplicated row can cancel out in a sum. Also compare the totalDocs field in the response; a doubled count with correct distinct IDs points to a segment that was pushed twice under different names.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Pinot apache-062 command notebook

Use these commands only from the copied owned Pinot project described in its README.
The classroom Markdown pad does not execute Docker commands.

```bash
bash run.sh identity
bash run.sh stop
bash run.sh resume
bash run.sh identity
bash run.sh down
bash run.sh start
bash run.sh identity
```

These are read-only identity observations. Never call initialize after stop/resume or replacement. Compare saved service IDs, image IDs, segment metadata and exact order rows; export evidence before explicit owned-data destruction.

Native service acceptance and each advanced extension have distinct entries in
`QUALIFICATION.md`. Source/configuration presence is not an observed service result.

## Primary references

- [Troubleshooting](https://github.com/pinot-contrib/pinot-docs/blob/latest/operate-pinot/troubleshooting/README.md)
- [Segment management](https://github.com/pinot-contrib/pinot-docs/blob/latest/operate-pinot/segment-management.md)
- [Pinned release](https://pinot.apache.org/download/)
