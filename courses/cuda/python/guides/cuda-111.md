# cuda-111: A profiler-guided kernel case study

**Route:** CUDA Python and machine learning. **Stage:** advanced. **Prerequisites:** `cuda-079`, `cuda-085`, `cuda-092`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Calculate arithmetic intensity.
- Count eliminated bytes.
- Name a profiler counter.
- Design one controlled change.
- Test a boundary shape.
- Explain a failed optimization.

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

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-111_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-111_cpu.py
```

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

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-111.md) before opening hints.

### Exercise 1: Calculate arithmetic intensity

**Trap to avoid:** Dividing bytes by operations gives 2 and inverts the conclusion, suggesting the kernel is compute-heavy.

### Exercise 2: Count eliminated bytes

**Trap to avoid:** Counting only the avoided write gives 4096 bytes and underestimates the saving by half.

### Exercise 3: Name a profiler counter

**Trap to avoid:** Using only total kernel time cannot separate fewer bytes from other effects. Time can also change because of clock variation or a different compiled instruction mix, so a timing-only comparison leaves the mechanism unknown.

### Exercise 4: Design one controlled change

**Trap to avoid:** Applying fusion and a new block size together leaves the source of a speedup ambiguous. If one change helps and the other hurts, the combined result may even show no difference and hide both effects.

### Exercise 5: Test a boundary shape

**Trap to avoid:** Testing only 1024 elements misses an off-by-one bounds check that writes past the end on 1023.

### Exercise 6: Explain a failed optimization

**Trap to avoid:** Reporting the fused version as an improvement because bytes fell ignores the measured timing. The bytes counter confirms the mechanism worked, but the goal was throughput, and that goal was not met for this shape.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Divide the operation count by the bytes moved.
2. Count the intermediate's bytes once for the write you avoid and once more for the read you avoid.
3. Pick a counter that measures memory traffic or the stall reason your hypothesis predicts.
4. Change one mechanism and keep the shapes, dtype, inputs and timing method identical.
5. Use a size that is not a multiple of the tile or block, plus a very small case.
6. Relate the measured resource use, such as registers or active blocks, to why the timing did not improve.

## Common mistakes and self-check

A common mistake is accepting a traffic model's prediction as a result. Fusion removes an intermediate write and read in the model, but extra register pressure or fewer active blocks can make it slower for some shapes. Another is changing several things at once, so no single cause can be credited. Fix both by changing one mechanism at a time against an unchanged library baseline, checking numerical results and boundary shapes after every change and keeping failed optimizations in the record with the evidence that rejected them.

**Misconception:** If the arithmetic intensity model says an operation is memory bound, reducing bytes will make it faster. **Correction:** The model is a hypothesis built from counted operations and bytes; real behavior also depends on caching, coalescing, occupancy and launch overhead, which the model ignores. Use the profiler to check achieved bandwidth and compute utilization for the target shape. If achieved bandwidth is already far below the device's capability, the bottleneck may be latency or the access pattern rather than total bytes, and cutting bytes alone may not help.

**Evidence limit:** The reference computes an intensity of 0.5 operations per byte and 8192 removable bytes from a simplified model. Whether the kernel is really bandwidth or compute limited, and whether fusion helps, requires profiler counters on the target device and shape.

1. What does a low arithmetic intensity suggest?
2. Why can a fused kernel be slower?
3. Why include a failed optimization in the case study?

Answers: [self-check answers](../solutions/cuda-111_solutions.md#self-check-answers).

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-111: A profiler-guided kernel case study.
Read courses/cuda/python/guides/cuda-111.md and courses/cuda/python/lessons/cuda-111.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
