# docker-012: Health checks, startup order and real readiness

## Level and prerequisites

Beginner; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-011`

## Learning objectives

Design a readiness endpoint for a file-backed teaching app. Write separate health and acceptance assertions. Use health check, readiness and depends_on accurately when you explain what you observed.

## Purpose, vocabulary and mental model

Readiness means the application can perform the work a dependent component needs. Process existence is weaker evidence. A server can be running while it initializes files, connects to a database or rejects requests. A health check periodically executes a small observation and classifies container health according to timing and failure rules.

Compose can wait for a dependency to become healthy before starting a dependent service. This improves startup ordering, but it is not a permanent dependency availability guarantee. The dependency can fail later. Applications still need bounded timeouts, useful error handling and appropriate reconnect behavior.

A useful health endpoint checks enough to represent readiness without performing expensive or destructive work. It should not mutate learner data or require a public internet service to declare a local classroom ready. Its failure should point to the missing capability, not trigger an unbounded retry loop.

### Key terms

- **Health check:** A small command the engine runs on a schedule to classify a container as starting, healthy or unhealthy.
- **Readiness:** The point where an application can do the work a dependent component needs, which is stronger than its process existing.
- **`depends_on`:** The Compose setting that orders service startup and can wait for a named condition on a dependency.
- **`service_healthy`:** A `depends_on` condition that waits until the dependency's health check reports healthy before starting the dependent.
- **Startup order:** The sequence in which Compose starts services, which helps initialization but does not guarantee later availability.

## Anatomy and a trace you can follow

The fixture’s health command uses Python’s standard-library HTTP client to request its own loopback `/healthz` endpoint with a timeout. `interval`, `timeout`, `retries` and `start_period` control repeated observations. The health command runs inside the container, so its loopback is the app’s loopback. An image can also declare a default check with the Dockerfile instruction `HEALTHCHECK --interval=5s --timeout=3s CMD ["python", "-c", "..."]`; a Compose `healthcheck` overrides the image's values for that service.

A dependent service may specify `depends_on: app: condition: service_healthy`. That describes an initial ordering condition. A check that only tests whether a PID exists is usually too weak for a web dependency; a check that queries an unrelated remote service may be unnecessarily strong and fragile.

## How to use this lesson

The classroom saves `courses/docker/lessons/docker-012.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** Start the project and watch the health state change with `docker compose -p ds60-docker-study ps` during the first few seconds; it moves from `starting` to `healthy`. Read the recorded probe results with `docker inspect --format '{{json .State.Health}}'` on the app container ID from `ps -q app`. Then run the tools-profile client from the fixture README, whose `depends_on` condition waits for that healthy state before it starts. Finally, compare the internal and host paths by running the health command yourself through `exec` and requesting `/healthz` from the host on port 18080. Both succeed here; write down which network namespace each one used, since the exercises ask what happens when only one of them works.

## Worked example / walkthrough

### Worked example 1: Inspect the fixture readiness command

This is an illustrative Compose fragment.

```yaml
healthcheck:
  test:
    [
      "CMD",
      "python",
      "-c",
      "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=2).read()",
    ]
  interval: 5s
  timeout: 3s
  retries: 5
  start_period: 5s
```

**Expected observation:** A responding local health endpoint establishes app readiness according to this narrow check.

### Worked example 2: Express a dependency condition

The client is a separate short-lived observation role.

```yaml
depends_on:
  app:
    condition: service_healthy
```

**Expected observation:** The dependent service waits for app health at startup; later app failures still require client error handling.

## Six progressive exercises

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

### Exercise 1: Compare running and healthy.

**Hint:** Compare the State and Health fields in docker inspect.

### Exercise 2: Predict which loopback the health command uses.

**Hint:** Ask in which container the health command runs.

### Exercise 3: Design a readiness endpoint for a file-backed teaching app.

**Expected evidence:** A bounded non-destructive test of required local capability.

**Hint:** Check the capability the app needs without changing stored data.

### Exercise 4: Diagnose a healthy app with a broken host mapping.

**Hint:** Compare where the health check runs with where the browser connects.

### Exercise 5: Explain a dependency crash after startup.

**Hint:** Ask when depends_on is evaluated.

### Exercise 6: Write separate health and acceptance assertions.

**Expected evidence:** Health endpoint succeeds; user-facing response and persistence also satisfy their contracts.

**Hint:** Write one assertion for /healthz and one for the user-facing response.

## Common mistakes and diagnosis

Using a check that only proves a process exists. Making the health check call an external service, so the local app looks unhealthy when the internet is down. Expecting `depends_on` to keep a dependency available after startup.

Exercise 4 is this chapter's boundary case: Diagnose a healthy app with a broken host mapping. Run the healthcheck command from inside the container and the browser request from the host, then compare the two paths hop by hop.

Another mistake is a health check that is too eager in a slow-starting service. If a database takes forty seconds to initialize and the check allows five retries at five-second intervals with no start period, the container is marked unhealthy before it ever had a chance, and anything waiting on `service_healthy` gives up. The fix is to set `start_period` to cover normal initialization, during which failed probes do not count against the retry limit, and to keep the probe itself cheap and local so that it measures the service rather than the network.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** Say what `condition: service_healthy` waits for and what it cannot promise about a host browser request.

**Transfer case.** A web service depends on a database with `condition: service_healthy`. Startup works, but an hour later the database restarts and the web service returns errors for a minute. A teammate suggests adding a second `depends_on` condition. What is the actual fix?

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

## Primary references

- [Control startup order in Compose](https://docs.docker.com/compose/how-tos/startup-order/)
- [Compose file reference: healthcheck](https://docs.docker.com/reference/compose-file/services/#healthcheck)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-012: Health checks, startup order and real readiness.
Read courses/docker/guides/docker-012.md and courses/docker/lessons/docker-012.md. Direct prerequisites: `docker-011`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
