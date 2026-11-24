# docker-041: Scaling replicas, shared state and concurrency traps

## Level and prerequisites

Advanced; about 120 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-040`

## Learning objectives

Design a replica-readiness checklist. Propose a correct scaled counter architecture. Use replica, shared state and race condition accurately when you explain what you observed.

## Purpose, vocabulary and mental model

A replica is another instance of an application role. More replicas can increase capacity or tolerate some process failures, but only if request routing and state design support them. Two processes writing the same local file can lose updates even when each performs an atomic file replacement.

The fixture counter is intentionally a single-process teaching app. Its in-process lock coordinates threads in that process. It does not coordinate separate containers. Scaling it without redesigning the storage protocol would violate its assumption. This is a useful example of knowing when a tutorial pattern stops being valid.

A load balancer distributes requests; it does not automatically synchronize application memory, sessions or files. State can move into a service designed for concurrent transactions, or the workload can be partitioned under an explicit ownership scheme. Both choices need tests for races, failures and retries.

### Key terms

- **Replica:** Another instance of the same application role, which adds capacity only if routing and state design allow it.
- **Shared state:** Data that several replicas read or write, such as one file or session store.
- **Race condition:** A defect where the outcome depends on the timing of concurrent operations.
- **Lost update:** A race where one writer's change overwrites another's because both read the same old value.
- **Load balancer:** A component that distributes requests among replicas but does not synchronize their memory, sessions or files.

## Anatomy and a trace you can follow

Compose can request several service instances, but a fixed published host port can collide across replicas. A proxy or another deliberate routing arrangement is needed. Do not run a scaling command against the fixture and assume the engine will infer the intended architecture.

Use a synthetic lost-update trace: two writers read 7, both compute 8, both replace the file, and the final count is 8 instead of 9. Each file write can be atomic while the read-modify-write transaction is not. This distinction connects container operations to concurrency and data modeling.

## How to use this lesson

The classroom displays this guide and saves your worksheet, `courses/docker/lessons/docker-041.md`. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example. **How to use the lessons** in the [subject README](../README.md) collects these rules in one place.

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

For each exercise, name the object involved and the phase of its lifetime before changing anything, then vary only the condition the task names. Exercises that ask you to predict, explain, compare or diagnose keep their answers in the solutions file; the others show the evidence to look for.

### Exercise 1: Predict the lost-update result.

**Hint:** Interleave two read-modify-write sequences that both start from 7.

### Exercise 2: Identify the scope of the fixture lock.

**Hint:** Ask what a threading lock protects across processes.

### Exercise 3: Design a replica-readiness checklist.

**Expected evidence:** Routing, state concurrency, sessions, resource budget and recovery.

**Hint:** List what each replica would share and what must change for it.

### Exercise 4: Diagnose a fixed host-port collision.

**Hint:** Count how many processes can bind one host port.

### Exercise 5: Explain why load balancing does not fix lost updates.

**Hint:** Ask whether spreading requests makes two updates happen in order.

### Exercise 6: Propose a correct scaled counter architecture.

**Expected evidence:** A transaction-capable shared store or explicit single-writer ownership.

**Hint:** Choose where increments are serialized: in a database or in one writer.

## Common mistakes and diagnosis

Scaling a service that keeps its state in local files. Relying on an in-process lock across containers. Publishing a fixed host port on a scaled service.

Exercise 4 is this chapter's boundary case: Diagnose a fixed host-port collision. Read which replica holds the published host port and which replicas failed to start, then decide between a routing layer and distinct ports. Preserve the original failure and the exact changed field before retrying. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations first. Name the requirement each of routing, shared data, sessions and retries adds when replicas increase. Then reconstruct worked example 2 (Separate scaling requirements) with one different value, predict what changes, and name which of replica, shared state, race condition and scaling the change touches.

When a host session ends, run `docker compose -p ds60-docker-study down` from your fixture copy. It removes the project's containers and network but keeps named volumes; deleting a volume is a separate, deliberate reset described in the fixture README.

## Primary references

- [docker compose up reference](https://docs.docker.com/reference/cli/docker/compose/up/)
- [Networking in Compose](https://docs.docker.com/compose/how-tos/networking/)

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
