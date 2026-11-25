# cuda-100: Attention as GPU work

**Route:** CUDA Python and machine learning. **Stage:** advanced. **Prerequisites:** `cuda-087`, `cuda-090`, `cuda-092`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Compute stable softmax.
- Draw a causal mask.
- Count score-matrix bytes.
- Define fully masked behavior.
- Compare fused and reference gradients.
- Separate backend selection from API name.

## Mechanism and vocabulary

Attention forms query-key scores, applies scaling and masks, normalizes with softmax, and combines values. Materializing a full sequence-by-sequence score matrix creates a quadratic intermediate. Fused algorithms can reorganize computation to reduce memory traffic while preserving the intended operation, but selected backend, dtype, head size and mask affect available implementations.

Stable softmax subtracts each row's maximum before exponentiation. A causal mask prevents positions from attending to later tokens; a padding mask excludes invalid positions. Define behavior for fully masked rows rather than accepting NaNs by accident. PyTorch scaled-dot-product attention and TensorFlow attention paths need actual backend inspection and forward/backward comparison. An API name alone cannot prove a particular fused kernel ran.

## Follow attention from shapes to memory traffic

For one head, queries have shape \((L_q,d)\), keys \((L_k,d)\), and values \((L_k,d_v)\). Scores have shape \((L_q,L_k)\). The operation is:

\[
S=QK^{\mathsf T}/\sqrt{d},\quad
P=\operatorname{softmax}(S+M),\quad
O=PV.
\]

The mask \(M\) contributes zero for allowed positions and an effectively negative-infinite value for excluded positions under the chosen implementation. Causal masks depend on query/key position alignment, especially when decode uses a short query and a longer cache. Do not assume a square lower-triangular mask is correct for every cache layout.

A straightforward implementation writes the entire score matrix, reads it for normalization, writes probabilities, then reads those for the value product. When sequence length doubles, a square score matrix has four times as many elements. Memory-efficient attention reorganizes tiling and normalization to avoid some full intermediates. This is an algorithmic memory-traffic improvement, not a claim that all attention has linear arithmetic complexity.

For a row, subtracting the maximum leaves softmax unchanged because the same exponential factor divides out. A streaming/tiled implementation must combine partial normalization state correctly when a later tile changes that maximum. That state consists of a running maximum, a normalized exponential sum and a correspondingly rescaled weighted-value accumulator. Losing one rescaling factor can produce plausible-looking but wrong outputs.

Validation should include unequal query/key lengths, a causal case, padding, non-unit upstream gradients, and the explicitly defined fully masked behavior. The small PyTorch variant compares a supported attention API to the explicit reference; the TensorFlow variant builds the same reference arithmetic. Neither prints a fictitious fused-kernel identity. A real fast-backend comparison requires the prepared implementation, device trace and accepted dtype/head-size matrix.


### Key terms

- **Score matrix:** The query-key dot products for every pair of positions, with sequence length squared entries per head.
- **Causal mask:** A mask that blocks each position from attending to later positions.
- **Quadratic memory:** Memory growth proportional to the square of sequence length when the score matrix is materialized.
- **Fused attention kernel:** An implementation that computes softmax attention in tiles without storing the full score matrix.
- **Fully masked row:** A query row with every score masked, whose softmax is undefined and can produce NaN unless handled.

## Worked examples

### Worked example 1

For scores [1000,1001], direct exponentiation can overflow. Subtracting 1001 yields [-1,0] and well-behaved probabilities summing to one.

### Worked example 2

A causal row for token 0 can see only token 0. Masking later positions before normalization gives weight 1 to the sole valid position.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-100_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-100_cpu.py
```

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

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `scores` | `[1000.0, 1001.0]` |
| `shift` | `1001.0` |
| `exp` | `[0.36787944117144233, 1.0]` |
| `weights` | `[0.2689414213699951, 0.7310585786300049]` |
| `causal` | `[[1, 0, 0], [1, 1, 0], [1, 1, 1]]` |

## Equal framework lanes

### PyTorch

Compare scaled_dot_product_attention with explicit scores, masks, softmax and value multiplication. Record actual backend selection when exposed; test dropout policy and backward separately.

### TensorFlow

Build the explicit tf.matmul/mask/softmax reference first. Compare an optional prepared optimized attention path with the same shapes and gradients rather than assuming every Keras attention layer selects the same kernel.

Lane rules: [framework labs](../../STUDY-GUIDE.md#python-gpu-and-framework-labs).

## Executable framework practice

Run the **PyTorch** and **TensorFlow** variants on CPU first; [lab rules](../../STUDY-GUIDE.md#python-gpu-and-framework-labs).

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-100.md) before opening hints.

### Exercise 1: Compute stable softmax

**Trap to avoid:** Exponentiating directly, `math.exp(1000)`, overflows to infinity in float64 and the division produces NaN. In float16 the overflow happens above about 11.

### Exercise 2: Draw a causal mask

**Trap to avoid:** Using `j < i` excludes the diagonal, leaving row 0 with no allowed positions and producing NaN in softmax.

### Exercise 3: Count score-matrix bytes

**Trap to avoid:** Estimating attention memory as linear in sequence length misses the quadratic term, which dominates for long sequences.

### Exercise 4: Define fully masked behavior

**Trap to avoid:** Leaving it undefined lets NaN appear only with certain padding patterns.

### Exercise 5: Compare fused and reference gradients

**Trap to avoid:** Comparing only forward outputs leaves backward bugs undetected, and comparing a float16 fused result to a float32 reference with float32 tolerance reports false failures.

### Exercise 6: Separate backend selection from API name

**Trap to avoid:** Assuming the flash backend ran because the function was called leads to wrong memory estimates when it silently fell back to math.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Subtract the row's largest score from every score before exponentiating, then normalize.
2. For each query position, mark which key positions are at or before it.
3. Multiply batch, heads, sequence length squared and the bytes per element.
4. Decide what a row with no valid key should return, and make it an explicit rule instead of a NaN.
5. Compare masked outputs and gradients from the fused path and a plain reference at a stated tolerance.
6. Ask what runtime evidence would show which backend actually executed.

## Common mistakes and self-check

A common mistake is exponentiating raw scores; values like 1000 overflow and produce infinities or NaNs. Another is masking after softmax, which leaves probability on forbidden positions, or leaving a fully masked row to return NaNs by accident. Fix these by subtracting the row maximum, applying causal and padding masks before normalization and defining behavior for fully masked rows, then comparing a fused path with a reference in both forward and backward.

**Evidence limit:** The reference computes stable probabilities that sum to 1 and a lower-triangular causal mask in Python. It cannot show which fused kernel a framework selects, since that depends on backend, dtype, head size and mask.

1. Why does attention create a quadratic intermediate?
2. Does subtracting the row maximum change the softmax result?
3. Does calling a scaled-dot-product attention API prove a fused kernel ran?

Answers: [self-check answers](../solutions/cuda-100_solutions.md#self-check-answers).

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-100: Attention as GPU work.
Read courses/cuda/python/guides/cuda-100.md and courses/cuda/python/lessons/cuda-100.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
