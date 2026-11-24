# cuda-033: explanatory solutions

## Mechanism review

Kernel counters describe selected aspects of execution, often through replay or sampled collection. They require context: achieved occupancy is a residency measurement, memory throughput measures traffic, and eligible-warps metrics describe scheduling opportunity. High utilization can mean an inefficient algorithm is busy moving unnecessary data. Low utilization can be expected for tiny work. Counter permissions are separate from ordinary CUDA execution capability; a working kernel does not promise profiler access. Start with a small question and a few relevant metrics, keeping the baseline's input, dtype and result contract fixed.

The separate [CPU reference](../references/cuda-033_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

A synthetic kernel reads 400 useful bytes but causes 1,600 transferred bytes because of its access pattern. Useful-to-transferred ratio is 0.25. A high DRAM traffic counter does not imply useful data processing is efficient. Compare address patterns and a corrected layout before blaming arithmetic capacity.

**Approach:** Divide 400 useful bytes by 1,600 transferred bytes.

**Why it is correct:** Only a quarter of moved bytes do useful work, so the access pattern wastes bandwidth.

**A plausible wrong approach:** Reading high DRAM throughput as efficient processing ignores that most bytes are unused.

**How to verify:** The reference asserts useful / transferred == 0.25.

## Exercise 2

Two kernels show 50% and 75% occupancy, yet times are 2 and 3 ms. Occupancy alone cannot rank them. The second may do more instructions, spill registers or repeat loads. Keep both correctness and selected counters with the timings, and state which causal explanation remains a hypothesis.

**Approach:** Rank by measured time and use occupancy only to explain differences.

**Why it is correct:** The 75 percent kernel takes 3 ms against 2 ms, so occupancy did not predict speed.

**A plausible wrong approach:** Picking the higher-occupancy kernel as faster contradicts the measured times.

**How to verify:** Keep correctness checks and counters next to each timing.

## Exercise 3

60 GB/s in decimal units. State useful-byte accounting separately from measured hardware traffic.

**Approach:** Divide 12,000,000 bytes by 0.0002 seconds.

**Why it is correct:** That is 6e10 bytes per second, or 60 GB/s in decimal units.

**A plausible wrong approach:** Using binary units here gives about 55.9 GiB/s and a mismatched label.

**How to verify:** The reference asserts 12_000_000 / 0.0002 == 60_000_000_000.

## Exercise 4

Collection and replay can perturb cache state, scheduling and overhead. Keep instrumented evidence separate from normal benchmark samples.

**Approach:** Keep profiler-collected numbers separate from ordinary timing samples.

**Why it is correct:** Counter replay reruns kernels and perturbs caches and timing.

**A plausible wrong approach:** Quoting a kernel time from an instrumented replay as normal runtime overstates cost.

**How to verify:** Time the same kernel without the profiler and compare.

## Exercise 5

Record profiling capability as unavailable; use correctness, host/device timing and address reasoning without inventing counters.

**Approach:** Record counters as unavailable and use timing and address reasoning.

**Why it is correct:** Missing permissions or hardware means no counter values exist.

**A plausible wrong approach:** Estimating counter values and presenting them as measured fabricates evidence.

**How to verify:** State the capability check result next to the analysis.

## Exercise 6

Compare equal useful work, map lane addresses, collect relevant memory metrics if permitted and test a contiguous alternative while preserving output.

**Approach:** Map lane addresses for the strided read and compare with a contiguous version of equal work.

**Why it is correct:** Address mapping predicts wasted bytes that memory metrics can confirm.

**A plausible wrong approach:** Comparing a strided kernel with a contiguous one doing less work credits layout for reduced work.

**How to verify:** Confirm both produce identical outputs before comparing metrics.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-033_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It also asserts an exercise answer that the guide's model leaves for you to derive: `assert 12_000_000 / 0.0002 == 60_000_000_000`. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Compare equal useful work, map lane addresses, collect relevant memory metrics if permitted and test a contiguous alternative while preserving output.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
