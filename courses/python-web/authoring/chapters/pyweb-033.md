## Starting point and result

Two different problems often appear as duplicate requests. Competing clients can overwrite each other's updates, while a retry can repeat a command whose first result was lost. This chapter handles them separately with a resource version and an idempotency key, using real atomic SQL operations.

## Mechanism: compare versions and identify commands

Optimistic concurrency attaches a version to a resource representation. A client submits the version it observed, commonly through an If-Match precondition. The update changes the row only if its current version still matches. The database evaluates the predicate and mutation together, preventing a gap between checking and writing.

An idempotency key identifies one logical command. The service stores the key, a digest or canonical representation of the relevant input, and the resulting outcome in the same transaction as the effect. Repeating the same key and input returns the earlier result. Reusing the key with different input is a conflict, not permission to silently substitute a new command.

These mechanisms serve different purposes. A version belongs to mutable resource state; a command identity belongs to an attempted operation. Neither should be an unbounded global dictionary in a multi-worker service. The fixture uses SQLite transactions and bounded inputs to make the storage semantics inspectable.

## Worked case: reject a stale update

The first update supplies the current version and succeeds. A later update using the old version receives a precondition failure. A request without the required precondition receives a distinct refusal. The program checks both statuses and the stored value after the sequence.

The crucial SQL shape is an UPDATE with both identifier and expected version in its WHERE clause. A separate SELECT followed by an unconditional UPDATE would allow another writer to intervene. The affected-row count tells the application whether the conditional change occurred.

A missing row and a stale version may require different public handling depending on disclosure policy. The lesson keeps the fixture behavior explicit rather than implying that one status convention fits every API. Authorization must happen within the same resource scope as the update.

## Worked case: replay one command and reject conflicting reuse

The second case submits a command with an idempotency key, then repeats it. The database stores one effect, and the replay returns the recorded result. Reusing that key with a different payload receives a conflict response. The final row count verifies that no extra effect slipped through.

The fixture uses BEGIN IMMEDIATE to make its SQLite write ownership explicit. This is not a universal PostgreSQL recipe. A PostgreSQL implementation can use unique constraints, transaction retries and suitable locking or upsert semantics, but must preserve the same command/result invariant.

An idempotency record also needs a retention policy. Deleting it too soon can turn an old retry into a new effect. Keeping all keys forever without bounds creates another operational problem. The correct window depends on the client retry contract and the cost of duplicate effects.

## Failure diagnosis and discussion

**Does a timeout mean the command failed?** No. The response may have been lost after commit. Reconcile using the operation identity before issuing a logically new command.

**Why compare payloads when keys match?** Otherwise a client bug can reuse a key for a different operation and receive an unrelated result, hiding a serious semantic error.

If duplicate effects appear, inspect whether the key record and effect commit atomically. If stale writes succeed, inspect whether the version condition is inside the UPDATE itself. Continue with response contracts, which control what successful and failed operations expose to callers.
