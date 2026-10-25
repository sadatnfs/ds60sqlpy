# cuda-039: explanatory solutions

## Mechanism review

A stream is an ordered queue of work. Operations in one stream respect that stream's ordering, while separate streams need explicit dependencies when sharing data. Record an event after a producer and make the consumer stream wait for it before reading the result. Two streams allow concurrency; they do not guarantee simultaneous execution or isolated memory. Default-stream semantics depend on the selected configuration, so educational code should use explicit streams rather than relying on invisible ordering. Buffer lifetimes must cover all queued consumers, and a host completion check is required before validating or releasing their outputs.

The separate [CPU reference](../references/cuda-039_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Stream A doubles \([1,2,3]\) to \([2,4,6]\), records an event, and stream B waits before adding one, producing \([3,5,7]\). The event creates the producer-consumer edge. Without that edge, B might read old or incomplete data even though both launches individually succeed.

## Exercise 2

Two independent vectors can be transformed in separate streams without a cross-stream dependency if they share no mutable storage. Their outputs remain correct even if hardware serializes them. Correctness must not depend on overlap being observed.

## Exercise 3

Record after the upload in A; make B wait on that event before launching compute that reads the uploaded buffer.

## Exercise 4

The buffer's final consumer must complete before release or reuse. Stream names do not determine allocation lifetime.

## Exercise 5

Skip unnecessary work while preserving dependencies needed by later nonempty chunks; do not record fabricated output completion.

## Exercise 6

Respect the producer framework's stream and consumer synchronization contract, including lifetime. Sharing a pointer alone is insufficient.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-039_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Respect the producer framework's stream and consumer synchronization contract, including lifetime. Sharing a pointer alone is insufficient.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
