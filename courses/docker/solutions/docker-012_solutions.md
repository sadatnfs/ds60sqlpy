# docker-012: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

Readiness means the application can perform the work a dependent component needs. Process existence is weaker evidence. A server can be running while it initializes files, connects to a database or rejects requests. A health check periodically executes a small observation and classifies container health according to timing and failure rules.

Compose can wait for a dependency to become healthy before starting a dependent service. This improves startup ordering, but it is not a permanent dependency availability guarantee. The dependency can fail later. Applications still need bounded timeouts, useful error handling and appropriate reconnect behavior.

A useful health endpoint checks enough to represent readiness without performing expensive or destructive work. It should not mutate learner data or require a public internet service to declare a local classroom ready. Its failure should point to the missing capability, not trigger an unbounded retry loop.

The fixture’s health command uses Python’s standard-library HTTP client to request its own loopback `/healthz` endpoint with a timeout. `interval`, `timeout`, `retries` and `start_period` control repeated observations. The health command runs inside the container, so its loopback is the app’s loopback.

A dependent service may specify `depends_on: app: condition: service_healthy`. That describes an initial ordering condition. A check that only tests whether a PID exists is usually too weak for a web dependency; a check that queries an unrelated remote service may be unnecessarily strong and fragile.

## Exercise 1: Compare running and healthy.

A running process may not be ready. A healthy classification is only as meaningful as its check, so review what the command actually observes.

**Expected:** A lifecycle state versus a defined repeated behavioral check.

## Exercise 2: Predict which loopback the health command uses.

The command runs inside that container. It does not traverse the published host port, so host-browser acceptance remains a separate observation.

**Expected:** The app container network namespace.

## Exercise 3: Design a readiness endpoint for a file-backed teaching app.

Readiness should verify that the app can serve its intended role without creating records or depending on unrelated internet availability.

**Expected:** A bounded non-destructive test of required local capability.

## Exercise 4: Diagnose a healthy app with a broken host mapping.

The checks traverse different paths. Inspect the host port mapping and request destination rather than weakening a valid internal readiness check.

**Expected:** The internal readiness check can pass while browser access fails.

## Exercise 5: Explain a dependency crash after startup.

An initial condition can become false later. Clients need timeouts and failure handling that match whether retrying the specific operation is safe.

**Expected:** depends_on does not replace runtime recovery logic.

## Exercise 6: Write separate health and acceptance assertions.

The cheap periodic check should remain small. A fuller acceptance check proves features such as content, authentication or saved-state behavior that health may intentionally omit.

**Expected:** Health endpoint succeeds; user-facing response and persistence also satisfy their contracts.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
