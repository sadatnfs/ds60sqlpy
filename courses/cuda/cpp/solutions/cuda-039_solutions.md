# cuda-039: explanatory solutions

## Mechanism review

A stream is an ordered queue of work. Operations in one stream respect that stream's ordering, while separate streams need explicit dependencies when sharing data. Record an event after a producer and make the consumer stream wait for it before reading the result. Two streams allow concurrency; they do not guarantee simultaneous execution or isolated memory. Default-stream semantics depend on the selected configuration, so educational code should use explicit streams rather than relying on invisible ordering. Buffer lifetimes must cover all queued consumers, and a host completion check is required before validating or releasing their outputs.

The separate [CPU reference](../references/cuda-039_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Stream A doubles \([1,2,3]\) to \([2,4,6]\), records an event, and stream B waits before adding one, producing \([3,5,7]\). The event creates the producer-consumer edge. Without that edge, B might read old or incomplete data even though both launches individually succeed.

**Approach:** Record an event in stream A after doubling, and make stream B wait on it before adding one.

**Why it is correct:** The event edge guarantees [2, 4, 6] is complete before B reads it, giving [3, 5, 7].

**A plausible wrong approach:** Launching B's kernel after A's on the host assumes ordering that separate streams do not provide.

**How to verify:** The reference asserts b == [3, 5, 7] and lists the three order edges.

## Exercise 2

Two independent vectors can be transformed in separate streams without a cross-stream dependency if they share no mutable storage. Their outputs remain correct even if hardware serializes them. Correctness must not depend on overlap being observed.

**Approach:** Run two independent vectors in separate streams with no shared mutable storage.

**Why it is correct:** With no shared data, any interleaving or serialization gives the same outputs.

**A plausible wrong approach:** Asserting that the streams must overlap turns a performance hope into a correctness requirement.

**How to verify:** Compare outputs from separate streams with a single-stream run.

## Exercise 3

Record after the upload in A; make B wait on that event before launching compute that reads the uploaded buffer.

**Approach:** Record an event after the upload in A and wait on it in B before compute.

**Why it is correct:** The wait prevents B's kernel from reading a partially uploaded buffer.

**A plausible wrong approach:** Recording the event before the upload makes the edge order nothing useful.

**How to verify:** Draw upload, record, wait and compute in order and check the arrow direction.

## Exercise 4

The buffer's final consumer must complete before release or reuse. Stream names do not determine allocation lifetime.

**Approach:** Tie buffer release to its final consumer's completion, not to a stream's lifetime.

**Why it is correct:** Another stream may still read the buffer after the first stream is destroyed.

**A plausible wrong approach:** Assuming destroying a stream waits for borrowers frees memory still in use.

**How to verify:** Wait on the consumer's done event before release and run a sanitizer.

## Exercise 5

Skip unnecessary work while preserving dependencies needed by later nonempty chunks; do not record fabricated output completion.

**Approach:** Skip compute for an empty chunk but keep events later chunks depend on.

**Why it is correct:** Later work may still wait on that event position.

**A plausible wrong approach:** Recording a done event as if output exists fabricates completion of real data.

**How to verify:** Insert an empty chunk in the middle and confirm later chunks finish correctly.

## Exercise 6

Respect the producer framework's stream and consumer synchronization contract, including lifetime. Sharing a pointer alone is insufficient.

**Approach:** Use the producer framework's stream and synchronization contract when sharing buffers.

**Why it is correct:** A raw pointer says nothing about when writes are done or when memory is freed.

**A plausible wrong approach:** Passing only the pointer lets the consumer read before the producer finishes.

**How to verify:** Test with a delayed producer and confirm the consumer still sees final data.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-039_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Respect the producer framework's stream and consumer synchronization contract, including lifetime. Sharing a pointer alone is insufficient.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
