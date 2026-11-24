# cuda-036: explanatory solutions

## Mechanism review

Occupancy compares resident warps with a hardware limit. Residency is constrained by threads, blocks, register allocation and shared memory, including allocation granularity. Resident does not mean ready to issue: a warp may wait for data or dependencies. More work per thread can improve reuse while increasing registers and reducing occupancy. Forcing fewer registers can increase spills to device memory. The goal is a correct faster workload, not maximizing one percentage. Use reviewed launch candidates, compiler resource reports and timings together, and avoid pretending a simplified resource arithmetic model reproduces every scheduling rule.

The separate [CPU reference](../references/cuda-036_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

In a simplified SM with 65,536 registers, a 256-thread block using 64 registers per thread needs 16,384 registers. Registers alone permit four blocks. At 128 registers per thread, registers alone permit two. Other limits can reduce both figures; this calculation is not an actual occupancy API result.

**Approach:** Divide 65,536 registers by 256 threads times registers per thread for 64 and 128 registers.

**Why it is correct:** 256 * 64 is 16,384, so four blocks fit by registers; at 128 registers each block needs 32,768, so two fit.

**A plausible wrong approach:** Treating four blocks as the final residency ignores shared memory, thread and block limits that may bind first.

**How to verify:** The reference asserts blocks == [4, 2] and prints other_hardware_limits_included False.

## Exercise 2

Configuration A takes 2 ms with 50% occupancy. Configuration B takes 2.4 ms with 75%. If both pass correctness, A wins that stated timing objective. Investigate reuse, instruction-level parallelism and spills rather than choosing B merely because its percentage is larger.

**Approach:** Choose A because it meets correctness and takes 2 ms against 2.4 ms.

**Why it is correct:** The objective is time, and A wins it despite lower occupancy.

**A plausible wrong approach:** Picking B for its 75 percent occupancy confuses a resource metric with the goal.

**How to verify:** Keep both timing distributions and resource reports together with the decision.

## Exercise 3

Eight blocks under the simplified division, before block/thread/shared-memory/granularity limits.

**Approach:** Divide 65,536 by 128 threads times 64 registers.

**Why it is correct:** Each block needs 8,192 registers, so eight blocks fit before other limits.

**A plausible wrong approach:** Reusing the 256-thread answer of four blocks ignores that the block is half as large.

**How to verify:** Compute 65536 // (128 * 64) and expect 8, labeled register-only.

## Exercise 4

It can spill live values to device-backed storage and add loads/stores, outweighing increased residency.

**Approach:** Inspect spill bytes in the compiler report after lowering the register cap.

**Why it is correct:** Spilled values go to device-backed local memory and add loads and stores.

**A plausible wrong approach:** Assuming more resident warps always hides the extra traffic ignores that spills sit on the critical path.

**How to verify:** Time both versions and compare spill counts from the resource report.

## Exercise 5

There may be too few blocks to populate the device regardless of theoretical per-SM occupancy.

**Approach:** Count blocks against SMs: too few blocks leave SMs idle.

**Why it is correct:** Per-SM occupancy only matters where blocks exist to fill the SM.

**A plausible wrong approach:** Raising per-block occupancy for a two-block grid cannot use the remaining SMs.

**How to verify:** Compare block count with the device's SM count before tuning occupancy.

## Exercise 6

Use a small explicit set such as 64,128,256 threads, hold algorithm/input fixed, validate every result, retain resource reports and timing distributions.

**Approach:** Sweep 64, 128 and 256 threads per block with fixed algorithm and input.

**Why it is correct:** Holding everything else fixed attributes differences to block size alone.

**A plausible wrong approach:** Changing tile size and block size together in one sweep mixes two effects.

**How to verify:** Validate every output and retain resource reports and timing samples for each size.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-036_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Use a small explicit set such as 64,128,256 threads, hold algorithm/input fixed, validate every result, retain resource reports and timing distributions.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
