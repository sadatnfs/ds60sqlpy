# cuda-122: Shuffle, transport and network bottlenecks

**Route:** CUDA Python and machine learning / GPU Spark specialization. **Stage:** advanced. **Prerequisites:** `cuda-118`, `cuda-119`, `cuda-120`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Compute transfer lower bound.
- Identify local versus network time.
- Explain pre-aggregation.
- List transport qualification.
- Separate startup settings.
- Design a bounded shuffle comparison.

## Mechanism and vocabulary

A shuffle redistributes records between tasks, often crossing executor and host boundaries. Its cost includes serialization or columnar handling, buffering, transport, disk and downstream processing. A GPU can accelerate supported local operators while the job remains limited by network or storage. Specialized shuffle managers and transports have their own compatibility, startup configuration and failure behavior.

Do not infer RDMA, peer-to-peer or GPUDirect capability from an installed library. Those paths require actual hardware, topology and runtime support. Establish an ordinary supported shuffle baseline, then qualify an optional accelerated path. Record bytes, partitions, transfer time, retries and spill. Preserve query semantics and avoid exposing network services or changing cluster-wide settings from an ordinary lesson pad.



### Key terms

- **Shuffle:** Redistribution of records between tasks, often across executors and hosts.
- **Serialization:** Encoding records or columnar batches into bytes for transfer or storage.
- **Shuffle manager:** The pluggable Spark component that writes and fetches shuffle data, with its own compatibility rules.
- **Pre-aggregation:** Partial aggregation before a shuffle that reduces the bytes moved.

## Worked examples

### Worked example 1

Moving 10 GiB over an effective 1 GiB/s path has a 10-second payload lower bound before other costs. Halving a 100 ms local kernel cannot remove that bottleneck.

### Worked example 2

Reducing shuffle volume through an equivalent pre-aggregation may help more than changing transport. The rewrite must preserve aggregate semantics, especially for nonassociative or stateful operations.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-122_cpu.py) adds assertions.

```sh
python courses/cuda/spark/lessons/cuda-122_cpu.py
```

```python
gib = 1024**3
payload = 10 * gib
bandwidth = gib
seconds = payload / bandwidth
assert seconds == 10
kernel_saving = 0.05
assert kernel_saving / seconds < 0.01
print("CPU shuffle bound:", seconds, "seconds before additional overhead")
```

**Expected observation:** Ten-second payload lower bound; 50 ms kernel saving is below 1 percent of it.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `gib` | `1073741824` |
| `payload` | `10737418240` |
| `bandwidth` | `1073741824` |
| `seconds` | `10.0` |
| `kernel_saving` | `0.05` |

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-122.md) before opening hints.

### Exercise 1: Compute transfer lower bound

**Trap to avoid:** Spending effort to halve a 100 ms kernel, saving 50 ms, addresses less than 1 percent of the 10-second floor, as the reference asserts with `kernel_saving/seconds < 0.01`.

### Exercise 2: Identify local versus network time

**Trap to avoid:** Profiling only the GPU kernels shows local compute and misses fetch wait time, which may dominate. A GPU profile of a shuffle-bound stage can look idle for long stretches, and that idle time is exactly the network wait.

### Exercise 3: Explain pre-aggregation

**Trap to avoid:** Pre-aggregating a non-associative operation, such as a median computed from partial medians, produces wrong results.

### Exercise 4: List transport qualification

**Trap to avoid:** Enabling the transport setting and assuming it is active skips checking whether it actually carried traffic. A missing library on one host can silently route that host's traffic over the default path.

### Exercise 5: Separate startup settings

**Trap to avoid:** Setting a shuffle manager in an existing session and attributing later timing changes to it measures noise. Any improvement seen there comes from caching, warm JIT code or variation between runs.

### Exercise 6: Design a bounded shuffle comparison

**Trap to avoid:** Comparing configurations on different data sizes confounds the transport effect with payload size. Different partition counts also change the number of shuffle blocks, which affects per-block overhead independently of bandwidth.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Divide the payload size by the effective bandwidth, keeping the units consistent.
2. Time the complete stage, then separate the time spent in local operators from the time spent moving data.
3. Ask whether partial results can be combined before the shuffle without changing the aggregate's meaning.
4. List the hardware, topology, libraries and real traffic test an accelerated transport needs before you trust it.
5. Ask which shuffle settings can change in a running session and which need fresh executors.
6. Use identical partitioned fixtures for both shuffle paths and record bytes, spills and the output rows.

## Common mistakes and self-check

A common mistake is optimizing a local kernel when the stage is limited by moving data. Moving 10 GiB over an effective 1 GiB/s path takes at least 10 seconds, so saving 50 ms in a kernel changes almost nothing. Another is assuming RDMA or GPUDirect works because a library is installed. Fix both by measuring the complete stage, establishing an ordinary shuffle baseline and qualifying any accelerated transport on real hardware and topology before comparing.

**Misconception:** Adding more shuffle partitions always spreads the network load and speeds up the stage. **Correction:** More partitions create more, smaller blocks. Each block needs metadata, requests and buffer space, and many tiny blocks can be slower to fetch and process than fewer large ones. The bytes crossing the network stay the same unless the query changes. Measure total shuffle bytes, block counts and fetch wait time, and change the partition count in bounded steps alongside the semantic checks.

**Evidence limit:** The reference computes a ten-second payload lower bound and a 50 ms kernel saving. It sends no network traffic, so real bandwidth, retries, spill and transport compatibility must be measured on owned hosts with a bounded fixture.

1. What costs make up a shuffle?
2. When is pre-aggregation a valid rewrite?
3. Why should a lesson pad not change cluster settings?

Answers: [self-check answers](../solutions/cuda-122_solutions.md#self-check-answers).

## Primary references

- [GPU Spark tuning guide](https://docs.nvidia.com/cudf-spark/latest/tuning-guide.html)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-122: Shuffle, transport and network bottlenecks.
Read courses/cuda/spark/guides/cuda-122.md and courses/cuda/spark/lessons/cuda-122.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
