# cuda-068: Array operations before custom kernels

**Route:** CUDA Python and machine learning. **Stage:** beginner. **Prerequisites:** `cuda-066`, `cuda-067`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Compute centered columns.
- Add a constant feature.
- Implement distance directly.
- Explain expanded-form cancellation.
- Count a pairwise temporary.
- Choose a library baseline.

## Mechanism and vocabulary

Broadcasting extends dimensions of size one logically, so a column mean can be subtracted from every row without constructing a full repeated matrix. A reduction consumes an axis; matrix multiplication combines contracted dimensions. These shape rules matter before choosing a backend. Express a correct reference using clear operations, then inspect whether intermediates and repeated launches dominate the useful work.

For squared distances, expanding \((x-y)^2\) gives \(x^2+y^2-2xy\). The expanded form avoids a full pairwise difference tensor but can lose relative accuracy when large nearly equal vectors cancel. A custom fused kernel can reduce temporary traffic, yet it creates maintenance, numerical and testing obligations. A mature library baseline is therefore both a correctness comparison and a performance competitor.



### Key terms

- **Broadcasting:** A rule that stretches size-one or missing axes so arrays of different shapes combine elementwise without copying.
- **Reduction axis:** The axis that an operation such as sum or max collapses, removing that dimension from the result.
- **Pairwise temporary:** An intermediate array of size m by n created when two vectors are broadcast against each other, which can exhaust device memory.
- **Catastrophic cancellation:** Loss of significant digits when subtracting two nearly equal floating-point numbers, as in the expanded squared-distance formula.

## Worked examples

### Worked example 1

Center rows [[1,3],[3,7]] by column means [2,5], producing [[-1,-2],[1,2]]. Each centered column sums to zero.

### Worked example 2

Distance between [1,2] and [4,6] is 25. Both direct differences and the expanded identity yield 25 for this small exact case; cancellation needs an additional adversarial test.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-068_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-068_cpu.py
```

```python
rows = [[1.0, 3.0], [3.0, 7.0]]
means = [sum(row[c] for row in rows) / len(rows) for c in range(2)]
centered = [[x - m for x, m in zip(row, means, strict=True)] for row in rows]
assert centered == [[-1.0, -2.0], [1.0, 2.0]]
x, y = [1, 2], [4, 6]
distance = sum((a - b) ** 2 for a, b in zip(x, y, strict=True))
assert distance == 25
print("CPU array reference:", centered, distance)
```

**Expected observation:** Centered columns and distance 25.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `rows` | `[[1.0, 3.0], [3.0, 7.0]]` |
| `means` | `[2.0, 5.0]` |
| `centered` | `[[-1.0, -2.0], [1.0, 2.0]]` |
| `x` | `[1, 2]` |
| `y` | `[4, 6]` |
| `distance` | `25` |

## Optional NVIDIA CUDA lab

**CuPy on NVIDIA CUDA** needs the `cuda-python` profile; [lab rules](../../STUDY-GUIDE.md#python-gpu-and-framework-labs).

```python
"""Optional NVIDIA CUDA lab. No CPU fallback or external dataset."""

import cupy as cp

if cp.cuda.runtime.getDeviceCount() < 1:
    raise RuntimeError("This variant requires an explicitly prepared NVIDIA CUDA GPU")
cp.cuda.Device(0).use()

x = cp.asarray([[1.0, 3.0], [3.0, 7.0]], dtype=cp.float32)
centered = x - cp.mean(x, axis=0)
cp.testing.assert_allclose(centered, cp.asarray([[-1, -2], [1, 2]], dtype=cp.float32))
cp.cuda.get_current_stream().synchronize()
print("CUDA centered features:", cp.asnumpy(centered).tolist())
```

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-068.md) before opening hints.

### Exercise 1: Compute centered columns

**Trap to avoid:** Subtracting row means instead is tempting because they are also 2 and 5 here, a coincidence of this data. Broadcasting them down the wrong axis gives `[[-1,1],[-2,2]]`; the shapes still match, so no error appears, and the columns no longer sum to zero.

### Exercise 2: Add a constant feature

**Trap to avoid:** Dividing by the column standard deviation after centering, as in standardization, divides zero by zero for this column and produces NaN that spreads into later steps.

### Exercise 3: Implement distance directly

**Trap to avoid:** Taking a square root and reporting 5 answers a different question. The chapter defines squared distance, and mixing the two breaks comparisons against the reference.

### Exercise 4: Explain expanded-form cancellation

**Trap to avoid:** Concluding that the expanded form is safe because the small worked example matches is the trap. Exact agreement on tiny integers says nothing about inputs where the squared norms dominate.

### Exercise 5: Count a pairwise temporary

**Trap to avoid:** Counting only the output `N*M` elements underestimates peak memory by a factor of D. The allocation fails or swaps even though the result itself would fit.

### Exercise 6: Choose a library baseline

**Trap to avoid:** Starting with a raw kernel for centering means writing reduction, broadcasting and tail handling by hand, with no reference to tell whether a wrong column mean is a kernel bug or a math bug.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Average each column of `[[1,3],[3,7]]` first, then subtract that row vector from both rows.
2. Append a column of identical values and compute its mean before subtracting anything.
3. Subtract coordinates pairwise for `[1,2]` and `[4,6]`, square each difference, then add them.
4. Repeat the expanded identity with two large, nearly equal vectors and count how many float32 digits survive the subtraction.
5. Multiply N, M and D for the broadcast difference tensor, then multiply by the float32 itemsize.
6. Before writing a kernel, list which library calls already compute the centering and the distance with tested edge handling.

## Common mistakes and self-check

A common mistake is trusting the expanded distance formula because it matches the direct form on small integers, as in worked example 2. The identity is exact algebra but not exact floating point: with large nearly equal vectors, subtracting squared norms cancels most significant digits. Fix it by keeping the direct difference form as the reference, and add an adversarial test with large close values before accepting the expanded or fused version.

**Evidence limit:** The reference verifies centering and one distance with small exact integers. It cannot reveal float32 cancellation, temporary memory pressure from broadcasting, or whether a fused kernel beats a library call; those need adversarial inputs and measured runs.

1. How does broadcasting subtract column means without building a repeated matrix?
2. What property of the centered result checks the computation?
3. Why is a mature library baseline also a performance competitor?

Answers: [self-check answers](../solutions/cuda-068_solutions.md#self-check-answers).

## Primary references

- [CuPy array and installation documentation](https://docs.cupy.dev/en/v13.6.0/)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-068: Array operations before custom kernels.
Read courses/cuda/python/guides/cuda-068.md and courses/cuda/python/lessons/cuda-068.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
