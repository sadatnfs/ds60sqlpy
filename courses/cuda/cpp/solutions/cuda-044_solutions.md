# cuda-044: explanatory solutions

## Mechanism review

A streaming compute service needs bounded ownership and backpressure before it needs more streams. Backpressure means producers stop or reject work when the system cannot safely accept another item. A slot moves through states such as free, filling, computing, copying and consumed. Reuse is allowed only after the final consumer completes. Cancellation stops admission and cleans up according to actual completion state; it does not magically cancel every submitted device instruction. This capstone is a bounded local pipeline, not a new network server inside the classroom worker.

The separate [CPU reference](../references/cuda-044_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

With capacity two, submit chunks A and B. Chunk C waits until a slot becomes free. If A finishes compute but its output is still downloading, A's slot is not yet free. A correct queue can process arbitrary many chunks with constant bounded storage by reusing only completed slots.

**Approach:** Admit chunks A and B into two slots, and hold C until a slot reaches the free state.

**Why it is correct:** A slot is free only after its output download and host consumption complete, not after compute.

**A plausible wrong approach:** Freeing A's slot when its kernel finishes lets C's upload overwrite output still downloading.

**How to verify:** The reference doubles [[1, 2], [3], [], [4, 5]] to [[2, 4], [6], [], [8, 10]]; match each chunk's output.

## Exercise 2

A synchronous pipeline has 7 ms latency per chunk. A pipelined version can deliver later chunks every 3 ms while the first still takes roughly 7 ms in the ideal model. Throughput and first-result latency are distinct objectives; reporting only the inter-result interval hides the user's wait.

**Approach:** Report first-result latency of about 7 ms and steady interval of about 3 ms separately.

**Why it is correct:** Pipelining raises throughput while the first chunk still passes through every stage.

**A plausible wrong approach:** Quoting 3 ms as the latency of each request hides the 7 ms a single caller waits.

**How to verify:** Measure time to first output and time between outputs on a GPU.

## Exercise 3

Free to filling to computing to copying to consumed to free, with explicit completion conditions and rejection of reuse from intermediate states.

**Approach:** Write free, filling, computing, copying, consumed, free with a completion condition per arrow.

**Why it is correct:** Each arrow requires the prior stage to finish, which prevents early reuse.

**A plausible wrong approach:** Allowing computing to return to free skips copying and consumption.

**How to verify:** The reference asserts computing comes before consumed in the lifecycle list.

## Exercise 4

Outstanding operations may still access them. Stop new admission, establish supported completion/cleanup and preserve the original cancellation record.

**Approach:** Stop admission, wait for or cancel outstanding work through supported calls, then free.

**Why it is correct:** Queued copies or kernels may still touch the buffers.

**A plausible wrong approach:** Freeing immediately on cancel leaves in-flight operations reading released memory.

**How to verify:** Cancel mid-stream under a sanitizer and confirm no invalid access and a kept record.

## Exercise 5

Produce the explicitly defined empty result without occupying expensive work unnecessarily, preserving sequence/order bookkeeping.

**Approach:** Return an empty result for the empty chunk without launching, keeping its sequence slot.

**Why it is correct:** The output list must still align one-to-one with inputs.

**A plausible wrong approach:** Dropping the empty chunk shifts every later output to the wrong input.

**How to verify:** The reference keeps [] at position 2 in the results.

## Exercise 6

Every input chunk has exactly one matching output, no early slot reuse, bounded memory, correct tails, cancellation diagnostics and a baseline comparison.

**Approach:** Check one output per chunk, no early reuse, bounded memory, tails, cancellation and a baseline.

**Why it is correct:** These properties make the service correct before any timing matters.

**A plausible wrong approach:** Accepting the capstone on throughput alone skips the failures users would notice.

**How to verify:** Run long and short chunk streams and assert each property.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-044_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Every input chunk has exactly one matching output, no early slot reuse, bounded memory, correct tails, cancellation diagnostics and a baseline comparison.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
