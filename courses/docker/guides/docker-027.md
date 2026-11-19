# docker-027: Intermediate capstone: a recoverable two-tier teaching system

## Level and prerequisites

Intermediate; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-026`

## Learning objectives

Build an independent restore demonstration. Write a beginner operator handoff. Use service discovery, resource limits and recovery test accurately when you explain what you observed.

## Purpose, vocabulary and mental model

This capstone adds peer discovery, constrained execution and a recovery test to the first app. The system still fits on one page: app serves JSON and owns its counter volume; client observes app through service DNS; the browser observes the loopback-published endpoint. Keeping these paths small makes failures explainable.

A recoverable system is more than a system that restarts. It has an identified durable state, a consistency boundary, a backup, an independent restore target and a bounded procedure to regain useful behavior. A second-tier client must also handle a dependency being temporarily unavailable without replaying unsafe writes.

Your deliverable is a short operator guide plus evidence, not a collection of screenshots. A future reader should know which project the commands affect, which volume contains state, how to inspect a failure, and what they can remove without losing the retained counter.

## Anatomy and a trace you can follow

Work only in the copied fixture. Verify host and peer requests, record the non-root user and read-only configuration, export the stopped app’s counter, restore into a distinct target and compare. A deliberately wrong service port in a scratch client should fail with a bounded transport error.

Do not broaden the project into a real database cluster for this exercise. The purpose is to integrate mechanisms already learned, then clearly state the limitations that a database, public endpoint or multi-host deployment would add.

## How to use this lesson

The classroom displays this guide and saves your worksheet, `courses/docker/lessons/docker-027.md`. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example. **How to use the lessons** in the [subject README](../README.md) collects these rules in one place.

## Worked example / walkthrough

### Worked example 1: Observe both traffic paths

The peer request uses service DNS.

```sh
docker compose -p ds60-docker-study up -d --wait
docker compose -p ds60-docker-study --profile tools run --rm client
```

**Expected observation:** The browser and peer see the same public message through different endpoints.

### Worked example 2: Review the operational state machine

The backup and restore details are in the fixture README.

```text
ready -> quiesce writer -> export -> validate -> restore separate target -> verify -> resume
failure -> preserve logs -> identify phase -> targeted repair -> recheck
```

**Expected observation:** Each transition has a specific observation and an owned resource scope.

## Six progressive exercises

For each exercise, name the object involved and the phase of its lifetime before changing anything, then vary only the condition the task names. Exercises that ask you to predict, explain, compare or diagnose keep their answers in the solutions file; the others show the evidence to look for.

### Exercise 1: Predict which resources are durable.

**Hint:** List which resources survive docker compose down.

### Exercise 2: Change only the peer target port in a scratch copy.

**Expected evidence:** The request fails within its timeout while app remains healthy.

**Hint:** Change the port only in the client's request and leave the app unchanged.

### Exercise 3: Build an independent restore demonstration.

**Expected evidence:** New target state equals the exported counter while source remains intact.

**Hint:** Restore into a new volume and compare it with the source.

### Exercise 4: Diagnose a passing host request with failing peer request.

**Hint:** Compare the host's path to the app with the peer's path.

### Exercise 5: Explain the limits of this single-engine design.

**Hint:** List what fails if the engine host goes down.

### Exercise 6: Write a beginner operator handoff.

**Expected evidence:** Setup, evidence, failure diagnosis, backup/restore and scoped cleanup.

**Hint:** Write each step as a command plus the evidence that shows it worked.

## Common mistakes and diagnosis

Testing only from the host and missing a broken peer path. Restoring over the source volume. Claiming high availability from a single engine.

Exercise 4 is this chapter's boundary case: Diagnose a passing host request with failing peer request. Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status; an application request adds another layer, and a healthy container can still serve the wrong result. Preserve the original failure and the exact changed field before retrying. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here, using service discovery, resource limits, recovery test and release review. Reconstruct worked example 2 (Review the operational state machine) with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild, or why none of those operations applies to this mechanism.

When a host session ends, run `docker compose -p ds60-docker-study down` from your fixture copy. It removes the project's containers and network but keeps named volumes; deleting a volume is a separate, deliberate reset described in the fixture README.

## Primary references

- [Networking in Compose](https://docs.docker.com/compose/how-tos/networking/)
- [Volumes](https://docs.docker.com/engine/storage/volumes/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-027: Intermediate capstone: a recoverable two-tier teaching system.
Read courses/docker/guides/docker-027.md and courses/docker/lessons/docker-027.md. Direct prerequisites: `docker-026`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
