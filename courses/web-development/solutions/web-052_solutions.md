# web-052: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

A transaction groups operations into a unit that can commit or roll back. Atomicity means the unit is not partially applied when the transaction aborts under the database's contract. Constraints enforce invariants close to the stored data, where every writer must encounter them. Application checks alone can race when two requests read the same state and then both attempt an update.

Concurrency requires more than wrapping code in begin and commit. Isolation levels, locking and the chosen database determine what other transactions can observe. An optimistic update includes an expected version in its WHERE clause and checks the affected-row count. A zero-row update can mean the record changed or was not accessible; the application must decide how to report and retry safely.

Begin a transaction, perform related writes, commit only after all succeed, and roll back on failure if still in a transaction. Use a database CHECK or UNIQUE constraint where it expresses a durable invariant. The SQLite example demonstrates rollback and a version predicate in one connection; it does not simulate real parallel requests or qualify PostgreSQL isolation.

## Exercise 1: Explain atomicity without claiming every transaction is serializable.

Atomicity concerns all-or-nothing application; isolation is a separate property.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Add a database constraint for nonnegative minutes.

The database rejects invalid writes even if an application check is missed.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Implement a version-checked update in a disposable database.

The first expected version succeeds and the repeated stale version affects zero rows.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose accepting a zero-row update as success.

Inspect affected-row evidence and handle the conflict explicitly.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Force a failure after a write and verify rollback.

The stored value remains the pre-transaction value.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain the limits of the single-connection concurrency demonstration.

It tests predicates and rollback, while real races require controlled concurrent integration tests on the target engine.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
