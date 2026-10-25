# cuda-044: explanatory solutions

## Mechanism review

A streaming compute service needs bounded ownership and backpressure before it needs more streams. Backpressure means producers stop or reject work when the system cannot safely accept another item. A slot moves through states such as free, filling, computing, copying and consumed. Reuse is allowed only after the final consumer completes. Cancellation stops admission and cleans up according to actual completion state; it does not magically cancel every submitted device instruction. This capstone is a bounded local pipeline, not a new network server inside the classroom worker.

The separate [CPU reference](../references/cuda-044_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

With capacity two, submit chunks A and B. Chunk C waits until a slot becomes free. If A finishes compute but its output is still downloading, A's slot is not yet free. A correct queue can process arbitrary many chunks with constant bounded storage by reusing only completed slots.

## Exercise 2

A synchronous pipeline has 7 ms latency per chunk. A pipelined version can deliver later chunks every 3 ms while the first still takes roughly 7 ms in the ideal model. Throughput and first-result latency are distinct objectives; reporting only the inter-result interval hides the user's wait.

## Exercise 3

Free to filling to computing to copying to consumed to free, with explicit completion conditions and rejection of reuse from intermediate states.

## Exercise 4

Outstanding operations may still access them. Stop new admission, establish supported completion/cleanup and preserve the original cancellation record.

## Exercise 5

Produce the explicitly defined empty result without occupying expensive work unnecessarily, preserving sequence/order bookkeeping.

## Exercise 6

Every input chunk has exactly one matching output, no early slot reuse, bounded memory, correct tails, cancellation diagnostics and a baseline comparison.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-044_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Every input chunk has exactly one matching output, no early slot reuse, bounded memory, correct tails, cancellation diagnostics and a baseline comparison.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
