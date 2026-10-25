# cuda-041: explanatory solutions

## Mechanism review

A stream-ordered allocator treats allocation and free as operations with ordering relationships. It can reuse pooled storage efficiently, but the program must still ensure that every access occurs after allocation and before the relevant free/reuse. Cross-stream consumers require explicit dependencies. Memory returned to a pool can remain reserved for reuse, so reported device memory need not immediately drop to zero. Distinguish live application allocations from reserved pool storage. Pool behavior and support are runtime capabilities, not assumptions justified by a function name in documentation.

The separate [CPU reference](../references/cuda-041_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Stream A allocates X, writes X and records ready. Stream B waits, reads X and records done. Before A frees X, A waits for done. This closes both the producer-to-consumer edge and the consumer-to-reuse edge. The first event alone is insufficient for lifetime safety.

## Exercise 2

A pool reserves 64 MiB and the application currently uses 16 MiB. After freeing that allocation back to the pool, live usage may be zero while reservation remains 64 MiB. Calling this a leak without examining ownership and retention policy confuses two different measurements.

## Exercise 3

Ready orders production before consumption; done orders final consumption before free or reuse.

## Exercise 4

Enqueueing does not imply completion. Establish the final-consumer dependency before the allocation becomes reusable.

## Exercise 5

Existing valid owners and original diagnostics; do not pretend a null allocation has valid output or destroy unrelated state.

## Exercise 6

Compare a bounded reuse pool with repeated allocation, record live versus reserved bytes and retain identical correctness and completion contracts.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-041_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Compare a bounded reuse pool with repeated allocation, record live versus reserved bytes and retain identical correctness and completion contracts.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
