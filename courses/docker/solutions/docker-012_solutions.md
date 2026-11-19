# docker-012: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-012.md`.

## Exercise 1: Compare running and healthy.

**Expected answer:** A lifecycle state versus a defined repeated behavioral check.

**Why:** A running process may not be ready. A healthy classification is only as meaningful as its check, so review what the command actually observes.

## Exercise 2: Predict which loopback the health command uses.

**Expected answer:** The app container network namespace.

**Why:** The command runs inside that container. It does not traverse the published host port, so host-browser acceptance remains a separate observation.

## Exercise 3: Design a readiness endpoint for a file-backed teaching app.

**Expected evidence:** A bounded non-destructive test of required local capability.

**Why:** Readiness should verify that the app can serve its intended role without creating records or depending on unrelated internet availability.

## Exercise 4: Diagnose a healthy app with a broken host mapping.

**Expected answer:** The internal readiness check can pass while browser access fails.

**Why:** The checks traverse different paths. Inspect the host port mapping and request destination rather than weakening a valid internal readiness check.

## Exercise 5: Explain a dependency crash after startup.

**Expected answer:** depends_on does not replace runtime recovery logic.

**Why:** An initial condition can become false later. Clients need timeouts and failure handling that match whether retrying the specific operation is safe.

## Exercise 6: Write separate health and acceptance assertions.

**Expected evidence:** Health endpoint succeeds; user-facing response and persistence also satisfy their contracts.

**Why:** The cheap periodic check should remain small. A fuller acceptance check proves features such as content, authentication or saved-state behavior that health may intentionally omit.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
