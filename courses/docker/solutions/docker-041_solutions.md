# docker-041: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

A replica is another instance of an application role. More replicas can increase capacity or tolerate some process failures, but only if request routing and state design support them. Two processes writing the same local file can lose updates even when each performs an atomic file replacement.

The fixture counter is intentionally a single-process teaching app. Its in-process lock coordinates threads in that process. It does not coordinate separate containers. Scaling it without redesigning the storage protocol would violate its assumption. This is a useful example of knowing when a tutorial pattern stops being valid.

A load balancer distributes requests; it does not automatically synchronize application memory, sessions or files. State can move into a service designed for concurrent transactions, or the workload can be partitioned under an explicit ownership scheme. Both choices need tests for races, failures and retries.

Compose can request several service instances, but a fixed published host port can collide across replicas. A proxy or another deliberate routing arrangement is needed. Do not run a scaling command against the fixture and assume the engine will infer the intended architecture.

Use a synthetic lost-update trace: two writers read 7, both compute 8, both replace the file, and the final count is 8 instead of 9. Each file write can be atomic while the read-modify-write transaction is not. This distinction connects container operations to concurrency and data modeling.

## Exercise 1: Predict the lost-update result.

Both writers used the same old value. Atomic file visibility prevents partial bytes but not stale computations.

**Expected:** The final value can be 8 after two attempted increments.

## Exercise 2: Identify the scope of the fixture lock.

A lock object in memory is not shared across isolated processes. State the assumption instead of extending it by analogy.

**Expected:** Threads in one process, not multiple containers.

## Exercise 3: Design a replica-readiness checklist.

Each requirement can fail independently. A successful second process start does not prove the application is safely scalable.

**Expected:** Routing, state concurrency, sessions, resource budget and recovery.

## Exercise 4: Diagnose a fixed host-port collision.

Introduce an intended routing layer or distinct ports for a controlled experiment. Do not disable isolation merely to make startup succeed.

**Expected:** Several replicas cannot all bind the same host socket independently.

## Exercise 5: Explain why load balancing does not fix lost updates.

The data store or application protocol must provide the necessary concurrency guarantees regardless of which replica receives the request.

**Expected:** Traffic distribution does not serialize shared-state transactions.

## Exercise 6: Propose a correct scaled counter architecture.

Defend the consistency and failure semantics. Test concurrent increments and unknown outcomes rather than presenting replica count as correctness evidence.

**Expected:** A transaction-capable shared store or explicit single-writer ownership.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
