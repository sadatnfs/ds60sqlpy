# docker-041: explanatory solutions

These answers explain teaching fixtures, not engine results; the mechanism is in [the guide](../guides/docker-041.md).

## Exercise 1: Predict the lost-update result.

**Expected answer:** The final value can be 8 after two attempted increments.

**Why:** Both writers used the same old value. Atomic file visibility prevents partial bytes but not stale computations.

**Approach:** Step through the worked example: both writers read 7 before either writes, and both compute 8.

**Why this is correct:** Each write is atomic, so the file always holds a whole value, but both writes say 8, leaving one increment lost.

**A plausible wrong approach:** Expecting 9 because each write is atomic confuses complete writes with ordered read-modify-write.

**How to verify:** Run two concurrent increments against two replicas sharing study-data; the final count can fall short of the starts.

## Exercise 2: Identify the scope of the fixture lock.

**Expected answer:** Threads in one process, not multiple containers.

**Why:** A lock object in memory is not shared across isolated processes. State the assumption instead of extending it by analogy.

**Approach:** Ask where the lock lives: in server.py's memory, shared only by that process's threads.

**Why this is correct:** A second container has its own copy of the lock, so the two never wait on each other.

**A plausible wrong approach:** Assuming the in-process lock protects shared study-data across replicas extends it beyond its scope.

**How to verify:** The design note states the single-process assumption, and the concurrent test shows lost updates once it is broken.

## Exercise 3: Design a replica-readiness checklist.

**Expected evidence:** Routing, state concurrency, sessions, resource budget and recovery.

**Why:** Each requirement can fail independently. A successful second process start does not prove the application is safely scalable.

**Approach:** Check routing, shared-state writes, sessions, resource budget and recovery one at a time for a second replica.

**Why this is correct:** Any of these can fail alone; the fixture's counter fails the shared-state item.

**A plausible wrong approach:** Starting a second replica and seeing it healthy as proof of scalability ignores the counter's concurrency gap.

**How to verify:** Each item has a check; the counter item fails under the concurrent increment test until redesigned.

## Exercise 4: Diagnose a fixed host-port collision.

**Expected answer:** Several replicas cannot all bind the same host socket independently.

**Why:** Introduce an intended routing layer or distinct ports for a controlled experiment. Do not disable isolation merely to make startup succeed.

**Approach:** Read the ports line: 127.0.0.1:18080 can be bound by only one container at a time.

**Why this is correct:** A second replica tries the same host socket and fails to start.

**A plausible wrong approach:** Switching to network_mode host to avoid the collision removes isolation and still allows only one listener.

**How to verify:** Add a proxy in front, or give each replica its own port for a test; each then starts.

## Exercise 5: Explain why load balancing does not fix lost updates.

**Expected answer:** Traffic distribution does not serialize shared-state transactions.

**Why:** The data store or application protocol must provide the necessary concurrency guarantees regardless of which replica receives the request.

**Approach:** Separate who receives a request from how shared data is updated.

**Why this is correct:** A balancer spreads requests, but each replica still does its own read-modify-write on the same file.

**A plausible wrong approach:** Adding a balancer to fix wrong counts keeps the same race in every replica.

**How to verify:** Run the concurrent test behind the balancer; counts still fall short.

## Exercise 6: Propose a correct scaled counter architecture.

**Expected evidence:** A transaction-capable shared store or explicit single-writer ownership.

**Why:** Defend the consistency and failure semantics. Test concurrent increments and unknown outcomes rather than presenting replica count as correctness evidence.

**Approach:** Choose a store with atomic increments or transactions, or route every write to one owning instance.

**Why this is correct:** Either makes increments ordered, which replicas alone cannot provide.

**A plausible wrong approach:** Raising the replica count to show scalability adds more writers to the race.

**How to verify:** Concurrent increments match the request count, and a timed-out request is checked rather than retried blindly.

## Check your transfer

Three replicas need a routing layer instead of the fixed host port, and the counter needs a shared store with transactions, such as a database that increments in one statement, because file replacement and an in-process lock cannot serialize writers in different containers. The simplest correct alternative is one replica with an explicit single writer, measured first: a standard-library server answering small JSON requests may well carry two hundred learners. A load test showing that one replica saturates is the evidence that would justify the larger design.
