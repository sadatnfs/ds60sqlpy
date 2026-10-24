# docker-032: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

A minimal image may omit a shell, curl, a package manager or debugging tools. Their absence can reduce image size and unnecessary functionality, but it changes how you inspect failures. An application can be correct without a shell; an attempted `docker exec ... sh` failure may describe tooling, not the application.

Debugging should preserve the original artifact and evidence. Installing tools into a live container changes its writable layer and can hide the conditions that caused the failure. Prefer structured inspection, existing runtime libraries, bounded logs and an explicitly prepared diagnostic workflow.

A separate debug image or ephemeral diagnostic container can be useful when its permissions, network access and data exposure are deliberately scoped. It must not become an excuse to mount the whole host or attach to unrelated production workloads.

The fixture already has Python, so a short standard-library request can test HTTP without adding curl. Use container inspection for configuration and logs for application behavior. If you need a shell in a different project, verify that the selected image actually contains one.

Record whether each diagnostic ran inside the app container, a peer container or the host. The vantage point determines which DNS names, loopback address, files and permissions were observed.

## Exercise 1: Predict a missing-shell error in a minimal image.

The diagnostic command needs its own dependency. Do not conclude that the application is broken merely because a familiar tool is absent.

**Expected:** It may be expected image content, not an app crash.

## Exercise 2: Choose a prepared tool for one HTTP request.

Adding a new package is unnecessary for this bounded observation. Reuse a declared runtime while keeping timeout and output limits explicit.

**Expected:** Use Python already present in the fixture.

## Exercise 3: Create a vantage-point diagnosis table.

The table helps explain why one request works and another fails. It prevents applying a host-network fix to a container-loopback problem.

**Expected:** Host, peer and app observations with distinct address scopes.

## Exercise 4: Diagnose an interactive repair that cannot survive recreation.

Record the useful finding, then implement the repair in source and rebuild. Treat the altered live container as diagnostic state, not a release artifact.

**Expected:** The maintained image was never changed.

## Exercise 5: Explain why host filesystem mounts are excessive for this lab.

The fixture can be inspected through its own image, logs and volume. Broader mounts change authority without adding necessary evidence.

**Expected:** They expose data unrelated to the app diagnosis.

## Exercise 6: Write a repeatable minimal-image incident procedure.

A repeatable procedure works for another learner and preserves the original symptom. It should not depend on tools installed manually during a previous incident.

**Expected:** Preserve artifact, inspect state, run bounded prepared probes and test a source repair.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
