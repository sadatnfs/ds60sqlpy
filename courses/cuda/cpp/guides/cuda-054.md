# cuda-054: Attention and memory-aware algorithm design

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-046`, `cuda-051`, `cuda-052`, `cuda-053`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Implement tiled attention with online softmax that matches the reference and report memory use and supported masks.

**Scope:** Queries, keys, values, score matrix size, stable softmax, tiling, online normalization and recomputation.

**Evidence to produce:** Agreement with the reference and a memory/time report that states supported shapes and masks.

## Purpose, vocabulary and mental model

Scaled dot-product attention forms scores from queries and keys, normalizes each score row with softmax and combines values using those weights. Materializing the entire score matrix costs storage proportional to sequence length squared. Tiling can avoid retaining that large intermediate by maintaining an online maximum, normalization sum and weighted output accumulator. When a new tile raises the maximum, rescale earlier accumulators before combining them. Masking and training's backward needs add contracts. A tiny educational online algorithm demonstrates memory-aware mathematics; it is not a production replacement for specialized attention libraries.

### Key terms

- **Scaled dot-product attention:** The operation that divides query-key dot products by the square root of the key width, applies softmax and uses the resulting weights to average the values.
- **Online softmax:** Computing softmax over tiles while updating a running maximum and denominator, so the full score row is never stored.
- **Attention mask:** A rule that excludes key positions, such as future tokens in causal attention, before normalization.
- **Quadratic memory:** Memory that grows with sequence length squared when the full score matrix is materialized.

## Mathematical contract

\[
\operatorname{Attention}(Q,K,V)=\operatorname{softmax}\left(\frac{QK^{\mathsf T}}{\sqrt{d_k}}+M\right)V
\]

The mask M, softmax axis and scaling dimension d_k are part of the model contract. The first tiny example deliberately states that its scores are unscaled.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-054_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-054_cpu.py
```

## Worked example 1: trace the mechanism

With query \([1,0]\), keys \([[1,0],[0,1]]\) and values \([[2,0],[0,4]]\), unscaled scores are \([1,0]\). Softmax weights are approximately \([0.731059,0.268941]\), giving output \([1.462117,1.075766]\). A real scaled attention contract also divides scores by square root of key dimension.

**Why:** Weights 0.731059 and 0.268941 scale [2, 0] and [0, 4] to give [1.462117, 1.075766].

```python
import math

weights = [math.exp(1) / (math.exp(1) + 1), 1 / (math.exp(1) + 1)]
out = [weights[0] * 2, weights[1] * 4]
assert abs(sum(weights) - 1) < 1e-12
assert 4096 * 4096 * 4 == 64 * 1024 * 1024
print({"unscaled_tiny_attention": out, "score_matrix_MiB": 64})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'unscaled_tiny_attention': [1.4621171572600098, 1.0757656854799804], 'score_matrix_MiB': 64}
```

**Check:** The reference asserts the weights sum to one and prints the output pair.

## Worked example 2: change a meaningful condition

For 4,096 tokens, a full score matrix has 16,777,216 elements per head and batch item. At four bytes each that is 64 MiB for scores alone. A tiled algorithm's advantage can come from avoiding traffic and storage, even if it recomputes some arithmetic.

**Why:** That is 16,777,216 scores, or 64 MiB, before any other buffer.

**Check:** The reference asserts 4096 * 4096 * 4 == 64 * 1024 * 1024.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Score query [1, 0] against keys to get [1, 0], softmax, then weight the value rows.

**Trap to avoid:** Skipping the 1 / sqrt(d) scaling by accident here matches the unscaled reference but breaks a scaled contract.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Multiply 4,096 by 4,096 by 4 bytes for one head and batch item.

**Trap to avoid:** Assuming a tiled kernel is faster only because of fewer FLOPs misses that it avoids this storage.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Apply a causal mask that leaves only the first key in the worked row.

**Trap to avoid:** Setting the masked score to 0 instead of negative infinity keeps weight on it.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why must online accumulators rescale when the maximum increases?

**Trap to avoid:** Adding new terms without rescaling mixes two reference points.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What is the policy for a completely masked row?

**Trap to avoid:** Letting the general path run leaves behavior undefined.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design an attention benchmark contract.

**Trap to avoid:** Comparing forward-only timing with a library's forward and backward is unfair.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **A short educational attention kernel is a production FlashAttention replacement or validates a complete Transformer.** A short teaching kernel proves one small contract, not a production attention library or a working Transformer. Production versions handle scaling, masking, numerically stable online softmax, many shapes and dtypes, and backward passes. Claim only what your fixtures and reference cover.

## Self-check, retrieval and transfer

1. With a causal mask that keeps only the first key, what output does worked example 1 give?
2. How large is a 2,048 token score matrix at four bytes per element?
3. Why must online accumulators rescale when the maximum increases?

Short answers are in the [separate explanations](../solutions/cuda-054_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-054: Attention and memory-aware algorithm design.
Read courses/cuda/cpp/guides/cuda-054.md and courses/cuda/cpp/lessons/cuda-054.md.
Direct prerequisites: `cuda-046`, `cuda-051`, `cuda-052`, `cuda-053`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-054_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-054_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
