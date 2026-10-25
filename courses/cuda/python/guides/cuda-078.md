# cuda-078: Atomics and contention

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-076`, `cuda-077`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **trace a lost update**, **count private storage**, and **specify completion before reading** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

An atomic operation updates one supported location indivisibly with respect to competing atomic operations. It does not make an entire multi-location algorithm transactional. A histogram demonstrates the need: two threads reading count 0 and both writing count 1 lose an increment. Atomic addition prevents that lost update for the counter, but every thread targeting the same bin can serialize.

Privatization reduces contention by building per-block or per-warp partial histograms and merging them later. The memory footprint grows with bin count and number of partials. Floating-point atomic addition can still vary with arrival order. Explain what is protected, what ordering is required, and whether non-atomic readers can observe partially completed results.



## Worked examples

### Worked example 1

Values [0,0,1,2,2,2] produce bins [2,1,3]. Six updates aimed at one bin would be a deliberately skewed contention case.

### Worked example 2

Two local histograms [2,1,0] and [0,0,3] merge elementwise to [2,1,3]. Local updates reduce shared contention at the expense of extra storage and a merge.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
values = [0, 0, 1, 2, 2, 2]
bins = [0] * 3
for value in values:
    bins[value] += 1
left, right = [2, 1, 0], [0, 0, 3]
merged = [a + b for a, b in zip(left, right, strict=True)]
assert bins == merged == [2, 1, 3]
print("CPU histogram oracle:", bins)
```

**Expected observation:** Histogram bins [2,1,3].

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Trace a lost update

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **trace a lost update** in the examples above.

### Exercise 2: Compute a skewed histogram

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **compute a skewed histogram** in the examples above.

### Exercise 3: Merge partials

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **merge partials** in the examples above.

### Exercise 4: Count private storage

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **count private storage** in the examples above.

### Exercise 5: Explain floating atomic order

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **explain floating atomic order** in the examples above.

### Exercise 6: Specify completion before reading

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **specify completion before reading** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Trace a lost update".
2. Change one assumption in worked example 2 while preserving the declared contract: compute a skewed histogram.
3. Trace the CPU program's variables before adding hardware behavior: merge partials.
4. Draw producers, consumers and the exact operation boundary for the task "Count private storage".
5. Separate what the small fixture establishes from what the real runtime must show: explain floating atomic order.
6. Write a counterexample to an overbroad claim before you specify completion before reading.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Trace a lost update`. For the final claim use `Specify completion before reading`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Ask an AI tutor about this lesson

> I am studying `cuda-078` using `courses/cuda/python/guides/cuda-078.md` and `courses/cuda/python/lessons/cuda-078.md`. Help me reason about Atomics and contention. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [NVIDIA CUDA Python introduction](https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/intro-to-cuda-python.html)
- [Maintained numba-cuda project](https://github.com/NVIDIA/numba-cuda)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
