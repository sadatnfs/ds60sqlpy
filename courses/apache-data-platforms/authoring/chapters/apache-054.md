## Expiration is a logical rule before it is reclaimed storage

A time-to-live attaches an expiration rule to stored data. Once expired, a value
should no longer appear as a live application result. Its underlying storage can
still contain metadata and tombstones until compaction and retention rules permit
cleanup. A read returning no row therefore establishes logical invisibility, not
physical byte erasure or immediate space reclamation.

A tombstone records deletion information so that older replicas or storage files
do not simply reintroduce a previous value during reconciliation. Removing that
information too early can allow stale data to reappear. Repair frequency, replica
availability, gc_grace_seconds and compaction policy therefore interact. Reducing
the grace period merely to make a tiny demo use less disk would teach the wrong
operational habit.

The project uses synthetic fixture keys and a bounded TTL observation. It does
not alter the cluster's garbage-collection grace policy or run aggressive storage
cleanup. Existing unexpected order data remains protected. The ephemeral TTL row
is deliberately separate from the retained orders used for lifecycle readback.

## Worked case A: observe a real TTL countdown and disappearance

The client inserts one transient row with TTL 5, reads the actual remaining TTL
and requires a positive value no greater than five seconds. It then polls under
a fifteen-second deadline until the row is no longer returned. The first read
proves that a live expiring value was observed; the later read establishes its
logical expiration rather than accepting an empty table from the beginning.

The deadline is larger than the nominal TTL to tolerate scheduling and request
latency on a shared local machine. It is not a claim about subsecond precision.
Client and server clock behavior also matter, so an application should not use
a tiny TTL as an exact financial or safety-critical timer without a much more
careful design.

TTL may apply at a finer granularity than an application's intuitive whole-row
object. Updating selected columns can change their expiration or leave other
columns visible according to the actual statement. A full production example
needs explicit column, collection and update semantics; this fixture uses a
single value column to keep the observed condition unambiguous.

## Worked case B: deletion is distinct from compaction and repair

An explicitly deleted synthetic key is no longer visible to the application,
but that result does not say every historical representation has vanished.
The chapter traces a replica that missed the delete, a repair window and the
risk of collecting deletion information before reconciliation. The real local
read checks logical deletion; the replica narrative explains a failure mechanism
and is not falsely labeled as an injected multi-node resurrection experiment.

Compaction rewrites selected SSTables and may discard obsolete versions when
its rules allow. Different workload shapes can favor different strategies,
including time-windowed patterns for appropriately designed expiring data.
Selecting a strategy requires write rate, update/deletion behavior, read patterns,
SSTable overlap and repair obligations. A strategy name is not a substitute for
that workload evidence.

Storage usage after expiration may remain high because files still contain other
live data, tombstones must be retained, compaction has not run, or snapshots keep
hardlinks to older files. Inspect each responsibility before interpreting disk
size as a failed TTL. Never delete individual SSTables or a Docker volume as a
shortcut while expecting the logical table to remain intact.

## Diagnosis and interview discussion

Record TTL at write, actual live read, expiration observation, relevant clocks,
repair schedule and retained snapshots. Separate current query visibility from
physical-byte inspection and backup retention. A privacy erasure requirement
needs a broader policy covering replicas, snapshots, exports and downstream data;
this synthetic expiration fixture makes no compliance guarantee.

**Interview discussion: why can deleted data reappear in a poorly operated
replicated system?** A replica can retain an older value while deletion information
is collected before reconciliation. The two cases explain why logical expiry,
tombstone retention, repair and physical cleanup are different mechanisms and
why a successful empty read alone cannot validate all four.
