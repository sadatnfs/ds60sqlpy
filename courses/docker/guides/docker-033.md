# docker-033: Restart policies, failure loops and idempotent startup

## Level and prerequisites

Advanced; about 120 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-032`

## Learning objectives

Design idempotent counter initialization. Define restart acceptance for a stateful app. Use restart policy, crash loop and idempotent startup accurately when you explain what you observed.

## Purpose, vocabulary and mental model

A restart policy tells the engine when to restart an exited container. It is not a repair mechanism for an invalid configuration or corrupted data. A process that crashes on every startup can loop indefinitely, consuming resources and repeating side effects.

Idempotent startup means repeating initialization does not create duplicate or conflicting state. Creating a file exclusively and recognizing its existing valid form is different from appending a new seed record every time. Database migrations need their own concurrency and version rules rather than casual startup scripts.

The study fixture avoids an automatic endless restart loop so a learner can inspect failures directly. In another service, choose a restart policy according to operational intent and test both clean shutdown and crash behavior. Preserve logs and a clear failure condition rather than making the container appear perpetually recovering.

### Key terms

- **Restart policy:** A rule telling the engine when to restart an exited container, such as on-failure or unless-stopped.
- **Crash loop:** Repeated restarts of a process that fails on every startup, consuming resources and repeating side effects.
- **Idempotent startup:** Initialization that can run again without creating duplicate or conflicting state.
- **Backoff:** A growing delay between restart attempts that limits how quickly a failing service is retried.

## Anatomy and a trace you can follow

Policies such as no, on-failure and unless-stopped have different lifecycle semantics. Their exact behavior also depends on successful startup conditions and manual stops. Compose’s dependency restart option is a separate feature from the container restart policy. Do not treat similarly named fields as interchangeable.

Before enabling automatic restart, verify the app’s initialization, bounded retries and data ownership. Retrying an HTTP read is different from retrying a write that may already have committed. Unknown outcome requires reconciliation, not blind replay.

## How to use this lesson

The classroom saves `courses/docker/lessons/docker-033.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** Watch a bounded failure loop in a scratch container: `docker run -d --name ds60-restart-demo --restart on-failure:3 --pull never ds60-docker-study:local python -c "import sys; print('starting'); sys.exit(3)"`. Wait about ten seconds, then read `docker inspect --format '{{.RestartCount}} {{.State.Status}} {{.State.ExitCode}}' ds60-restart-demo`: three restarts, status `exited`, exit code 3. `docker logs ds60-restart-demo` shows `starting` four times, once per attempt, and nothing about the cause, because restarting never addressed it. The attempts come quickly at first and then slow down, because the engine doubles its delay before each restart, starting at 100 milliseconds; a longer loop backs off much further, so a quiet container may still be waiting. Remove it with `docker rm ds60-restart-demo`. Then check the fixture's own startup: note `/counter`, run `docker compose -p ds60-docker-study restart app`, and read `/counter` again. The value is unchanged, since `main()` only creates the data directory if needed and validates the stored file; nothing is written until a `POST /increment` arrives.

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

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

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

Exercise 4 is this chapter's boundary case: Diagnose duplicate records after repeated startup. Count the seed records after each start and read the initializer to see whether it checks for existing state before writing.

The policies `restart: always` and `restart: unless-stopped` behave alike until the engine itself restarts. A container you stopped by hand with `docker stop` stays stopped under both while the engine runs, but after an engine or Docker Desktop restart, `always` starts it again and `unless-stopped` leaves it alone. Learners who stop a misbehaving lab service and then reboot are surprised to find it running and writing again. Choose `unless-stopped` when an operator's manual stop should stick, keep the fixture's default of no policy for teaching runs, and after any engine restart check `docker ps` before assuming that what you stopped is still stopped.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** Rewrite the unsafe initializer as the safe sequence from memory.

**Transfer case.** A client's `POST /increment` timed out, the client retried, and the counter rose by two. Was the retry wrong, and how would you tell what the server actually did?

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

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
