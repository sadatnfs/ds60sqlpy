# cuda-111: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Calculate arithmetic intensity

Divide operations by bytes.

**Approach.** Calculate arithmetic intensity: 4096 operations over 8192 bytes moved gives 0.5 operations per byte, as the reference asserts.

**Why it is correct here.** Arithmetic intensity compares work with data movement. At 0.5 operations per byte, the kernel needs memory bandwidth far more than compute throughput on typical GPUs.

**A plausible wrong approach.** Dividing bytes by operations gives 2 and inverts the conclusion, suggesting the kernel is compute-heavy.

**How to verify.** Recompute from element counts and element size in the code, then compare with profiler-measured operations and DRAM bytes.

## Exercise 2: Count eliminated bytes

Count both avoided write and read.

**Approach.** Count eliminated bytes from fusion: an intermediate of 1024 float32 values is 4096 bytes, and fusion avoids both writing and reading it, saving 8192 bytes.

**Why it is correct here.** Without fusion the first kernel writes the intermediate to global memory and the second reads it back. Fusion keeps the value in registers, so both transfers disappear.

**A plausible wrong approach.** Counting only the avoided write gives 4096 bytes and underestimates the saving by half.

**How to verify.** The reference asserts `saved == 8192`. Compare DRAM bytes in the profiler before and after fusion.

## Exercise 3: Name a profiler counter

Choose a relevant measured traffic or stall metric.

**Approach.** Name a relevant profiler counter, such as DRAM bytes read and written or the memory-throughput percentage, since the hypothesis is about memory traffic.

**Why it is correct here.** A counter tied to the hypothesis can confirm or reject it. If DRAM bytes do not fall after fusion, the expected saving did not happen.

**A plausible wrong approach.** Using only total kernel time cannot separate fewer bytes from other effects. Time can also change because of clock variation or a different compiled instruction mix, so a timing-only comparison leaves the mechanism unknown.

**How to verify.** Collect the counter for both versions on the same shape, record the values with the profiler version, and compare them.

## Exercise 4: Design one controlled change

Keep all other settings fixed.

**Approach.** Design one controlled change: apply fusion while keeping the shape, dtype, launch configuration rules, warm-up and timing method fixed.

**Why it is correct here.** Changing one factor attributes any difference in time or counters to that change. Repeating each configuration several times also shows whether the difference exceeds normal run-to-run variation.

**A plausible wrong approach.** Applying fusion and a new block size together leaves the source of a speedup ambiguous. If one change helps and the other hurts, the combined result may even show no difference and hide both effects.

**How to verify.** Diff the two configurations and confirm that only the fusion setting differs.

## Exercise 5: Test a boundary shape

Use a nonmultiple and a tiny case.

**Approach.** Test a boundary shape such as 1023 elements, not a multiple of the block size, and a tiny case such as 1 element.

**Why it is correct here.** Fused kernels combine index logic from both stages, so bounds checks are a common source of errors. Odd sizes exercise partial blocks.

**A plausible wrong approach.** Testing only 1024 elements misses an off-by-one bounds check that writes past the end on 1023.

**How to verify.** Compare outputs with the unfused reference for both shapes and use a guard region to detect stray writes.

## Exercise 6: Explain a failed optimization

Relate observed resource use and timing to the rejected hypothesis.

**Approach.** Explain a failed optimization: if fusion raises register use so occupancy falls, throughput may drop even though DRAM bytes fell, and the hypothesis that traffic limited performance is rejected for that shape.

**Why it is correct here.** Profiler evidence shows which resource changed. Fewer bytes with lower occupancy suggests latency hiding, not bandwidth, became the limit.

**A plausible wrong approach.** Reporting the fused version as an improvement because bytes fell ignores the measured timing. The bytes counter confirms the mechanism worked, but the goal was throughput, and that goal was not met for this shape.

**How to verify.** Record registers per thread, achieved occupancy, DRAM bytes and time for both versions, then decide from all four.

## Reference observation

Intensity 0.5 and hypothetical 8192 bytes removable traffic.

The reference file is `courses/cuda/python/references/cuda-111_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
