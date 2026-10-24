# docker-034: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

A migration changes stored data or schema from one version to another. Replacing an application image can require such a change, but image rollback does not automatically reverse data migration. Code version and data version are related state machines with different reversibility.

A safe migration procedure identifies the starting schema, validates preconditions, creates a consistent backup, performs a bounded transition and verifies the new invariant. Concurrent old and new application instances complicate this because both may read or write the same data during replacement.

The fixture counter includes a schema_version field so learners can discuss this boundary without a full database. The course does not run destructive migrations on the main classroom’s progress store. Work on copied synthetic records and a separate disposable restore target.

An expand-and-contract approach first adds a compatible representation, allows both versions to work, migrates data and only later removes the old representation. It costs temporary complexity but can reduce deployment downtime. A tiny offline app may instead choose a documented maintenance window and an exclusive migration.

Atomic file replacement can prevent a partially written JSON file from appearing, but it is not a general distributed transaction. Define locking and single-writer assumptions explicitly. Backups and rollback commands must match the data protocol, not just the image tag.

## Exercise 1: Predict whether image rollback reverses a schema change.

The image and volume have different lifetimes. A rollback that ignores the data format can replace one failure with another.

**Expected:** It does not automatically restore previous data.

## Exercise 2: Identify migration preconditions.

These conditions make the transition reviewable. Guessing the starting format can corrupt records that belong to a different version.

**Expected:** Known schema version, exclusive or compatible writers and a verified backup.

## Exercise 3: Design a v1-to-v2 synthetic record conversion.

Use a pure transformation on copied input first. Reject malformed records instead of silently guessing missing values.

**Expected:** Preserve counter value and set a validated new schema version.

## Exercise 4: Diagnose an old reader failing after deployment rollback.

Inspect the stored version before restarting repeatedly. Restore or use a compatible reader according to the planned recovery procedure.

**Expected:** The data format may have advanced beyond its compatibility.

## Exercise 5: Explain atomic file replacement limits.

Multiple writers can still overwrite each other’s valid updates without coordination. Name the lock and single-host assumptions.

**Expected:** It avoids partial file visibility under stated local assumptions, not all concurrent-write races.

## Exercise 6: Write a migration release plan.

The plan should be concrete enough to rehearse on a copy. A code tag change alone is not a data recovery strategy.

**Expected:** Preconditions, backup, transition, validation, compatible rollback and cleanup.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
