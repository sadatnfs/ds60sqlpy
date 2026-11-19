# docker-033: Restart policies, failure loops and idempotent startup

## Level and prerequisites

Advanced; about 120 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-032`

## Learning objectives

Design idempotent counter initialization. Define restart acceptance for a stateful app. Use restart policy, crash loop and idempotent startup accurately when you explain what you observed.

## Purpose, vocabulary and mental model

A restart policy tells the engine when to restart an exited container. It is not a repair mechanism for an invalid configuration or corrupted data. A process that crashes on every startup can loop indefinitely, consuming resources and repeating side effects.

Idempotent startup means repeating initialization does not create duplicate or conflicting state. Creating a file exclusively and recognizing its existing valid form is different from appending a new seed record every time. Database migrations need their own concurrency and version rules rather than casual startup scripts.

The study fixture avoids an automatic endless restart loop so a learner can inspect failures directly. In another service, choose a restart policy according to operational intent and test both clean shutdown and crash behavior. Preserve logs and a clear failure condition rather than making the container appear perpetually recovering.

## Anatomy and a trace you can follow

Policies such as no, on-failure and unless-stopped have different lifecycle semantics. Their exact behavior also depends on successful startup conditions and manual stops. Compose’s dependency restart option is a separate feature from the container restart policy. Do not treat similarly named fields as interchangeable.

Before enabling automatic restart, verify the app’s initialization, bounded retries and data ownership. Retrying an HTTP read is different from retrying a write that may already have committed. Unknown outcome requires reconciliation, not blind replay.

## How to use this lesson

The classroom displays this guide and saves your worksheet, `courses/docker/lessons/docker-033.md`. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example. **How to use the lessons** in the [subject README](../README.md) collects these rules in one place.

## Worked example / walkthrough

### Worked example 1: Read two distinct restart concepts

This fragment illustrates the naming difference.

```yaml
services:
  app:
    restart: "no"
  client:
    depends_on:
      app:
        condition: service_healthy
        restart: true
```

**Expected observation:** The service restart policy and dependency update behavior are separate configuration mechanisms.

### Worked example 2: Trace an unsafe initializer

The corrected design uses an existence/version check and a safe write.

```text
unsafe: every start appends seed record
safe: inspect owned state -> validate version -> create only when absent -> serve
```

**Expected observation:** Repeated starts should not silently duplicate application data.

## Six progressive exercises

For each exercise, name the object involved and the phase of its lifetime before changing anything, then vary only the condition the task names. Exercises that ask you to predict, explain, compare or diagnose keep their answers in the solutions file; the others show the evidence to look for.

### Exercise 1: Predict a restart loop with invalid configuration.

**Hint:** Ask whether restarting changes the invalid configuration.

### Exercise 2: Distinguish the two restart fields.

**Hint:** Compare the restart key with the restart field under depends_on.

### Exercise 3: Design idempotent counter initialization.

**Expected evidence:** Create absent state once and validate existing state.

**Hint:** Make initialization check for existing state before creating it.

### Exercise 4: Diagnose duplicate records after repeated startup.

**Hint:** Ask what initialization does every time the container starts.

### Exercise 5: Explain unknown write outcomes.

**Hint:** Ask what the client knows when a timeout ends the request.

### Exercise 6: Define restart acceptance for a stateful app.

**Expected evidence:** Repeated starts preserve valid data and expose unrecoverable failures clearly.

**Hint:** Restart several times and check the data after each start.

## Common mistakes and diagnosis

Using a restart policy to hide a configuration error. Writing initialization that inserts data on every start. Assuming a timed-out write did not happen.

Exercise 4 is this chapter's boundary case: Diagnose duplicate records after repeated startup. Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status; an application request adds another layer, and a healthy container can still serve the wrong result. Preserve the original failure and the exact changed field before retrying. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here, using restart policy, crash loop, idempotent startup and backoff. Reconstruct worked example 2 (Trace an unsafe initializer) with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild, or why none of those operations applies to this mechanism.

When a host session ends, run `docker compose -p ds60-docker-study down` from your fixture copy. It removes the project's containers and network but keeps named volumes; deleting a volume is a separate, deliberate reset described in the fixture README.

## Primary references

- [Start containers automatically](https://docs.docker.com/engine/containers/start-containers-automatically/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-033: Restart policies, failure loops and idempotent startup.
Read courses/docker/guides/docker-033.md and courses/docker/lessons/docker-033.md. Direct prerequisites: `docker-032`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
