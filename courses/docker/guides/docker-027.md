# docker-027: Intermediate capstone: a recoverable two-tier teaching system

## Level and prerequisites

Intermediate; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-026`

## Learning objectives

Build an independent restore demonstration. Write a beginner operator handoff. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

This capstone adds peer discovery, constrained execution and a recovery test to the first app. The system still fits on one page: app serves JSON and owns its counter volume; client observes app through service DNS; the browser observes the loopback-published endpoint. Keeping these paths small makes failures explainable.

A recoverable system is more than a system that restarts. It has an identified durable state, a consistency boundary, a backup, an independent restore target and a bounded procedure to regain useful behavior. A second-tier client must also handle a dependency being temporarily unavailable without replaying unsafe writes.

Your deliverable is a short operator guide plus evidence, not a collection of screenshots. A future reader should know which project the commands affect, which volume contains state, how to inspect a failure, and what they can remove without losing the retained counter.

## Anatomy and a trace you can follow

Work only in the copied fixture. Verify host and peer requests, record the non-root user and read-only configuration, export the stopped app’s counter, restore into a distinct target and compare. A deliberately wrong service port in a scratch client should fail with a bounded transport error.

Do not broaden the project into a real database cluster for this exercise. The purpose is to integrate mechanisms already learned, then clearly state the limitations that a database, public endpoint or multi-host deployment would add.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

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

### Exercise 1: Predict which resources are durable.

**Expected evidence:** Only the intended named volume and explicit backup files.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Change only the peer target port in a scratch copy.

**Expected evidence:** The request fails within its timeout while app remains healthy.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Build an independent restore demonstration.

**Expected evidence:** New target state equals the exported counter while source remains intact.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose a passing host request with failing peer request.

**Expected evidence:** Inspect service DNS, network attachment and internal target port.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Explain the limits of this single-engine design.

**Expected evidence:** No multi-host failover or database consistency guarantee is claimed.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Write a beginner operator handoff.

**Expected evidence:** Setup, evidence, failure diagnosis, backup/restore and scoped cleanup.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose a passing host request with failing peer request. Use its expected observation, Inspect service DNS, network attachment and internal target port., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/compose/how-tos/networking/)
- [Official reference 2](https://docs.docker.com/engine/storage/volumes/)

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
