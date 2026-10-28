## A catalog commit must detect competing table state

Two writers can load the same table metadata and prepare different updates.
Without a conflict check, the later writer could replace the pointer and discard
the earlier writer's committed change. Iceberg uses optimistic concurrency: a
writer prepares an update, then commits subject to requirements about the state
it observed. A conflict means the client must reload and decide whether its
operation remains valid, not overwrite the newer metadata blindly.

A simplified compare-and-swap rule is
\(\mathrm{commit}(v_{old},v_{new})\) succeeds only if the catalog's current
version still matches the required old state. Actual Iceberg requirements are
more specific to operations and include schema, snapshot and other identities.
The model explains the reason for the boundary; the executable source uses real
PyIceberg catalog validation rather than implementing a substitute lock manager.

Conflict recovery is different from delivery retry. A client that never received
a commit response must determine whether its previous operation succeeded before
repeating a business append. Reloading the table can reveal new state, but it does
not by itself give every append an application-level idempotency key. Record source
operation identity and reconcile ambiguous outcomes when exact effects matter.

## Worked case A: reject a stale schema update

The program creates two handles to the same table. The first handle commits an
optional note field. The stale handle then tries to add a different field based
on its older schema. The prepared catalog rejects the stale update with an actual
CommitFailedException. The independent readback confirms that note exists and
the stale field does not.

This sequence is deterministic and needs no timing-dependent threads. It models
two clients by retaining separate real table handles, then deliberately orders
the commits. It demonstrates conflict detection, not simultaneous network failure,
distributed consensus or a benchmark of concurrent write throughput. Those claims
would require additional topology and measurements.

The original data remains readable after the rejection. A conflict must not be
handled by deleting the table or recreating its warehouse. Its files are not
corrupt merely because another writer advanced metadata. Diagnose the specific
requirement that failed and compare the intended operation with the new table
state.

## Worked case B: reload and revalidate the intended update

A fresh handle loads the committed note field, then adds reviewed as another
optional field. Both fields are present after this second successful commit.
The program verifies all field identities are unique and the original three
orders remain unchanged. This is a valid retry because the intended addition is
compatible with the newly observed schema.

A rename conflict can require a business decision instead. If another writer
renamed or removed the source field, blindly reapplying a textual operation might
change a different field or fail again. A retry policy must distinguish retryable
transport failures, optimistic conflicts, invalid requests and permanent access
errors. Exponential backoff reduces pressure but cannot decide semantic validity.

For append workflows, a safe recovery design may reuse already-written immutable
files after revalidation rather than rewrite all data. That depends on the actual
operation and writer support. Unreferenced files can remain after failed attempts;
their later cleanup must respect all retained snapshots and in-flight writers.
A conflict error is not permission for broad directory deletion.

## Diagnosis and interview discussion

Log the catalog identity, loaded table version, intended operation and exact
failure category. Keep application operation identifiers separate from snapshot
IDs. Bound retry count and preserve the final unknown outcome for reconciliation.
Never turn every exception into success or catch a conflict and silently drop
one writer's requested change.

**Interview discussion: why choose optimistic concurrency for analytical tables?**
Immutable data preparation can proceed without holding a long exclusive catalog
lock, while a short validated metadata commit resolves competing changes. The
tradeoff is explicit conflict handling and sometimes wasted preparation work.
These cases show both the rejected stale update and a reloaded, revalidated
success without inventing a global lock or claiming every operation is automatically
safe to replay.
