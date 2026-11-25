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

The classroom saves `courses/docker/lessons/docker-041.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** Ask Compose for a second replica and read why it refuses: `docker compose -p ds60-docker-study up -d --scale app=2`. The second container is created but cannot start, and the error names the `127.0.0.1:18080` binding already held by the first, because a fixed host port can be bound by only one container. Run `docker compose -p ds60-docker-study ps -a` to see one running and one created container, then return to one replica with `docker compose -p ds60-docker-study up -d --scale app=1 --wait`, which removes the extra. Both would have mounted the same `study-data` volume, so trace on paper what two working replicas would do: each holds its own `LOCK`, each reads the same file, and each writes its own increment, which is the lost update from worked example 1.

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

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

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

Exercise 4 is this chapter's boundary case: Diagnose a fixed host-port collision. Read which replica holds the published host port and which replicas failed to start, then decide between a routing layer and distinct ports.

Even the fixture's careful write path hides a single-writer assumption: every writer stages its data in the same file name, `counter.next`, before `replace()` moves it into place. Two processes in separate containers sharing the volume can both write `counter.next`, after which the first `replace()` moves the other writer's bytes into place and the second fails with `FileNotFoundError` because the staging file is already gone. Its client sees the connection close without a response, alongside the lost updates. Atomic replacement is only as good as the uniqueness of its staging name and the exclusivity of its writer, so a scaled design needs unique temporary names and, more importantly, one owner or a transactional store.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** Name the requirement each of routing, shared data, sessions and retries adds when replicas increase.

**Transfer case.** A product owner wants three replicas of the study app behind a load balancer for a workshop of two hundred learners. What must change before that is safe, and what is the simplest correct alternative?

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

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
