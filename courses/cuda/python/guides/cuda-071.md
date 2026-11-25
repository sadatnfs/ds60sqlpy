# cuda-071: A timing experiment that measures the right thing

**Route:** CUDA Python and machine learning. **Stage:** beginner. **Prerequisites:** `cuda-007`, `cuda-008`, `cuda-067`, `cuda-070`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Identify the timing boundary.
- Compute the median.
- Add transfer cost.
- Separate first-call compile time.
- Design equal-work comparison.
- Explain why CPU trace is not a benchmark.

## Mechanism and vocabulary

A host timer around an asynchronous launch may measure enqueue latency rather than completed arithmetic. GPU events delimit work in a stream; host end-to-end timing must wait for all work needed by the output. These boundaries answer different questions. Warmup can include context creation, library initialization, compilation and allocator population, so report cold-start cost separately from repeated steady-state samples.

Use a distribution rather than one flattering minimum. Median summarizes the middle observation, while a tail statistic describes slow requests. Record sample count, workload size, dtype, transfer policy, synchronization and competing load. A speedup should compare equal outputs and equally complete work. This chapter's CPU trace arithmetic is deliberately a model: it cannot establish a GPU speedup.



### Key terms

- **Enqueue latency:** The host time needed to submit work to the device queue, which can be much shorter than the time the work takes to execute.
- **GPU event:** A marker recorded in a stream whose timestamps measure elapsed device time between two points.
- **Warmup:** Initial runs that absorb one-time costs such as context creation, JIT compilation and allocator growth before timing starts.
- **Median timing:** The middle value of repeated measurements, which resists outliers better than a single run or the mean.

## Worked examples

### Worked example 1

A launch returns at 2 microseconds but the output finishes at 102 microseconds. A host timer stopped at return undercounts the operation by a factor of 51.

### Worked example 2

For completed times [10,11,10,12,100] milliseconds, the median is 11 while the maximum is 100. Removing the last sample without explaining its cause hides tail behavior.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-071_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-071_cpu.py
```

```python
import statistics

samples = [10, 11, 10, 12, 100]
assert statistics.median(samples) == 11
submit_us, finish_us = 2, 102
assert finish_us / submit_us == 51
print("CPU trace analysis: median", statistics.median(samples), "ms; tail", max(samples))
```

**Expected observation:** Median 11 ms and maximum 100 ms, from synthetic trace data.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `samples` | `[10, 11, 10, 12, 100]` |
| `submit_us` | `2` |
| `finish_us` | `102` |

## Optional NVIDIA CUDA lab

**CuPy on NVIDIA CUDA** needs the `cuda-python` profile; [lab rules](../../STUDY-GUIDE.md#python-gpu-and-framework-labs).

```python
"""Optional NVIDIA CUDA lab. No CPU fallback or external dataset."""

import cupy as cp

if cp.cuda.runtime.getDeviceCount() < 1:
    raise RuntimeError("This variant requires an explicitly prepared NVIDIA CUDA GPU")
cp.cuda.Device(0).use()

x = cp.arange(4096, dtype=cp.float32)
for _ in range(2):
    y = x * 2 + 1
cp.cuda.get_current_stream().synchronize()
start, end = cp.cuda.Event(), cp.cuda.Event()
start.record()
y = x * 2 + 1
end.record()
end.synchronize()
cp.testing.assert_allclose(y, 2 * cp.arange(4096, dtype=cp.float32) + 1)
print(
    "CUDA event interval:",
    cp.cuda.get_elapsed_time(start, end),
    "ms; excludes transfers and initial compilation",
)
```

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-071.md) before opening hints.

### Exercise 1: Identify the timing boundary

**Trap to avoid:** Stopping the timer at the return reports 2 microseconds and undercounts by the factor of 51 the reference computes.

### Exercise 2: Compute the median

**Trap to avoid:** Reporting the mean, 28.6 ms, mixes the tail into the center and overstates the typical case by a factor of about 2.6.

### Exercise 3: Add transfer cost

**Trap to avoid:** Reporting only the kernel interval as latency makes a GPU path look faster than a CPU path that includes its own I/O.

### Exercise 4: Separate first-call compile time

**Trap to avoid:** Discarding the first call without reporting it hides a cost a real user pays at process start.

### Exercise 5: Design equal-work comparison

**Trap to avoid:** Comparing a float32 GPU run with a float64 CPU run reports a speedup that is partly a precision change.

### Exercise 6: Explain why CPU trace is not a benchmark

**Trap to avoid:** Copying the 11 ms median into a report as GPU latency misrepresents a CPU script's constant as a hardware result.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Mark the moment the launch call returns and the moment the output is ready. Which interval contains the arithmetic?
2. Sort the five synthetic samples and pick the middle one.
3. Draw the caller's timeline from host input to host output and place both copies on it.
4. Separate the first call's context, compilation and allocator setup from the later repeated samples.
5. List what must be identical on both sides before a ratio of times means anything: data, dtype, outputs and tolerance.
6. Ask where the trace numbers came from. Were they measured on any device, or written into the program?

## Common mistakes and self-check

The mistake this chapter targets is stopping a host timer when an asynchronous launch returns. That measures enqueue latency, 2 microseconds in worked example 1, not the 102 microseconds until the output exists. Another is reporting only the fastest sample, or deleting the 100 ms outlier without explaining it. Fix the boundary with a synchronization or GPU events, report the median with a tail statistic and the sample count, and keep cold-start time in a separate row.

**Evidence limit:** Every value in this chapter's trace is invented for teaching. The median and maximum arithmetic is exact, but it cannot support any speedup claim; a real comparison needs measured, synchronized samples of equal work on named hardware.

1. Why can a first call be much slower than later ones?
2. What does the median hide that the maximum reveals?
3. What makes two timings an equal-work comparison?

Answers: [self-check answers](../solutions/cuda-071_solutions.md#self-check-answers).

## Primary references

- [CuPy array and installation documentation](https://docs.cupy.dev/en/v13.6.0/)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-071: A timing experiment that measures the right thing.
Read courses/cuda/python/guides/cuda-071.md and courses/cuda/python/lessons/cuda-071.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
