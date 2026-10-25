# cuda-111: A profiler-guided kernel case study

**Route:** CUDA Python and machine learning. **Stage:** advanced. **Prerequisites:** `cuda-079`, `cuda-085`, `cuda-092`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **calculate arithmetic intensity**, **design one controlled change**, and **explain a failed optimization** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Choose one operation, such as a bounded LayerNorm or segmented reduction, and derive an operation-count and byte-traffic model. Arithmetic intensity is operations divided by transferred bytes. A bandwidth-limited hypothesis suggests reducing traffic; a compute-limited hypothesis suggests improving arithmetic utilization. These bounds are simplified and need real profiler evidence for the target shape.

Change one mechanism at a time and keep an unchanged library baseline. Resource usage can reverse an apparent optimization: extra fusion may increase register pressure, and a larger tile may reduce active blocks. Test numerical behavior and boundary shapes after every change. Include a failed optimization because explaining why a hypothesis failed is part of independent performance engineering.



## Worked examples

### Worked example 1

An operation performs 4096 arithmetic operations while moving 8192 bytes, giving intensity 0.5 operations/byte in the model. This low ratio motivates examining memory traffic.

### Worked example 2

Fusion removes one intermediate write and read but raises register use. The expected traffic saving is a hypothesis; actual throughput might worsen for some shapes.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
operations, bytes_moved = 4096, 8192
intensity = operations / bytes_moved
intermediate = 1024 * 4
saved = 2 * intermediate
assert intensity == 0.5 and saved == 8192
print("CPU roofline inputs:", intensity, "operations/byte; removable traffic", saved)
```

**Expected observation:** Intensity 0.5 and hypothetical 8192 bytes removable traffic.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Calculate arithmetic intensity

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **calculate arithmetic intensity** in the examples above.

### Exercise 2: Count eliminated bytes

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **count eliminated bytes** in the examples above.

### Exercise 3: Name a profiler counter

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **name a profiler counter** in the examples above.

### Exercise 4: Design one controlled change

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **design one controlled change** in the examples above.

### Exercise 5: Test a boundary shape

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **test a boundary shape** in the examples above.

### Exercise 6: Explain a failed optimization

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **explain a failed optimization** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Calculate arithmetic intensity".
2. Change one assumption in worked example 2 while preserving the declared contract: count eliminated bytes.
3. Trace the CPU program's variables before adding hardware behavior: name a profiler counter.
4. Draw producers, consumers and the exact operation boundary for the task "Design one controlled change".
5. Separate what the small fixture establishes from what the real runtime must show: test a boundary shape.
6. Write a counterexample to an overbroad claim before you explain a failed optimization.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Calculate arithmetic intensity`. For the final claim use `Explain a failed optimization`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Ask an AI tutor about this lesson

> I am studying `cuda-111` using `courses/cuda/python/guides/cuda-111.md` and `courses/cuda/python/lessons/cuda-111.md`. Help me reason about A profiler-guided kernel case study. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
