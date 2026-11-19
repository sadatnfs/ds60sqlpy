# docker-033: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-033.md`.

## Exercise 1: Predict a restart loop with invalid configuration.

**Expected answer:** The same failure can repeat without fixing its cause.

**Why:** Automatic restarts can mitigate transient failures but cannot make a malformed required value valid. Preserve the earliest useful error.

## Exercise 2: Distinguish the two restart fields.

**Expected answer:** Container lifecycle policy versus dependency update behavior.

**Why:** Read the scope and documentation for each field. Similar words in different parts of the model do not imply identical semantics.

## Exercise 3: Design idempotent counter initialization.

**Expected evidence:** Create absent state once and validate existing state.

**Why:** Existing data should not be reset merely because the app process restarts. Invalid existing data should produce an explicit recovery decision rather than silent overwrite.

## Exercise 4: Diagnose duplicate records after repeated startup.

**Expected answer:** Initialization performs a non-idempotent side effect.

**Why:** Repair the initialization protocol and reconcile existing data. Increasing restart delays alone does not remove the duplication mechanism.

## Exercise 5: Explain unknown write outcomes.

**Expected answer:** A timed-out client may not know whether the server committed.

**Why:** Blindly retrying can duplicate the action. Use an operation identity, queryable result or other explicit reconciliation design.

## Exercise 6: Define restart acceptance for a stateful app.

**Expected evidence:** Repeated starts preserve valid data and expose unrecoverable failures clearly.

**Why:** The test should cover both normal restarts and a controlled failure. A container continuously running says little about whether startup has corrupted its state.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
