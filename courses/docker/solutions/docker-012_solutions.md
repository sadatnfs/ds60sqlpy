# docker-012: explanatory solutions

These answers explain teaching fixtures, not engine results; the mechanism is in [the guide](../guides/docker-012.md).

## Exercise 1: Compare running and healthy.

**Expected answer:** A lifecycle state versus a defined repeated behavioral check.

**Why:** A running process may not be ready. A healthy classification is only as meaningful as its check, so review what the command actually observes.

**Approach:** Contrast the two states by their source: running comes from the process lifecycle, healthy from the healthcheck command passing on its interval.

**Why this is correct:** The fixture marks app healthy only after a python urllib request to /healthz succeeds, which requires the server to be listening.

**A plausible wrong approach:** Reporting running as ready fails during startup, because the container is running from the first instant, before the socket is bound.

**How to verify:** Watch docker compose ps right after up without --wait: the status shows starting first and then healthy.

## Exercise 2: Predict which loopback the health command uses.

**Expected answer:** The app container network namespace.

**Why:** The command runs inside that container. It does not traverse the published host port, so host-browser acceptance remains a separate observation.

**Approach:** Find where the check command runs: CMD in the healthcheck executes inside the app container, so 127.0.0.1 is that container's loopback.

**Why this is correct:** The probe targets 127.0.0.1:8080 directly, never the host mapping on 18080, so a healthy result says nothing about host publication.

**A plausible wrong approach:** Changing the probe to port 18080 makes the check fail permanently, since that port exists only on the host.

**How to verify:** Health stays healthy while the host request is tested separately with curl to 127.0.0.1:18080.

## Exercise 3: Design a readiness endpoint for a file-backed teaching app.

**Expected evidence:** A bounded non-destructive test of required local capability.

**Why:** Readiness should verify that the app can serve its intended role without creating records or depending on unrelated internet availability.

**Approach:** Check what the counter app needs to serve: a listener, and readable /data state. Probe both without writing anything.

**Why this is correct:** A GET that calls read_counter proves the volume is mounted and valid; it changes nothing and needs no internet.

**A plausible wrong approach:** Using POST /increment as the probe proves writes work but adds 1 to the learner's counter every five seconds.

**How to verify:** Over a minute of healthy status, GET /counter returns an unchanged value, showing the probe is non-destructive.

## Exercise 4: Diagnose a healthy app with a broken host mapping.

**Expected answer:** The internal readiness check can pass while browser access fails.

**Why:** The checks traverse different paths. Inspect the host port mapping and request destination rather than weakening a valid internal readiness check.

**Approach:** Trace both paths: the healthcheck runs inside the container, while the browser goes through the host port mapping.

**Why this is correct:** A wrong or missing ports: entry breaks only the host path, so healthy and unreachable can be true at once.

**A plausible wrong approach:** Removing or loosening the healthcheck because the browser fails throws away a correct signal and leaves the mapping broken.

**How to verify:** docker compose port app 8080 shows the wrong or missing mapping while health stays healthy; fixing the ports line restores the browser.

## Exercise 5: Explain a dependency crash after startup.

**Expected answer:** depends_on does not replace runtime recovery logic.

**Why:** An initial condition can become false later. Clients need timeouts and failure handling that match whether retrying the specific operation is safe.

**Approach:** Separate startup from runtime: condition: service_healthy gates only when client starts, not what happens to app afterward.

**Why this is correct:** Once client is running, Compose does not stop it if app later fails. The client's own timeout=3 call is what bounds a failure.

**A plausible wrong approach:** Expecting depends_on to restart or pause client when app crashes leaves no error handling for the real failure.

**How to verify:** Stop app while a long-lived client is running; the client sees connection errors that only its own retry or timeout logic can handle.

## Exercise 6: Write separate health and acceptance assertions.

**Expected evidence:** Health endpoint succeeds; user-facing response and persistence also satisfy their contracts.

**Why:** The cheap periodic check should remain small. A fuller acceptance check proves features such as content, authentication or saved-state behavior that health may intentionally omit.

**Approach:** Write two lists: the health assertion checks /healthz returns ready quickly, and acceptance checks GET / text, POST /increment and persistence across recreation.

**Why this is correct:** Health runs every 5s with a 3s timeout, so it must stay cheap. Acceptance runs once per change and can cover more behavior.

**A plausible wrong approach:** Putting the full acceptance flow into the healthcheck makes it slow and write-heavy, and may mark a working app unhealthy.

**How to verify:** Acceptance passes only when the message, the counter increment and the post-recreation value all match their contracts.

## Check your transfer

`depends_on` only orders startup; it does not watch the dependency afterwards, so no extra condition can cover a restart an hour later. The web service itself must handle a temporarily unavailable database, with bounded retries, timeouts and clear error responses while the database is down, and its own health check should report that state if traffic should stop. The expected result is a short period of controlled errors followed by recovery without a restart of the web container. Needing to restart the web service after every database restart would show that its reconnect logic is still missing.
