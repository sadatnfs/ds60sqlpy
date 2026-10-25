# cuda-100: Attention as GPU work

**Route:** CUDA Python and machine learning. **Stage:** advanced. **Prerequisites:** `cuda-087`, `cuda-090`, `cuda-092`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **compute stable softmax**, **define fully masked behavior**, and **separate backend selection from API name** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Attention forms query-key scores, applies scaling and masks, normalizes with softmax, and combines values. Materializing a full sequence-by-sequence score matrix creates a quadratic intermediate. Fused algorithms can reorganize computation to reduce memory traffic while preserving the intended operation, but selected backend, dtype, head size and mask affect available implementations.

Stable softmax subtracts each row's maximum before exponentiation. A causal mask prevents positions from attending to later tokens; a padding mask excludes invalid positions. Define behavior for fully masked rows rather than accepting NaNs by accident. PyTorch scaled-dot-product attention and TensorFlow attention paths need actual backend inspection and forward/backward comparison. An API name alone cannot prove a particular fused kernel ran.

## Follow attention from shapes to memory traffic

For one head, queries have shape \((L_q,d)\), keys \((L_k,d)\), and values \((L_k,d_v)\). Scores have shape \((L_q,L_k)\). The operation is:

\[
S=QK^{\mathsf T}/\sqrt d,\quad
P=\operatorname{softmax}(S+M),\quad
O=PV.
\]

The mask \(M\) contributes zero for allowed positions and an effectively negative-infinite value for excluded positions under the chosen implementation. Causal masks depend on query/key position alignment, especially when decode uses a short query and a longer cache. Do not assume a square lower-triangular mask is correct for every cache layout.

A straightforward implementation writes the entire score matrix, reads it for normalization, writes probabilities, then reads those for the value product. When sequence length doubles, a square score matrix has four times as many elements. Memory-efficient attention reorganizes tiling and normalization to avoid some full intermediates. This is an algorithmic memory-traffic improvement, not a claim that all attention has linear arithmetic complexity.

For a row, subtracting the maximum leaves softmax unchanged because the same exponential factor divides out. A streaming/tiled implementation must combine partial normalization state correctly when a later tile changes that maximum. That state consists of a running maximum, a normalized exponential sum and a correspondingly rescaled weighted-value accumulator. Losing one rescaling factor can produce plausible-looking but wrong outputs.

Validation should include unequal query/key lengths, a causal case, padding, non-unit upstream gradients, and the explicitly defined fully masked behavior. The small PyTorch variant compares a supported attention API to the explicit reference; the TensorFlow variant builds the same reference arithmetic. Neither prints a fictitious fused-kernel identity. A real fast-backend comparison requires the prepared implementation, device trace and accepted dtype/head-size matrix.


## Worked examples

### Worked example 1

For scores [1000,1001], direct exponentiation can overflow. Subtracting 1001 yields [-1,0] and well-behaved probabilities summing to one.

### Worked example 2

A causal row for token 0 can see only token 0. Masking later positions before normalization gives weight 1 to the sole valid position.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
import math

scores = [1000.0, 1001.0]
shift = max(scores)
exp = [math.exp(x - shift) for x in scores]
weights = [x / sum(exp) for x in exp]
assert abs(sum(weights) - 1) < 1e-12
assert weights[1] > weights[0]
causal = [[int(j <= i) for j in range(3)] for i in range(3)]
assert causal == [[1, 0, 0], [1, 1, 0], [1, 1, 1]]
print("CPU attention oracle:", weights, causal)
```

**Expected observation:** Stable probabilities sum to 1; lower-triangular causal mask.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Equal framework lanes

### PyTorch

Compare scaled_dot_product_attention with explicit scores, masks, softmax and value multiplication. Record actual backend selection when exposed; test dropout policy and backward separately.

### TensorFlow

Build the explicit tf.matmul/mask/softmax reference first. Compare an optional prepared optimized attention path with the same shapes and gradients rather than assuming every Keras attention layer selects the same kernel.

Choose either lane first, then compare the other using identical mathematical inputs. Framework-specific shape, mode and optimizer rules must be checked separately. Both use offline synthetic examples; no model hub or dataset download is triggered.

## Executable framework practice

The variant chooser offers **PyTorch on CPU**, **TensorFlow on CPU**, and separate **NVIDIA CUDA** versions. CPU versions force CPU placement. CUDA versions require the named GPU profile and refuse to silently fall back. Each complete program uses the same tiny deterministic objective, bounded tensors and local synthetic data. Read its source before running; a framework pass establishes only that variant and environment.

The checkpoint demonstration is in-memory. It teaches what state must be saved; it does not export a durable model artifact or preserve an in-flight device context. Advanced custom-op, distributed and engine-building projects remain separately prepared external workflows.

## Practice and transfer

### Exercise 1: Compute stable softmax

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **compute stable softmax** in the examples above.

### Exercise 2: Draw a causal mask

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **draw a causal mask** in the examples above.

### Exercise 3: Count score-matrix bytes

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **count score-matrix bytes** in the examples above.

### Exercise 4: Define fully masked behavior

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **define fully masked behavior** in the examples above.

### Exercise 5: Compare fused and reference gradients

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **compare fused and reference gradients** in the examples above.

### Exercise 6: Separate backend selection from API name

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **separate backend selection from API name** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Compute stable softmax".
2. Change one assumption in worked example 2 while preserving the declared contract: draw a causal mask.
3. Trace the CPU program's variables before adding hardware behavior: count score-matrix bytes.
4. Draw producers, consumers and the exact operation boundary for the task "Define fully masked behavior".
5. Separate what the small fixture establishes from what the real runtime must show: compare fused and reference gradients.
6. Write a counterexample to an overbroad claim before you separate backend selection from API name.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Compute stable softmax`. For the final claim use `Separate backend selection from API name`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Ask an AI tutor about this lesson

> I am studying `cuda-100` using `courses/cuda/python/guides/cuda-100.md` and `courses/cuda/python/lessons/cuda-100.md`. Help me reason about Attention as GPU work. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
