# docker-041: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-041.md`.

## Exercise 1: Predict the lost-update result.

**Expected answer:** The final value can be 8 after two attempted increments.

**Why:** Both writers used the same old value. Atomic file visibility prevents partial bytes but not stale computations.

## Exercise 2: Identify the scope of the fixture lock.

**Expected answer:** Threads in one process, not multiple containers.

**Why:** A lock object in memory is not shared across isolated processes. State the assumption instead of extending it by analogy.

## Exercise 3: Design a replica-readiness checklist.

**Expected evidence:** Routing, state concurrency, sessions, resource budget and recovery.

**Why:** Each requirement can fail independently. A successful second process start does not prove the application is safely scalable.

## Exercise 4: Diagnose a fixed host-port collision.

**Expected answer:** Several replicas cannot all bind the same host socket independently.

**Why:** Introduce an intended routing layer or distinct ports for a controlled experiment. Do not disable isolation merely to make startup succeed.

## Exercise 5: Explain why load balancing does not fix lost updates.

**Expected answer:** Traffic distribution does not serialize shared-state transactions.

**Why:** The data store or application protocol must provide the necessary concurrency guarantees regardless of which replica receives the request.

## Exercise 6: Propose a correct scaled counter architecture.

**Expected evidence:** A transaction-capable shared store or explicit single-writer ownership.

**Why:** Defend the consistency and failure semantics. Test concurrent increments and unknown outcomes rather than presenting replica count as correctness evidence.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
