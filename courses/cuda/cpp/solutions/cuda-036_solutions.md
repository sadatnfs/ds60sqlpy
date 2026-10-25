# cuda-036: explanatory solutions

## Mechanism review

Occupancy compares resident warps with a hardware limit. Residency is constrained by threads, blocks, register allocation and shared memory, including allocation granularity. Resident does not mean ready to issue: a warp may wait for data or dependencies. More work per thread can improve reuse while increasing registers and reducing occupancy. Forcing fewer registers can increase spills to device memory. The goal is a correct faster workload, not maximizing one percentage. Use reviewed launch candidates, compiler resource reports and timings together, and avoid pretending a simplified resource arithmetic model reproduces every scheduling rule.

The separate [CPU reference](../references/cuda-036_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

In a simplified SM with 65,536 registers, a 256-thread block using 64 registers per thread needs 16,384 registers. Registers alone permit four blocks. At 128 registers per thread, registers alone permit two. Other limits can reduce both figures; this calculation is not an actual occupancy API result.

## Exercise 2

Configuration A takes 2 ms with 50% occupancy. Configuration B takes 2.4 ms with 75%. If both pass correctness, A wins that stated timing objective. Investigate reuse, instruction-level parallelism and spills rather than choosing B merely because its percentage is larger.

## Exercise 3

Eight blocks under the simplified division, before block/thread/shared-memory/granularity limits.

## Exercise 4

It can spill live values to device-backed storage and add loads/stores, outweighing increased residency.

## Exercise 5

There may be too few blocks to populate the device regardless of theoretical per-SM occupancy.

## Exercise 6

Use a small explicit set such as 64,128,256 threads, hold algorithm/input fixed, validate every result, retain resource reports and timing distributions.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-036_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Use a small explicit set such as 64,128,256 threads, hold algorithm/input fixed, validate every result, retain resource reports and timing distributions.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
