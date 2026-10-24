# docker-033: Restart policies, failure loops and idempotent startup

## Level and prerequisites

Advanced; about 120 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-032`

## Learning objectives

Design idempotent counter initialization. Define restart acceptance for a stateful app. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

A restart policy tells the engine when to restart an exited container. It is not a repair mechanism for an invalid configuration or corrupted data. A process that crashes on every startup can loop indefinitely, consuming resources and repeating side effects.

Idempotent startup means repeating initialization does not create duplicate or conflicting state. Creating a file exclusively and recognizing its existing valid form is different from appending a new seed record every time. Database migrations need their own concurrency and version rules rather than casual startup scripts.

The study fixture avoids an automatic endless restart loop so a learner can inspect failures directly. In another service, choose a restart policy according to operational intent and test both clean shutdown and crash behavior. Preserve logs and a clear failure condition rather than making the container appear perpetually recovering.

## Anatomy and a trace you can follow

Policies such as no, on-failure and unless-stopped have different lifecycle semantics. Their exact behavior also depends on successful startup conditions and manual stops. Compose’s dependency restart option is a separate feature from the container restart policy. Do not treat similarly named fields as interchangeable.

Before enabling automatic restart, verify the app’s initialization, bounded retries and data ownership. Retrying an HTTP read is different from retrying a write that may already have committed. Unknown outcome requires reconciliation, not blind replay.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

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

### Exercise 1: Predict a restart loop with invalid configuration.

**Expected evidence:** The same failure can repeat without fixing its cause.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Distinguish the two restart fields.

**Expected evidence:** Container lifecycle policy versus dependency update behavior.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Design idempotent counter initialization.

**Expected evidence:** Create absent state once and validate existing state.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose duplicate records after repeated startup.

**Expected evidence:** Initialization performs a non-idempotent side effect.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Explain unknown write outcomes.

**Expected evidence:** A timed-out client may not know whether the server committed.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Define restart acceptance for a stateful app.

**Expected evidence:** Repeated starts preserve valid data and expose unrecoverable failures clearly.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose duplicate records after repeated startup. Use its expected observation, Initialization performs a non-idempotent side effect., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/engine/containers/start-containers-automatically/)

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
