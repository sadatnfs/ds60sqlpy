# cuda-071: A timing experiment that measures the right thing

**Route:** CUDA Python and machine learning. **Stage:** beginner. **Prerequisites:** `cuda-007`, `cuda-008`, `cuda-067`, `cuda-070`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **identify the timing boundary**, **separate first-call compile time**, and **explain why CPU trace is not a benchmark** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

A host timer around an asynchronous launch may measure enqueue latency rather than completed arithmetic. GPU events delimit work in a stream; host end-to-end timing must wait for all work needed by the output. These boundaries answer different questions. Warmup can include context creation, library initialization, compilation and allocator population, so report cold-start cost separately from repeated steady-state samples.

Use a distribution rather than one flattering minimum. Median summarizes the middle observation, while a tail statistic describes slow requests. Record sample count, workload size, dtype, transfer policy, synchronization and competing load. A speedup should compare equal outputs and equally complete work. This chapter's CPU trace arithmetic is deliberately a model: it cannot establish a GPU speedup.



## Worked examples

### Worked example 1

A launch returns at 2 microseconds but the output finishes at 102 microseconds. A host timer stopped at return undercounts the operation by a factor of 51.

### Worked example 2

For completed times [10,11,10,12,100] milliseconds, the median is 11 while the maximum is 100. Removing the last sample without explaining its cause hides tail behavior.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
import statistics

samples = [10, 11, 10, 12, 100]
assert statistics.median(samples) == 11
submit_us, finish_us = 2, 102
assert finish_us / submit_us == 51
print("CPU trace analysis: median", statistics.median(samples), "ms; tail", max(samples))
```

**Expected observation:** Median 11 ms and maximum 100 ms, from synthetic trace data.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Optional NVIDIA CUDA lab

The **CuPy on NVIDIA CUDA** variant executes the actual operation with CuPy in the separately prepared `cuda-python` profile. It refuses a missing device instead of switching to CPU. Keep inputs bounded as supplied; inspect the device, synchronize and compare with the CPU reference. The profile must pass real host/device readiness checks. Successful syntax checking on a Mac is not GPU qualification.

```python
"""Optional NVIDIA CUDA lab. No CPU fallback or external dataset."""

import math
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

### Exercise 1: Identify the timing boundary

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **identify the timing boundary** in the examples above.

### Exercise 2: Compute the median

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **compute the median** in the examples above.

### Exercise 3: Add transfer cost

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **add transfer cost** in the examples above.

### Exercise 4: Separate first-call compile time

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **separate first-call compile time** in the examples above.

### Exercise 5: Design equal-work comparison

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **design equal-work comparison** in the examples above.

### Exercise 6: Explain why CPU trace is not a benchmark

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **explain why CPU trace is not a benchmark** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Identify the timing boundary".
2. Change one assumption in worked example 2 while preserving the declared contract: compute the median.
3. Trace the CPU program's variables before adding hardware behavior: add transfer cost.
4. Draw producers, consumers and the exact operation boundary for the task "Separate first-call compile time".
5. Separate what the small fixture establishes from what the real runtime must show: design equal-work comparison.
6. Write a counterexample to an overbroad claim before you explain why CPU trace is not a benchmark.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Identify the timing boundary`. For the final claim use `Explain why CPU trace is not a benchmark`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Ask an AI tutor about this lesson

> I am studying `cuda-071` using `courses/cuda/python/guides/cuda-071.md` and `courses/cuda/python/lessons/cuda-071.md`. Help me reason about A timing experiment that measures the right thing. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [CuPy array and installation documentation](https://docs.cupy.dev/en/v13.6.0/)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
