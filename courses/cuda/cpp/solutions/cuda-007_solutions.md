# cuda-007: explanatory solutions

## Mechanism review

Arithmetic intensity measures operations per byte of data movement under an explicitly stated memory model. A roofline estimate limits performance by the smaller of arithmetic capacity and bandwidth times intensity. It is an upper bound, not a timer. Vector addition reads two float32 values and writes one for one addition, giving roughly one operation per twelve useful bytes before cache and transaction effects. Matrix multiplication can reuse each loaded value many times; tiling increases reuse but consumes working storage. Launch cost, transfer cost, dependency stalls and imperfect access patterns can keep measured work far below either bound.

The separate [CPU reference](../references/cuda-007_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Assume hypothetical bandwidth of 600 GB/s, using decimal billions, and a 12-byte-per-element vector addition. The ideal useful-element throughput is 50 billion elements/s. One million elements require at least 20 microseconds at that bandwidth, excluding launch and host transfer. This is a thought experiment, not a claim about the learner's GPU.

## Exercise 2

A hypothetical device has 10 TFLOP/s arithmetic capacity and 500 GB/s bandwidth. At intensity 2 FLOP/byte the roofline is 1 TFLOP/s; at intensity 40 it is capped at 10 TFLOP/s. Increasing reuse can change the limiting resource, but a kernel must still expose sufficient independent work.

## Exercise 3

Two eight-byte reads and one eight-byte write per element gives 24,000 useful bytes. Measured transactions and cache traffic can differ.

## Exercise 4

The units do not cancel. Divide bytes by bytes/s for memory time, or floating operations by operations/s for arithmetic time.

## Exercise 5

Fixed launch and synchronization overhead dominate; the asymptotic bandwidth model omits that term.

## Exercise 6

Correctness first, then measured time, compiler resource usage and selected memory/occupancy metrics on the same workload. Reduced estimated bytes alone is insufficient.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-007_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Correctness first, then measured time, compiler resource usage and selected memory/occupancy metrics on the same workload. Reduced estimated bytes alone is insufficient.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
