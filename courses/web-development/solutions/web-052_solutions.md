# web-052: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-052.md`.

## Exercise 1: Explain atomicity without claiming every transaction is serializable.

**Expected answer:** Atomicity concerns all-or-nothing application; isolation is a separate property.

**Approach:** Define atomicity as all or nothing for one transaction's writes, and isolation as how concurrent transactions see each other's changes.

**Why:** Atomicity means all writes commit or none do; isolation, a separate property, governs interference between concurrent transactions.

**Plausible wrong approach:** Saying a transaction makes concurrent edits safe fails because lost updates can still occur under weaker isolation levels.

**How to verify:** Your explanation gives an example where a transaction commits atomically but still overwrites another editor's change. The example names the isolation property that would have prevented the overwrite.

## Exercise 2: Add a database constraint for nonnegative minutes.

**Expected evidence:** The database rejects invalid writes even if an application check is missed.

**Approach:** Add `CHECK (minutes >= 0)` to the column in the CREATE TABLE statement and insert a negative value directly with SQL.

**Why:** A database constraint rejects invalid rows even when a code path forgets the application check.

**Plausible wrong approach:** Relying only on the PHP validator fails because a script, migration or other client can write to the table without it.

**How to verify:** Inserting minutes of -5 raises a PDOException for the constraint, and the table has no new row.

## Exercise 3: Implement a version-checked update in a disposable database.

**Expected evidence:** The first expected version succeeds and the repeated stale version affects zero rows.

**Approach:** Prepare the guarded UPDATE, run it with the current version, then run it again with the old version, and read `rowCount()` each time.

**Why:** The first update matches the version and increments it, so the second, stale update matches zero rows.

**Plausible wrong approach:** Fetching the row, comparing versions in PHP, then updating without the predicate fails because another write can land between those steps.

**How to verify:** The counts are 1 then 0, and the stored minutes hold the first submitted value. The version column reads 4 afterward, one step above the starting value of 3.

## Exercise 4: Diagnose accepting a zero-row update as success.

**Expected answer:** Inspect affected-row evidence and handle the conflict explicitly.

**Approach:** Check `rowCount()` after the update and return a conflict result to the caller when it is 0.

**Why:** Zero affected rows means the expected version no longer exists, which is a conflict to report, not a success.

**Plausible wrong approach:** Treating no exception as success fails because a predicate that matches nothing is a normal completed statement in SQL.

**How to verify:** A stale update now returns a conflict message, while a current one returns success. The conflict branch also tells the editor to reload the plan before trying again.

## Exercise 5: Force a failure after a write and verify rollback.

**Expected evidence:** The stored value remains the pre-transaction value.

**Approach:** Begin a transaction, update the value, throw an exception, roll back in the catch block, and read the value again.

**Why:** rollBack discards uncommitted writes, so the stored value is the one from before the transaction.

**Plausible wrong approach:** Calling `rollBack()` after the connection already committed fails because there is no open transaction to undo.

**How to verify:** After the rollback, the stored minutes equal the value from before `beginTransaction()`. Calling `inTransaction()` after the rollback returns false, so nothing is left open.

## Exercise 6: Explain the limits of the single-connection concurrency demonstration.

**Expected answer:** It tests predicates and rollback, while real races require controlled concurrent integration tests on the target engine.

**Approach:** Note that one connection runs statements strictly in sequence, so it can test predicates but never real interleaving.

**Why:** Sequential statements test predicates and rollback, but real races need concurrent connections on the target database.

**Plausible wrong approach:** Citing the sequential demo as proof that parallel requests are safe fails because no two transactions overlapped.

**How to verify:** Your answer describes a test with two connections or processes on the target engine.

## Reference comparison

Open `courses/web-development/solutions/web-052_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
