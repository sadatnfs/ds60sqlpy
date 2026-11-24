# cuda-111: A profiler-guided kernel case study

**Route:** CUDA Python and machine learning. **Stage:** advanced. **Prerequisites:** `cuda-079`, `cuda-085`, `cuda-092`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **calculate arithmetic intensity**, **design one controlled change**, and **explain a failed optimization** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Choose one operation, such as a bounded LayerNorm or segmented reduction, and derive an operation-count and byte-traffic model. Arithmetic intensity is operations divided by transferred bytes. A bandwidth-limited hypothesis suggests reducing traffic; a compute-limited hypothesis suggests improving arithmetic utilization. These bounds are simplified and need real profiler evidence for the target shape.

Change one mechanism at a time and keep an unchanged library baseline. Resource usage can reverse an apparent optimization: extra fusion may increase register pressure, and a larger tile may reduce active blocks. Test numerical behavior and boundary shapes after every change. Include a failed optimization because explaining why a hypothesis failed is part of independent performance engineering.



### Key terms

- **Arithmetic intensity:** Floating-point operations performed per byte of memory traffic.
- **Bandwidth-limited kernel:** A kernel whose time is set by memory traffic because its arithmetic intensity is below the device's balance point.
- **Compute-limited kernel:** A kernel whose time is set by arithmetic throughput because its arithmetic intensity is above the balance point.
- **Controlled change:** Changing one variable at a time so a measured difference can be attributed to it.

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

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `operations` | `4096` |
| `bytes_moved` | `8192` |
| `intensity` | `0.5` |
| `intermediate` | `4096` |
| `saved` | `8192` |

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Calculate arithmetic intensity

**Trap to avoid:** Dividing bytes by operations gives 2 and inverts the conclusion, suggesting the kernel is compute-heavy.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 2: Count eliminated bytes

**Trap to avoid:** Counting only the avoided write gives 4096 bytes and underestimates the saving by half.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 3: Name a profiler counter

**Trap to avoid:** Using only total kernel time cannot separate fewer bytes from other effects. Time can also change because of clock variation or a different compiled instruction mix, so a timing-only comparison leaves the mechanism unknown.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 4: Design one controlled change

**Trap to avoid:** Applying fusion and a new block size together leaves the source of a speedup ambiguous. If one change helps and the other hurts, the combined result may even show no difference and hide both effects.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 5: Test a boundary shape

**Trap to avoid:** Testing only 1024 elements misses an off-by-one bounds check that writes past the end on 1023.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 6: Explain a failed optimization

**Trap to avoid:** Reporting the fused version as an improvement because bytes fell ignores the measured timing. The bytes counter confirms the mechanism worked, but the goal was throughput, and that goal was not met for this shape.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

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

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-111: A profiler-guided kernel case study.
Read courses/cuda/python/guides/cuda-111.md and courses/cuda/python/lessons/cuda-111.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
