# docker-041: Scaling replicas, shared state and concurrency traps

## Level and prerequisites

Advanced; about 120 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-040`

## Learning objectives

Design a replica-readiness checklist. Propose a correct scaled counter architecture. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

A replica is another instance of an application role. More replicas can increase capacity or tolerate some process failures, but only if request routing and state design support them. Two processes writing the same local file can lose updates even when each performs an atomic file replacement.

The fixture counter is intentionally a single-process teaching app. Its in-process lock coordinates threads in that process. It does not coordinate separate containers. Scaling it without redesigning the storage protocol would violate its assumption. This is a useful example of knowing when a tutorial pattern stops being valid.

A load balancer distributes requests; it does not automatically synchronize application memory, sessions or files. State can move into a service designed for concurrent transactions, or the workload can be partitioned under an explicit ownership scheme. Both choices need tests for races, failures and retries.

## Anatomy and a trace you can follow

Compose can request several service instances, but a fixed published host port can collide across replicas. A proxy or another deliberate routing arrangement is needed. Do not run a scaling command against the fixture and assume the engine will infer the intended architecture.

Use a synthetic lost-update trace: two writers read 7, both compute 8, both replace the file, and the final count is 8 instead of 9. Each file write can be atomic while the read-modify-write transaction is not. This distinction connects container operations to concurrency and data modeling.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

## Worked example / walkthrough

### Worked example 1: Trace a lost update

This table is synthetic and requires no engine activity.

```text
writer A reads 7; writer B reads 7
writer A writes 8; writer B writes 8
expected two increments: 9; observed final value: 8
```

**Expected observation:** Atomic replacement does not make the entire read-modify-write sequence transactional.

### Worked example 2: Separate scaling requirements

Review these before any real scale experiment.

```text
replicas -> routing with no fixed-port collision
shared data -> transactional or partitioned ownership
sessions -> deliberate cross-instance model
retries -> idempotency or outcome reconciliation
```

**Expected observation:** Adding process instances does not supply the missing protocols.

## Six progressive exercises

### Exercise 1: Predict the lost-update result.

**Expected evidence:** The final value can be 8 after two attempted increments.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Identify the scope of the fixture lock.

**Expected evidence:** Threads in one process, not multiple containers.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Design a replica-readiness checklist.

**Expected evidence:** Routing, state concurrency, sessions, resource budget and recovery.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose a fixed host-port collision.

**Expected evidence:** Several replicas cannot all bind the same host socket independently.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Explain why load balancing does not fix lost updates.

**Expected evidence:** Traffic distribution does not serialize shared-state transactions.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Propose a correct scaled counter architecture.

**Expected evidence:** A transaction-capable shared store or explicit single-writer ownership.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose a fixed host-port collision. Use its expected observation, Several replicas cannot all bind the same host socket independently., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/reference/cli/docker/compose/up/)
- [Official reference 2](https://docs.docker.com/compose/how-tos/networking/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-041: Scaling replicas, shared state and concurrency traps.
Read courses/docker/guides/docker-041.md and courses/docker/lessons/docker-041.md. Direct prerequisites: `docker-040`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
