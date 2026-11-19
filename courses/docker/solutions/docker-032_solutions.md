# docker-032: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-032.md`.

## Exercise 1: Predict a missing-shell error in a minimal image.

**Expected answer:** It may be expected image content, not an app crash.

**Why:** The diagnostic command needs its own dependency. Do not conclude that the application is broken merely because a familiar tool is absent.

## Exercise 2: Choose a prepared tool for one HTTP request.

**Expected answer:** Use Python already present in the fixture.

**Why:** Adding a new package is unnecessary for this bounded observation. Reuse a declared runtime while keeping timeout and output limits explicit.

## Exercise 3: Create a vantage-point diagnosis table.

**Expected evidence:** Host, peer and app observations with distinct address scopes.

**Why:** The table helps explain why one request works and another fails. It prevents applying a host-network fix to a container-loopback problem.

## Exercise 4: Diagnose an interactive repair that cannot survive recreation.

**Expected answer:** The maintained image was never changed.

**Why:** Record the useful finding, then implement the repair in source and rebuild. Treat the altered live container as diagnostic state, not a release artifact.

## Exercise 5: Explain why host filesystem mounts are excessive for this lab.

**Expected answer:** They expose data unrelated to the app diagnosis.

**Why:** The fixture can be inspected through its own image, logs and volume. Broader mounts change authority without adding necessary evidence.

## Exercise 6: Write a repeatable minimal-image incident procedure.

**Expected evidence:** Preserve artifact, inspect state, run bounded prepared probes and test a source repair.

**Why:** A repeatable procedure works for another learner and preserves the original symptom. It should not depend on tools installed manually during a previous incident.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
