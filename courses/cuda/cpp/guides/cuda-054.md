# cuda-054: Attention and memory-aware algorithm design

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-046`, `cuda-051`, `cuda-052`, `cuda-053`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Implement tiled attention with online softmax that matches the reference and report memory use and supported masks.

Work through *Attention and memory-aware algorithm design* with the concrete cases below. Finish with this evidence:
agreement with the reference and a memory/time report that states supported shapes and masks. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

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

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-054_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-054_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

With query \([1,0]\), keys \([[1,0],[0,1]]\) and values \([[2,0],[0,4]]\), unscaled scores are \([1,0]\). Softmax weights are approximately \([0.731059,0.268941]\), giving output \([1.462117,1.075766]\). A real scaled attention contract also divides scores by square root of key dimension.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
import math

weights = [math.exp(1) / (math.exp(1) + 1), 1 / (math.exp(1) + 1)]
out = [weights[0] * 2, weights[1] * 4]
assert abs(sum(weights) - 1) < 1e-12
assert 4096 * 4096 * 4 == 64 * 1024 * 1024
print({"unscaled_tiny_attention": out, "score_matrix_MiB": 64})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'unscaled_tiny_attention': [1.4621171572600098, 1.0757656854799804], 'score_matrix_MiB': 64}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

For 4,096 tokens, a full score matrix has 16,777,216 elements per head and batch item. At four bytes each that is 64 MiB for scores alone. A tiled algorithm's advantage can come from avoiding traffic and storage, even if it recomputes some arithmetic.

Before applying this example to your own program, write down which inputs are
read, which result is produced, and the condition that makes the comparison
valid. Keep the original case as a regression check when changing a boundary.

## Six progressive exercises

Exercises 1 and 2 are guided reconstructions of the worked examples; exercises
3-6 change an input, diagnose a defect, test a boundary and transfer the idea.
For each one, keep the calculation, output, diagram or failure policy you
produce so another reader can compare it with the worked cases. If the hint is
not enough, reread the mechanism paragraph and the bounded CPU assertion.

### Exercise 1

Predict and trace the first worked example before running its CPU reference. Write every intermediate quantity that leads to the stated result, including units or ownership where applicable.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Reconstruct the second worked example without copying its conclusion. Identify the changed input or condition, show the resulting calculation or dependency, and explain why it differs from the first example.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Apply a causal mask that leaves only the first key in the worked row.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why must online accumulators rescale when the maximum increases?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What is the policy for a completely masked row?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design an attention benchmark contract.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **a short educational attention kernel is a production FlashAttention replacement or validates a complete Transformer.**

For the concrete failure exercise, why must online accumulators rescale when the maximum increases?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-054_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

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
