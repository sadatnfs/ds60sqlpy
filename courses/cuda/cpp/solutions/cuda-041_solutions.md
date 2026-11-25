# cuda-041: explanatory solutions

## Mechanism review

A stream-ordered allocator treats allocation and free as operations with ordering relationships. It can reuse pooled storage efficiently, but the program must still ensure that every access occurs after allocation and before the relevant free/reuse. Cross-stream consumers require explicit dependencies. Memory returned to a pool can remain reserved for reuse, so reported device memory need not immediately drop to zero. Distinguish live application allocations from reserved pool storage. Pool behavior and support are runtime capabilities, not assumptions justified by a function name in documentation.

## Exercise 1

Stream A allocates X, writes X and records ready. Stream B waits, reads X and records done. Before A frees X, A waits for done. This closes both the producer-to-consumer edge and the consumer-to-reuse edge. The first event alone is insufficient for lifetime safety.

**Approach:** Order allocate, write, ready, wait in B, read, done, wait in A, then free X.

**Why it is correct:** Ready guards the read and done guards the free, closing both edges.

**A plausible wrong approach:** Using only the ready event lets A free X while B may still be reading.

**How to verify:** The reference asserts read_B comes before free_A in the event list.

## Exercise 2

A pool reserves 64 MiB and the application currently uses 16 MiB. After freeing that allocation back to the pool, live usage may be zero while reservation remains 64 MiB. Calling this a leak without examining ownership and retention policy confuses two different measurements.

**Approach:** Report live and reserved bytes separately and check pool retention policy.

**Why it is correct:** After the free, live is 0 MiB while the pool keeps 64 MiB reserved for reuse.

**A plausible wrong approach:** Calling the reserved 64 MiB a leak ignores that the pool intentionally holds it.

**How to verify:** The reference prints reserved_MiB 64 and live_MiB 0; trim the pool and confirm release.

## Exercise 3

Ready orders production before consumption; done orders final consumption before free or reuse.

**Approach:** Name ready for production before consumption and done for consumption before free.

**Why it is correct:** Each event covers one hazard: reading too early or freeing too early.

**A plausible wrong approach:** Treating one event as covering both directions leaves the reuse hazard open.

**How to verify:** Draw both arrows and check each crosses streams in the right direction.

## Exercise 4

Enqueueing does not imply completion. Establish the final-consumer dependency before the allocation becomes reusable.

**Approach:** Wait for the consuming stream's done event before freeing.

**Why it is correct:** Enqueued work may not have run yet when the host frees.

**A plausible wrong approach:** Synchronizing the freeing stream alone does not wait for the other stream.

**How to verify:** Run a sanitizer and a delayed consumer to expose any early free.

## Exercise 5

Existing valid owners and original diagnostics; do not pretend a null allocation has valid output or destroy unrelated state.

**Approach:** Report the failure and keep existing valid buffers and diagnostics intact.

**Why it is correct:** Other owners still rely on their allocations.

**A plausible wrong approach:** Continuing with a null pointer as if allocation succeeded produces invalid output.

**How to verify:** Force an allocation failure in a test and check prior results survive.

## Exercise 6

Compare a bounded reuse pool with repeated allocation, record live versus reserved bytes and retain identical correctness and completion contracts.

**Approach:** Compare a bounded reuse pool with fresh allocation per iteration.

**Why it is correct:** Reuse avoids repeated allocation cost while the bound caps memory.

**A plausible wrong approach:** An unbounded pool can grow until other work cannot allocate.

**How to verify:** Record live and reserved bytes and timings for both, with identical outputs.

## Self-check answers

1. **Which two edges make the cross-stream allocation in worked example 1 safe?** Producer to consumer through the ready event, and consumer to free through the done event.
2. **Why is freeing right after enqueuing work in another stream unsafe?** The free is ordered only in its own stream, so the other stream may still read the buffer.
3. **What does a stream-ordered free promise?** The memory becomes reusable after prior work in that stream completes, not immediately.

## Numerical reference and its limits

The [CPU reference](../references/cuda-041_cpu.py) reproduces worked example 1 and prints `{'lifetime_order': ['allocate_A', 'write_A', 'ready', 'wait_ready_B', 'read_B', 'done', 'wait_done_A', 'free_A'], 'reserved_MiB': 64, 'live_MiB': 0}`.

## Transfer review

Compare a bounded reuse pool with repeated allocation, record live versus reserved bytes and retain identical correctness and completion contracts.
