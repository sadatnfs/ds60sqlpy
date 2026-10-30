# docker-012: Health checks, startup order and real readiness

## Level and prerequisites

Beginner; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-011`

## Learning objectives

Design a readiness endpoint for a file-backed teaching app. Write separate health and acceptance assertions. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

Readiness means the application can perform the work a dependent component needs. Process existence is weaker evidence. A server can be running while it initializes files, connects to a database or rejects requests. A health check periodically executes a small observation and classifies container health according to timing and failure rules.

Compose can wait for a dependency to become healthy before starting a dependent service. This improves startup ordering, but it is not a permanent dependency availability guarantee. The dependency can fail later. Applications still need bounded timeouts, useful error handling and appropriate reconnect behavior.

A useful health endpoint checks enough to represent readiness without performing expensive or destructive work. It should not mutate learner data or require a public internet service to declare a local classroom ready. Its failure should point to the missing capability, not trigger an unbounded retry loop.

## Anatomy and a trace you can follow

The fixture’s health command uses Python’s standard-library HTTP client to request its own loopback `/healthz` endpoint with a timeout. `interval`, `timeout`, `retries` and `start_period` control repeated observations. The health command runs inside the container, so its loopback is the app’s loopback.

A dependent service may specify `depends_on: app: condition: service_healthy`. That describes an initial ordering condition. A check that only tests whether a PID exists is usually too weak for a web dependency; a check that queries an unrelated remote service may be unnecessarily strong and fragile.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

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

### Exercise 1: Compare running and healthy.

**Expected evidence:** A lifecycle state versus a defined repeated behavioral check.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Predict which loopback the health command uses.

**Expected evidence:** The app container network namespace.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Design a readiness endpoint for a file-backed teaching app.

**Expected evidence:** A bounded non-destructive test of required local capability.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose a healthy app with a broken host mapping.

**Expected evidence:** The internal readiness check can pass while browser access fails.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Explain a dependency crash after startup.

**Expected evidence:** depends_on does not replace runtime recovery logic.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Write separate health and acceptance assertions.

**Expected evidence:** Health endpoint succeeds; user-facing response and persistence also satisfy their contracts.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose a healthy app with a broken host mapping. Use its expected observation, The internal readiness check can pass while browser access fails., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/compose/how-tos/startup-order/)
- [Official reference 2](https://docs.docker.com/reference/compose-file/services/#healthcheck)

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
