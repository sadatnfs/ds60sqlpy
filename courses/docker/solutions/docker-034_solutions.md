# docker-034: explanatory solutions

These answers explain teaching fixtures, not engine results; the mechanism is in [the guide](../guides/docker-034.md).

## Exercise 1: Predict whether image rollback reverses a schema change.

**Expected answer:** It does not automatically restore previous data.

**Why:** The image and volume have different lifetimes. A rollback that ignores the data format can replace one failure with another.

**Approach:** Separate lifetimes: rolling back changes the image, while study-data keeps whatever format the new code wrote.

**Why this is correct:** The old reader accepts only schema_version 1, so data migrated to version 2 fails to load after rollback.

**A plausible wrong approach:** Planning to fix a bad migration by rolling back the image leaves the volume in a format the old code rejects.

**How to verify:** Roll back in a copy after migration and see read_counter raise on the new version.

## Exercise 2: Identify migration preconditions.

**Expected answer:** Known schema version, exclusive or compatible writers and a verified backup.

**Why:** These conditions make the transition reviewable. Guessing the starting format can corrupt records that belong to a different version.

**Approach:** Check three things first: the current schema_version, that only the migration will write during the change, and that a restored backup works.

**Why this is correct:** Knowing the format avoids misreading data, single-writer control avoids lost updates, and a tested backup allows recovery.

**A plausible wrong approach:** Assuming every record is version 1 and starting the migration risks corrupting records in some other format.

**How to verify:** Each condition has a recorded check: the version read, the writer list, and a restore test.

## Exercise 3: Design a v1-to-v2 synthetic record conversion.

**Expected evidence:** Preserve counter value and set a validated new schema version.

**Why:** Use a pure transformation on copied input first. Reject malformed records instead of silently guessing missing values.

**Approach:** Write a function that takes the v1 record, checks it, and returns a v2 record with the same counter and schema_version 2.

**Why this is correct:** Running it on copies first means mistakes affect test data only; rejecting bad input avoids guessing values.

**A plausible wrong approach:** Defaulting a missing counter to 0 hides damaged data as a valid reset.

**How to verify:** Feed it the worked example's record and a malformed one; the first keeps counter 7, the second is rejected.

## Exercise 4: Diagnose an old reader failing after deployment rollback.

**Expected answer:** The data format may have advanced beyond its compatibility.

**Why:** Inspect the stored version before restarting repeatedly. Restore or use a compatible reader according to the planned recovery procedure.

**Approach:** Read the stored schema_version before restarting the old reader again.

**Why this is correct:** If the stored version is newer than the reader supports, every restart fails the same way.

**A plausible wrong approach:** Restarting repeatedly hoping it is transient repeats the failure without new information.

**How to verify:** Restore the pre-migration backup or deploy a reader that accepts both versions, as the plan specifies.

## Exercise 5: Explain atomic file replacement limits.

**Expected answer:** It avoids partial file visibility under stated local assumptions, not all concurrent-write races.

**Why:** Multiple writers can still overwrite each other’s valid updates without coordination. Name the lock and single-host assumptions.

**Approach:** Read increment's sequence: write counter.next, then replace counter.json, all under a lock in one process.

**Why this is correct:** Replace makes readers see the old or new file whole, and the lock orders writers in that process only.

**A plausible wrong approach:** Assuming atomic replace makes two app containers on the same volume safe ignores that each has its own lock.

**How to verify:** The plan states the single-writer, single-host assumption next to the atomic write claim.

## Exercise 6: Write a migration release plan.

**Expected evidence:** Preconditions, backup, transition, validation, compatible rollback and cleanup.

**Why:** The plan should be concrete enough to rehearse on a copy. A code tag change alone is not a data recovery strategy.

**Approach:** Order the plan as preconditions, backup, migration, validation, a rollback that works with the new data, and cleanup of old compatibility.

**Why this is correct:** Each step can be rehearsed on a copy of study-data before touching the real volume.

**A plausible wrong approach:** Treating a new image tag as the plan leaves no way to recover data.

**How to verify:** Rehearse the plan on a restored copy and record each step's result before the real run.

## Check your transfer

The v1 reader rejects the v2 record, so restarting it will keep failing. Options are rolling forward with a fixed v2 image, running a tested v2-to-v1 conversion as a one-off job, or restoring the pre-migration backup and accepting the loss of later increments. Rolling forward keeps every write; the conversion does too if it is lossless; the backup does not. Whichever you choose, `/counter` returning the expected value confirms it. If v1 still exits after a correct downgrade, the record holds another incompatibility you have not found.
