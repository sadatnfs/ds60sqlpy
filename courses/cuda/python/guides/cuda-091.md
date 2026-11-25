# cuda-091: Layouts, convolutions and library algorithm selection

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-066`, `cuda-087`, `cuda-090`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- State cross-correlation convention.
- Calculate output length.
- Count layout conversion cost.
- Compare forward and backward.
- Explain algorithm warmup.
- Design two shape cases.

## Mechanism and vocabulary

A convolution's mathematical axes are distinct from its storage order. NCHW and NHWC encode where batch, channel, height and width lie; a layout conversion is real work unless a view is valid for the consuming operator. Framework and library implementations choose algorithms based on shapes, dtype, workspace and deterministic settings. The fastest choice for one shape can lose for another.

PyTorch channels-last memory format and TensorFlow data-format conventions need separate explanations because identical axis names do not imply identical APIs. Compare outputs and gradients before timing. Include input conversion, algorithm search and workspace in the appropriate cost ledger. Do not promise a universal preferred layout or treat a profiler's kernel name as proof of mathematical equivalence.



### Key terms

- **NCHW and NHWC:** Tensor layouts ordering batch, channels, height and width; channels-last NHWC often suits tensor core kernels.
- **Cross-correlation:** The sliding dot product that deep learning frameworks call convolution, computed without flipping the filter.
- **Layout conversion:** A transpose between layouts that costs memory traffic and can erase a faster kernel's benefit.
- **Algorithm selection:** Benchmarking candidate convolution algorithms for a shape and caching the fastest, which needs warmup before timing.

## Worked examples

### Worked example 1

A one-dimensional valid convolution of [1,2,3,4] with kernel [1,-1], using cross-correlation convention, gives [-1,-1,-1]. Reversing the kernel changes the sign.

### Worked example 2

A layout conversion costs 2 ms and saves 1 ms per convolution. It loses for one call but amortizes over repeated calls only if the converted data can be reused correctly.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-091_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-091_cpu.py
```

```python
x, k = [1, 2, 3, 4], [1, -1]
out = [sum(x[i + j] * k[j] for j in range(len(k))) for i in range(len(x) - len(k) + 1)]
assert out == [-1, -1, -1]
assert 2 + 1 * 1 > 2 * 1
assert 2 + 1 * 4 < 2 * 4
print("CPU convolution oracle:", out)
```

**Expected observation:** Valid cross-correlation [-1,-1,-1]; conversion amortization depends on reuse.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `x` | `[1, 2, 3, 4]` |
| `k` | `[1, -1]` |
| `out` | `[-1, -1, -1]` |

## Equal framework lanes

### PyTorch

Understand NCHW shapes and channels-last memory format as separate concepts. Compare the native convolution expression and gradients before benchmarking layout transformations.

### TensorFlow

Understand NHWC/NCHW data_format and the exact tensor shape expected by tf.nn or Keras layers. Preserve cross-correlation convention and include conversions in timing.

Lane rules: [framework labs](../../STUDY-GUIDE.md#python-gpu-and-framework-labs).

## Executable framework practice

Run the **PyTorch** and **TensorFlow** variants on CPU first; [lab rules](../../STUDY-GUIDE.md#python-gpu-and-framework-labs).

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-091.md) before opening hints.

### Exercise 1: State cross-correlation convention

**Trap to avoid:** Writing a reference with `k[len(k)-1-j]`, textbook convolution, flips every sign compared with the library, which looks like a broken GPU kernel.

### Exercise 2: Calculate output length

**Trap to avoid:** Using input length as output length assumes same padding, adding an output whose computation needs a value beyond the input.

### Exercise 3: Count layout conversion cost

**Trap to avoid:** Counting only the faster convolution, 1 ms against 2, declares conversion a win even for a single call.

### Exercise 4: Compare forward and backward

**Trap to avoid:** Benchmarking only the forward pass and applying the result to training ignores roughly two thirds of the convolution work.

### Exercise 5: Explain algorithm warmup

**Trap to avoid:** Timing the first iteration and concluding the configuration is slow measures the search.

### Exercise 6: Design two shape cases

**Trap to avoid:** Testing a single shape and generalizing the chosen layout risks regressions at other batch sizes. Production traffic that mixes sizes then sees the slow path.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Write output index i as a sum over kernel index k of input times kernel, without flipping the kernel.
2. Count how many positions a length-2 kernel can occupy fully inside a length-4 input.
3. Charge the conversion once per call that needs it, then ask how many convolutions must reuse the converted data.
4. Ask which pass training runs after the forward pass and whether it uses the same layout and algorithm.
5. Ask what the library may do on the first call for a new shape before it settles on an algorithm.
6. Keep the mathematical operation fixed and change only the batch size between the two cases.

## Common mistakes and self-check

A common mistake is assuming one layout is always faster. NCHW and NHWC store the same axes in different orders, and a conversion is real work unless the consumer can use a view. Another mistake is timing only the forward pass or treating a profiler's kernel name as proof that results match. Fix both by checking outputs and gradients first, then timing complete latency with conversion, algorithm search and workspace included, across at least two shapes.

**Evidence limit:** The reference computes the valid cross-correlation `[-1, -1, -1]` and a conversion amortization in plain Python. It cannot show which algorithm a library picks, the workspace it needs or real layout costs, which depend on shape, dtype and hardware.

1. How does a deep learning convolution usually differ from the textbook definition?
2. When does a layout conversion pay off?
3. Why might the fastest algorithm for one shape lose on another?

Answers: [self-check answers](../solutions/cuda-091_solutions.md#self-check-answers).

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-091: Layouts, convolutions and library algorithm selection.
Read courses/cuda/python/guides/cuda-091.md and courses/cuda/python/lessons/cuda-091.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
