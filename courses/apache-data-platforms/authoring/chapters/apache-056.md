## Recovery needs data, schema and an operational boundary

A persistent container volume can retain a node's state across process replacement,
but it is not automatically a backup on another failure domain. A snapshot can
retain SSTable hardlinks at a point in time, but restoring useful data also needs
the compatible schema, version, permissions and topology assumptions. A backup
policy is incomplete until its chosen restore procedure has been exercised and
its result independently checked.

Repair reconciles replicas; it is not a substitute for an external backup.
Compaction reorganizes local storage; it is not a backup either. Hints can help
with some temporary replica unavailability, but do not cover every failure or
indefinite outage. Keeping these mechanisms separate makes a recovery plan easier
to evaluate when the system is under pressure.

The project first establishes local retained-volume recovery, then uses an
explicitly owned bounded restore target for its SSTable snapshot/import case.
It does not claim that three local containers or a snapshot directory on one
Docker engine survive destruction of that engine's disk. Moving state to another
machine requires a separately validated transfer and restore workflow.

## Worked case A: snapshot a known table and independently restore it

The source table contains exactly the known three synthetic orders. The snapshot
operation flushes as required by the chosen command and records a unique tag.
The experiment selects only this table's snapshot files, retains the exact schema
and copies the necessary SSTable components into a separate owned staging location.
It never imports arbitrary paths supplied through a classroom manifest.

A separate evidence table with the compatible key and column schema is created for the
restore. The node's supported import tool reads the staged SSTables, after which
the driver compares exact partition keys, clustering values, order identities and
amounts with the independent fixture oracle. An import tool returning success
without matching data is not a passed restore.

Staging files and the exact snapshot tag are removed only after their scope is
verified. The restored table and its receipt remain as evidence, bounded to four
targets per workshop until explicit confirmed project destruction. The original
retained orders are not truncated or dropped.
This is a bounded table-level restore experiment, not a full cluster disaster
recovery claim. System metadata, authorization, topology and a remote backup store
would require additional procedures and acceptance checks.

## Worked case B: replace a node container over retained state

The launcher stops and resumes the exact retained node container without pulling
or rebuilding its image. A fresh client checks the original orders and the defined
CQL behaviors again. Down then removes the owned container/network while retaining
its named state volume; start creates a replacement process that reads the same
orders and local database identity.

This tests a different boundary from an in-process reconnect. Configuration is
regenerated from the pinned release in temporary storage, while commitlog, SSTables,
caches, hints and logs remain on the owned volume. Image contents hold software,
not the learner's database state. The copied .env identifies the project and must
remain associated with the state it created.

Operational readback should include actual node status, schema agreement, pending
work and logs where the relevant tools support them. A healthy CQL endpoint alone
does not prove all repair or compaction work is complete. Conversely, a busy
maintenance task is not automatically a correctness failure if the service remains
within its stated operational contract.

## Diagnosis and interview discussion

Define recovery-point and recovery-time objectives before choosing backup frequency.
Record which writes are included, how snapshots and incremental data are retained,
where schema is stored, who can restore it, and how the restored result is checked.
A restore on the same machine is useful evidence, but a new-host exercise is
needed to qualify a different failure domain.

**Interview discussion: why is a successful backup command weaker than a recovery
plan?** It can produce files that are incomplete, inaccessible or incompatible
with the intended restore target. These cases require exact restored data and a
separate retained-volume replacement readback, while explicitly naming the remote
storage and whole-cluster guarantees that remain outside the local fixture.
