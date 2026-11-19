# docker-034: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-034.md`.

## Exercise 1: Predict whether image rollback reverses a schema change.

**Expected answer:** It does not automatically restore previous data.

**Why:** The image and volume have different lifetimes. A rollback that ignores the data format can replace one failure with another.

## Exercise 2: Identify migration preconditions.

**Expected answer:** Known schema version, exclusive or compatible writers and a verified backup.

**Why:** These conditions make the transition reviewable. Guessing the starting format can corrupt records that belong to a different version.

## Exercise 3: Design a v1-to-v2 synthetic record conversion.

**Expected evidence:** Preserve counter value and set a validated new schema version.

**Why:** Use a pure transformation on copied input first. Reject malformed records instead of silently guessing missing values.

## Exercise 4: Diagnose an old reader failing after deployment rollback.

**Expected answer:** The data format may have advanced beyond its compatibility.

**Why:** Inspect the stored version before restarting repeatedly. Restore or use a compatible reader according to the planned recovery procedure.

## Exercise 5: Explain atomic file replacement limits.

**Expected answer:** It avoids partial file visibility under stated local assumptions, not all concurrent-write races.

**Why:** Multiple writers can still overwrite each other’s valid updates without coordination. Name the lock and single-host assumptions.

## Exercise 6: Write a migration release plan.

**Expected evidence:** Preconditions, backup, transition, validation, compatible rollback and cleanup.

**Why:** The plan should be concrete enough to rehearse on a copy. A code tag change alone is not a data recovery strategy.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
