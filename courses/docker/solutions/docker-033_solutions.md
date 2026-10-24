# docker-033: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

A restart policy tells the engine when to restart an exited container. It is not a repair mechanism for an invalid configuration or corrupted data. A process that crashes on every startup can loop indefinitely, consuming resources and repeating side effects.

Idempotent startup means repeating initialization does not create duplicate or conflicting state. Creating a file exclusively and recognizing its existing valid form is different from appending a new seed record every time. Database migrations need their own concurrency and version rules rather than casual startup scripts.

The study fixture avoids an automatic endless restart loop so a learner can inspect failures directly. In another service, choose a restart policy according to operational intent and test both clean shutdown and crash behavior. Preserve logs and a clear failure condition rather than making the container appear perpetually recovering.

Policies such as no, on-failure and unless-stopped have different lifecycle semantics. Their exact behavior also depends on successful startup conditions and manual stops. Compose’s dependency restart option is a separate feature from the container restart policy. Do not treat similarly named fields as interchangeable.

Before enabling automatic restart, verify the app’s initialization, bounded retries and data ownership. Retrying an HTTP read is different from retrying a write that may already have committed. Unknown outcome requires reconciliation, not blind replay.

## Exercise 1: Predict a restart loop with invalid configuration.

Automatic restarts can mitigate transient failures but cannot make a malformed required value valid. Preserve the earliest useful error.

**Expected:** The same failure can repeat without fixing its cause.

## Exercise 2: Distinguish the two restart fields.

Read the scope and documentation for each field. Similar words in different parts of the model do not imply identical semantics.

**Expected:** Container lifecycle policy versus dependency update behavior.

## Exercise 3: Design idempotent counter initialization.

Existing data should not be reset merely because the app process restarts. Invalid existing data should produce an explicit recovery decision rather than silent overwrite.

**Expected:** Create absent state once and validate existing state.

## Exercise 4: Diagnose duplicate records after repeated startup.

Repair the initialization protocol and reconcile existing data. Increasing restart delays alone does not remove the duplication mechanism.

**Expected:** Initialization performs a non-idempotent side effect.

## Exercise 5: Explain unknown write outcomes.

Blindly retrying can duplicate the action. Use an operation identity, queryable result or other explicit reconciliation design.

**Expected:** A timed-out client may not know whether the server committed.

## Exercise 6: Define restart acceptance for a stateful app.

The test should cover both normal restarts and a controlled failure. A container continuously running says little about whether startup has corrupted its state.

**Expected:** Repeated starts preserve valid data and expose unrecoverable failures clearly.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
