# cuda-077: Reduction, ordering and numerical error

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-006`, `cuda-074`, `cuda-076`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Compute a tree by hand.
- Test the odd tail.
- Construct cancellation.
- Choose absolute and relative tolerance.
- Compare atomics with staged reduction.
- Explain deterministic settings limits.

## Mechanism and vocabulary

Parallel reduction changes the grouping of additions. Real-number addition is associative; finite-precision addition generally is not. A tree reduction can produce a different result from a left-to-right loop even when both are valid implementations. Test tolerances using scale and conditioning rather than requiring arbitrary bitwise identity. Distinguish a tolerable rounding difference from a missing tail element.

Reduction also changes the parallel ownership pattern. Threads first accumulate local partials, then combine within a block, then combine block results in a later stage. A single global atomic accumulator is simpler but can contend and has nondeterministic addition order. Use a higher-accuracy CPU sum where appropriate, test cancellation-heavy inputs, and document dtype and accumulation precision.



### Key terms

- **Non-associative addition:** Floating-point addition whose result depends on grouping because each step rounds.
- **Tree reduction:** A pairwise combining order that halves the active values each step and rounds differently from a sequential sum.
- **Absolute and relative tolerance:** Bounds that accept a result when its error is small in absolute terms or relative to the magnitude of the expected value.
- **Deterministic algorithm setting:** A framework option that selects reproducible kernels, often at a performance cost.

## Worked examples

### Worked example 1

For [1e16,1,-1e16], a naive left sum loses the one on common binary 64 arithmetic, while math.fsum preserves it. The input is intentionally cancellation-sensitive.

### Worked example 2

For [1,2,3,4,5], a padded pair tree produces 15. A faulty tree that ignores the fifth value produces 10, which is an indexing bug rather than rounding noise.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-077_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-077_cpu.py
```

```python
import math

values = [1e16, 1.0, -1e16]
assert math.fsum(values) == 1.0
items = [1, 2, 3, 4, 5]
while len(items) > 1:
    items = [sum(items[i : i + 2]) for i in range(0, len(items), 2)]
assert items == [15]
print("CPU reduction reference:", math.fsum(values), items[0])
```

**Expected observation:** Accurate cancellation sum 1 and tail-preserving sum 15.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `values` | `[1e+16, 1.0, -1e+16]` |
| `items` | `[15]` |

## Optional NVIDIA CUDA lab

**CuPy on NVIDIA CUDA** needs the `cuda-python` profile; [lab rules](../../STUDY-GUIDE.md#python-gpu-and-framework-labs).

```python
"""Optional NVIDIA CUDA lab. No CPU fallback or external dataset."""

import math

import cupy as cp

if cp.cuda.runtime.getDeviceCount() < 1:
    raise RuntimeError("This variant requires an explicitly prepared NVIDIA CUDA GPU")
cp.cuda.Device(0).use()

values = [1.0, 2.0, 3.0, 4.0, 5.0]
x = cp.asarray(values, dtype=cp.float64)
result = float(cp.sum(x).get())
assert math.isclose(result, math.fsum(values), rel_tol=1e-12, abs_tol=1e-12)
cp.cuda.get_current_stream().synchronize()
print("CUDA library reduction:", result, "; order-sensitive cases need a documented tolerance")
```

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-077.md) before opening hints.

### Exercise 1: Compute a tree by hand

**Trap to avoid:** Pairing only `range(0, len(items) - 1, 2)` drops the odd element at each odd level. For this input the result becomes 10 and the error looks small enough to mistake for rounding.

### Exercise 2: Test the odd tail

**Trap to avoid:** Using a tolerance like `abs(result - 15) < 10` would accept 10. Picking tolerances that wide hides structural bugs inside numerical noise.

### Exercise 3: Construct cancellation

**Trap to avoid:** Using `[1.0, 2.0, 3.0]` as the cancellation test shows nothing, since every order gives 6 exactly. A test needs magnitudes far enough apart to exceed the mantissa.

### Exercise 4: Choose absolute and relative tolerance

**Trap to avoid:** Using relative tolerance alone with an expected value of 0 requires exact equality. Any reordering then fails, even though both answers are within normal rounding of the large terms.

### Exercise 5: Compare atomics with staged reduction

**Trap to avoid:** Claiming the atomic version is deterministic because each update is indivisible confuses atomicity with order. Each addition is safe, but the sequence of additions still varies.

### Exercise 6: Explain deterministic settings limits

**Trap to avoid:** Treating a deterministic flag as a promise of identical results across machines leads to bit-exact comparisons between environments that fail for legitimate reasons.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Pair adjacent values of `[1,2,3,4,5]`, add each pair, and carry the unpaired element to the next level.
2. Check whether your tree still contains the fifth value after the first level.
3. Add a very large number, its negative and a small residual, then compare a left-to-right sum with `math.fsum`.
4. Ask what a purely relative tolerance allows when the expected answer is close to zero.
5. Compare one global counter that every thread updates with per-block partial sums combined later.
6. Ask whether repeating a run on the same machine says anything about a different GPU or library version.

## Common mistakes and self-check

A common mistake is treating every mismatch between a parallel sum and a sequential loop as harmless rounding. In worked example 2 a faulty tree returns 10 instead of 15 because it drops the fifth value; that is an indexing bug, not rounding noise. The opposite mistake is demanding bitwise identity across orderings. Fix both by testing odd tails explicitly, comparing with a higher-accuracy CPU sum and setting absolute and relative tolerances from the data's scale.

**Evidence limit:** The reference uses `math.fsum` and a padded tree on tiny inputs. It shows the expected values; it cannot show the error a real float32 tree or atomic accumulator produces, which depends on the device's grouping and arrival order.

1. Why can a tree reduction differ from a left-to-right loop?
2. How do you tell rounding noise from a missing element?
3. Why does a sum near zero need an absolute tolerance?

Answers: [self-check answers](../solutions/cuda-077_solutions.md#self-check-answers).

## Primary references

- [NVIDIA CUDA Python introduction](https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/intro-to-cuda-python.html)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-077: Reduction, ordering and numerical error.
Read courses/cuda/python/guides/cuda-077.md and courses/cuda/python/lessons/cuda-077.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
