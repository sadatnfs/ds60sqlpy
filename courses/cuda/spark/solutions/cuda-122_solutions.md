# cuda-122: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Compute transfer lower bound

Bytes divided by effective bandwidth.

**Approach.** Compute the transfer lower bound as bytes over effective bandwidth: 10 GiB at 1 GiB/s takes at least 10 seconds before serialization, connection setup or retries.

**Why it is correct here.** No implementation can move the payload faster than the link allows, so this bound is a floor on the shuffle stage regardless of kernel speed.

**A plausible wrong approach.** Spending effort to halve a 100 ms kernel, saving 50 ms, addresses less than 1 percent of the 10-second floor, as the reference asserts with `kernel_saving/seconds < 0.01`.

**How to verify.** The reference asserts `seconds == 10`. Compare with measured shuffle read and write time for the stage.

## Exercise 2: Identify local versus network time

Measure the complete stage.

**Approach.** Identify local versus network time by measuring the whole stage, including shuffle write, fetch wait time and local compute, from Spark stage metrics.

**Why it is correct here.** Stage metrics separate time spent waiting for remote blocks from time spent computing. The larger component is the target for optimization.

**A plausible wrong approach.** Profiling only the GPU kernels shows local compute and misses fetch wait time, which may dominate. A GPU profile of a shuffle-bound stage can look idle for long stretches, and that idle time is exactly the network wait.

**How to verify.** Read shuffle fetch wait time and executor compute time from the stage summary and compare them.

## Exercise 3: Explain pre-aggregation

Combine only when mathematical semantics allow.

**Approach.** Explain pre-aggregation: computing partial sums on each map task before the shuffle sends one value per key per task rather than every row.

**Why it is correct here.** Sum is associative and commutative, so combining partial sums gives the same total and greatly reduces shuffled bytes for keys with many rows.

**A plausible wrong approach.** Pre-aggregating a non-associative operation, such as a median computed from partial medians, produces wrong results.

**How to verify.** Compare shuffle bytes and results with and without pre-aggregation on the same data, and confirm totals match.

## Exercise 4: List transport qualification

Verify devices topology libraries and real traffic.

**Approach.** List transport qualification for an accelerated shuffle transport: supported network devices, topology, matching library versions and a test with real traffic between hosts.

**Why it is correct here.** Accelerated transports depend on specific hardware and libraries, and a misconfiguration may fall back to a slower path without obvious errors.

**A plausible wrong approach.** Enabling the transport setting and assuming it is active skips checking whether it actually carried traffic. A missing library on one host can silently route that host's traffic over the default path.

**How to verify.** Check transport logs or metrics on both sides of a test shuffle and confirm bytes went over the intended path.

## Exercise 5: Separate startup settings

Some shuffle choices require fresh executors.

**Approach.** Separate startup settings: some shuffle manager and transport choices are read when executors start, so changing them requires a fresh application.

**Why it is correct here.** Settings fixed at startup cannot change for a running session. Changing them mid-session has no effect.

**A plausible wrong approach.** Setting a shuffle manager in an existing session and attributing later timing changes to it measures noise. Any improvement seen there comes from caching, warm JIT code or variation between runs.

**How to verify.** Restart the application with the new setting and confirm it appears in the environment tab.

## Exercise 6: Design a bounded shuffle comparison

Use identical partitioned fixtures and capture bytes spills and output.

**Approach.** Design a bounded shuffle comparison using identical partitioned fixtures for both configurations, capturing shuffle bytes, spills and output.

**Why it is correct here.** Same data and partitioning make byte counts comparable, and equal outputs confirm the change preserved results.

**A plausible wrong approach.** Comparing configurations on different data sizes confounds the transport effect with payload size. Different partition counts also change the number of shuffle blocks, which affects per-block overhead independently of bandwidth.

**How to verify.** Assert outputs are equal, then report bytes and stage times side by side. Repeat each configuration at least three times and keep every sample, since network contention varies between runs.

## Reference observation

Ten-second payload lower bound;50 ms kernel saving is below 1 percent of it.

The reference file is `courses/cuda/spark/references/cuda-122_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
