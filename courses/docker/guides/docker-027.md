# docker-027: Intermediate capstone: a recoverable two-tier teaching system

## Level and prerequisites

Intermediate; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-026`

## Learning objectives

Build an independent restore demonstration. Write a beginner operator handoff. Use service discovery, resource limits and recovery test accurately when you explain what you observed.

## Purpose, vocabulary and mental model

This capstone adds peer discovery, constrained execution and a recovery test to the first app. The system still fits on one page: app serves JSON and owns its counter volume; client observes app through service DNS; the browser observes the loopback-published endpoint. Keeping these paths small makes failures explainable.

A recoverable system is more than a system that restarts. It has an identified durable state, a consistency boundary, a backup, an independent restore target and a bounded procedure to regain useful behavior. A second-tier client must also handle a dependency being temporarily unavailable without replaying unsafe writes.

Your deliverable is a short operator guide plus evidence, not a collection of screenshots. A future reader should know which project the commands affect, which volume contains state, how to inspect a failure, and what they can remove without losing the retained counter.

### Key terms

- **Two-tier system:** An application tier that owns state plus a client tier that reaches it through service DNS.
- **Service DNS:** Lookup of a peer by its Compose service name, so the client survives the app container's address changing.
- **Resource limits:** Bounds on memory, CPU and processes that keep each service's execution constrained and predictable.
- **Restore target:** A separate, disposable volume or project that receives a backup during a recovery test.
- **Operator guide:** A short document naming the project, the state volume, inspection steps and what can be removed safely.

## Anatomy and a trace you can follow

Work only in the copied fixture. Verify host and peer requests, record the non-root user and read-only configuration, export the stopped app’s counter, restore into a distinct target and compare. A deliberately wrong service port in a scratch client should fail with a bounded transport error.

Do not broaden the project into a real database cluster for this exercise. The purpose is to integrate mechanisms already learned, then clearly state the limitations that a database, public endpoint or multi-host deployment would add.

## How to use this lesson

The classroom saves `courses/docker/lessons/docker-027.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** Rehearse the full recovery path once, writing one line per transition with the observation that let you move on. Start with `up -d --wait`, then request `/counter` from the host and run the `tools` client, so both paths are confirmed before you touch data. Perform one increment through `exec` as the README shows, stop the writer, export with the README's `run --rm --no-deps` command into `counter-backup.json`, and check that the file's counter equals the value you just saw. Create and fill the separate `ds60-docker-study-restore` volume with the README's three commands, ending with the read-only verify, then start the app again and read `/counter` from the source. Both numbers should match the backup. Finish by removing only the restore volume and the backup file, and note in your record that `study-data` was never a restore target.

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

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

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

Exercise 4 is this chapter's boundary case: Diagnose a passing host request with failing peer request. Send the same request from the host and from a peer container, then compare the host mapping with the service name and internal port the peer used.

A healthcheck looks like self-healing, yet plain Docker and Compose only report health. When `/healthz` starts failing, `docker compose ps` shows the app as `unhealthy`, but no restart follows: the fixture sets no restart policy, and even a policy reacts to the process exiting, not to a failed probe. The `depends_on` condition `service_healthy` is likewise a check Compose makes when it starts the client; it does not watch the app afterward or repair it. Treat `unhealthy` as a signal someone must act on. Read `docker inspect --format '{{json .State.Health}}'` on the app container for the recent probe output, then decide between a targeted fix and a recreate.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** Draw the recovery state machine and mark where a failure stops the sequence.

**Transfer case.** After the rehearsal, `/counter` on the source shows 5 while the read-only verify of `ds60-docker-study-restore` shows 4. Is the restore broken, and which observation decides?

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

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
