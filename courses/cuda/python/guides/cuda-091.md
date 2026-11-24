# cuda-091: Layouts, convolutions and library algorithm selection

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-066`, `cuda-087`, `cuda-090`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **state cross-correlation convention**, **compare forward and backward**, and **design two shape cases** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

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

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

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

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Equal framework lanes

### PyTorch

Understand NCHW shapes and channels-last memory format as separate concepts. Compare the native convolution expression and gradients before benchmarking layout transformations.

### TensorFlow

Understand NHWC/NCHW data_format and the exact tensor shape expected by tf.nn or Keras layers. Preserve cross-correlation convention and include conversions in timing.

Choose either lane first, then compare the other using identical mathematical inputs. Framework-specific shape, mode and optimizer rules must be checked separately. Both use offline synthetic examples; no model hub or dataset download is triggered.

## Executable framework practice

The variant chooser offers **PyTorch on CPU**, **TensorFlow on CPU**, and separate **NVIDIA CUDA** versions. CPU versions force CPU placement. CUDA versions require the named GPU profile and refuse to silently fall back. Each complete program uses the same tiny deterministic objective, bounded tensors and local synthetic data. Read its source before running; a framework pass establishes only that variant and environment.

The checkpoint demonstration is in-memory. It teaches what state must be saved; it does not export a durable model artifact or preserve an in-flight device context. Advanced custom-op, distributed and engine-building projects remain separately prepared external workflows.

## Practice and transfer

### Exercise 1: State cross-correlation convention

**Trap to avoid:** Writing a reference with `k[len(k)-1-j]`, textbook convolution, flips every sign compared with the library, which looks like a broken GPU kernel.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 2: Calculate output length

**Trap to avoid:** Using input length as output length assumes same padding, adding an output whose computation needs a value beyond the input.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 3: Count layout conversion cost

**Trap to avoid:** Counting only the faster convolution, 1 ms against 2, declares conversion a win even for a single call.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 4: Compare forward and backward

**Trap to avoid:** Benchmarking only the forward pass and applying the result to training ignores roughly two thirds of the convolution work.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 5: Explain algorithm warmup

**Trap to avoid:** Timing the first iteration and concluding the configuration is slow measures the search.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 6: Design two shape cases

**Trap to avoid:** Testing a single shape and generalizing the chosen layout risks regressions at other batch sizes. Production traffic that mixes sizes then sees the slow path.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "State cross-correlation convention".
2. Change one assumption in worked example 2 while preserving the declared contract: calculate output length.
3. Trace the CPU program's variables before adding hardware behavior: count layout conversion cost.
4. Draw producers, consumers and the exact operation boundary for the task "Compare forward and backward".
5. Separate what the small fixture establishes from what the real runtime must show: explain algorithm warmup.
6. Write a counterexample to an overbroad claim before you design two shape cases.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `State cross-correlation convention`. For the final claim use `Design two shape cases`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

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
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-091: Layouts, convolutions and library algorithm selection.
Read courses/cuda/python/guides/cuda-091.md and courses/cuda/python/lessons/cuda-091.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
