# cuda-033: explanatory solutions

## Mechanism review

Kernel counters describe selected aspects of execution, often through replay or sampled collection. They require context: achieved occupancy is a residency measurement, memory throughput measures traffic, and eligible-warps metrics describe scheduling opportunity. High utilization can mean an inefficient algorithm is busy moving unnecessary data. Low utilization can be expected for tiny work. Counter permissions are separate from ordinary CUDA execution capability; a working kernel does not promise profiler access. Start with a small question and a few relevant metrics, keeping the baseline's input, dtype and result contract fixed.

The separate [CPU reference](../references/cuda-033_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

A synthetic kernel reads 400 useful bytes but causes 1,600 transferred bytes because of its access pattern. Useful-to-transferred ratio is 0.25. A high DRAM traffic counter does not imply useful data processing is efficient. Compare address patterns and a corrected layout before blaming arithmetic capacity.

## Exercise 2

Two kernels show 50% and 75% occupancy, yet times are 2 and 3 ms. Occupancy alone cannot rank them. The second may do more instructions, spill registers or repeat loads. Keep both correctness and selected counters with the timings, and state which causal explanation remains a hypothesis.

## Exercise 3

60 GB/s in decimal units. State useful-byte accounting separately from measured hardware traffic.

## Exercise 4

Collection and replay can perturb cache state, scheduling and overhead. Keep instrumented evidence separate from normal benchmark samples.

## Exercise 5

Record profiling capability as unavailable; use correctness, host/device timing and address reasoning without inventing counters.

## Exercise 6

Compare equal useful work, map lane addresses, collect relevant memory metrics if permitted and test a contiguous alternative while preserving output.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-033_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Compare equal useful work, map lane addresses, collect relevant memory metrics if permitted and test a contiguous alternative while preserving output.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
