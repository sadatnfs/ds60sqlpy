# cuda-001: explanatory solutions

## Mechanism review

A CPU is optimized to make progress on a comparatively small number of complicated instruction streams. A GPU spends more of its resources on throughput across many pieces of work. This is a design distinction, not a rule that the GPU wins. A dependency means that one result must exist before another calculation can start. Pixel brightness updates have independent destinations; a running account balance has a dependency between successive balances. There can still be a parallel prefix algorithm for that balance, but changing the algorithm is real work. Include loading data, launching kernels and returning results when deciding whether acceleration helps a person waiting for an answer.

The separate [CPU reference](../references/cuda-001_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Suppose an application spends 20 seconds parsing and 80 seconds transforming pixels. An imagined GPU makes the transform ten times faster and adds 4 seconds of transfers. The new time is \(20 + 8 + 4 = 32\) seconds, so the application speedup is 3.125. The tenfold kernel improvement is not the application improvement. Even an infinitely fast transform leaves 24 seconds under these assumptions.

## Exercise 2

For one tiny request, suppose CPU arithmetic costs 2 microseconds, while GPU submission and transfers cost 30 microseconds before arithmetic. A 0.2 microsecond kernel gives 30.2 microseconds end to end. Batching 1,000 independent requests may amortize overhead, but it changes waiting time and memory usage. Neither result follows from a core count.

## Exercise 3

The 40-second serial part remains. The upper bound is \(\frac{100}{40} = 2.5\), even with an infinitely fast parallel part.

## Exercise 4

Record upload, allocation, launch, synchronization and download costs with the same input and output contract before computing application speedup.

## Exercise 5

The mathematical output is empty. A host guard can return immediately instead of launching an empty grid; fixed overhead otherwise dominates.

## Exercise 6

CUDA does not remove network waiting or dependency ordering. First change the request architecture or batch independent work; do not infer a compute bottleneck.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-001_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

CUDA does not remove network waiting or dependency ordering. First change the request architecture or batch independent work; do not infer a compute bottleneck.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
