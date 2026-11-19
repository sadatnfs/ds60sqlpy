# web-052: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-052.md`.

## Exercise 1: Explain atomicity without claiming every transaction is serializable.

**Expected answer:** Atomicity concerns all-or-nothing application; isolation is a separate property.

**Why:** Atomicity means all writes commit or none do; isolation, a separate property, governs interference between concurrent transactions.

## Exercise 2: Add a database constraint for nonnegative minutes.

**Expected evidence:** The database rejects invalid writes even if an application check is missed.

**Why:** A database constraint rejects invalid rows even when a code path forgets the application check.

## Exercise 3: Implement a version-checked update in a disposable database.

**Expected evidence:** The first expected version succeeds and the repeated stale version affects zero rows.

**Why:** The first update matches the version and increments it, so the second, stale update matches zero rows.

## Exercise 4: Diagnose accepting a zero-row update as success.

**Expected answer:** Inspect affected-row evidence and handle the conflict explicitly.

**Why:** Zero affected rows means the expected version no longer exists, which is a conflict to report, not a success.

## Exercise 5: Force a failure after a write and verify rollback.

**Expected evidence:** The stored value remains the pre-transaction value.

**Why:** rollBack discards uncommitted writes, so the stored value is the one from before the transaction.

## Exercise 6: Explain the limits of the single-connection concurrency demonstration.

**Expected answer:** It tests predicates and rollback, while real races require controlled concurrent integration tests on the target engine.

**Why:** Sequential statements test predicates and rollback, but real races need concurrent connections on the target database.

## Reference comparison

Open `courses/web-development/solutions/web-052_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
