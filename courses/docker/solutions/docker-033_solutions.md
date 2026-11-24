# docker-033: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-033.md`.

## Exercise 1: Predict a restart loop with invalid configuration.

**Expected answer:** The same failure can repeat without fixing its cause.

**Why:** Automatic restarts can mitigate transient failures but cannot make a malformed required value valid. Preserve the earliest useful error.

**Approach:** Ask whether a restart changes the cause: an invalid required value is read again the same way on every start.

**Why this is correct:** Each restart repeats the error, and the first log entry is the most useful one.

**A plausible wrong approach:** Adding an always-restart policy to make the service look up hides a permanent fault behind constant restarts.

**How to verify:** docker compose logs show the same error on each attempt, and fixing the value stops the loop.

## Exercise 2: Distinguish the two restart fields.

**Expected answer:** Container lifecycle policy versus dependency update behavior.

**Why:** Read the scope and documentation for each field. Similar words in different parts of the model do not imply identical semantics.

**Approach:** Read where each field sits: restart under app is a container policy; restart under depends_on.app controls whether client restarts when app is updated.

**Why this is correct:** Same word, different blocks, different meanings, as in the worked example's YAML.

**A plausible wrong approach:** Setting depends_on restart: true to make app restart after a crash edits the wrong field.

**How to verify:** docker compose config shows both fields in their blocks, and the documentation for each describes different triggers.

## Exercise 3: Design idempotent counter initialization.

**Expected evidence:** Create absent state once and validate existing state.

**Why:** Existing data should not be reset merely because the app process restarts. Invalid existing data should produce an explicit recovery decision rather than silent overwrite.

**Approach:** Follow read_counter: a missing counter.json means zero, nothing is written at startup, and existing files are validated.

**Why this is correct:** Starting twice writes nothing extra, and an invalid file raises ValueError rather than being replaced.

**A plausible wrong approach:** Writing a fresh counter.json at every start would reset real counts after each restart.

**How to verify:** Restart the app several times after increments; GET /counter returns the same value.

## Exercise 4: Diagnose duplicate records after repeated startup.

**Expected answer:** Initialization performs a non-idempotent side effect.

**Why:** Repair the initialization protocol and reconcile existing data. Increasing restart delays alone does not remove the duplication mechanism.

**Approach:** Find the code that adds data at startup and check whether it looks for existing data first.

**Why this is correct:** An unconditional append adds a copy per start, so restarts and duplicates rise together.

**A plausible wrong approach:** Lengthening the restart delay makes duplicates arrive more slowly but still arrive.

**How to verify:** After guarding the step, repeated starts leave the record count unchanged, and existing duplicates are removed by a reviewed cleanup.

## Exercise 5: Explain unknown write outcomes.

**Expected answer:** A timed-out client may not know whether the server committed.

**Why:** Blindly retrying can duplicate the action. Use an operation identity, queryable result or other explicit reconciliation design.

**Approach:** Consider a POST /increment whose response is lost: the server may have committed the new counter before the client timed out.

**Why this is correct:** The client cannot tell commit from failure, so blindly retrying may increment twice.

**A plausible wrong approach:** Retrying POST until one response arrives can skip a counter value.

**How to verify:** Read GET /counter before retrying, or add an operation ID so the server can recognize a repeat.

## Exercise 6: Define restart acceptance for a stateful app.

**Expected evidence:** Repeated starts preserve valid data and expose unrecoverable failures clearly.

**Why:** The test should cover both normal restarts and a controlled failure. A container continuously running says little about whether startup has corrupted its state.

**Approach:** Test both cases: restarts with valid data preserve the counter, and restarts with an invalid counter.json fail visibly.

**Why this is correct:** Both outcomes matter; one shows state survives, the other that corruption is not hidden.

**A plausible wrong approach:** Checking that the container shows Up says nothing about whether the counter is still right.

**How to verify:** The valid case keeps its value across restarts; the invalid case logs a ValueError and the file is left unchanged for recovery.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
