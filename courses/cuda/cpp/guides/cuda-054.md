# cuda-054: Attention and memory-aware algorithm design

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-046`, `cuda-051`, `cuda-052`, `cuda-053`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Explain attention and memory-aware algorithm design using the concrete cases below. Produce agreement with the reference and a memory/time report that states supported shapes and masks.
Distinguish an algorithmic calculation, a compiled artifact and an actual device
observation when explaining what your work establishes.

## Purpose, vocabulary and mental model

Scaled dot-product attention forms scores from queries and keys, normalizes each score row with softmax and combines values using those weights. Materializing the entire score matrix costs storage proportional to sequence length squared. Tiling can avoid retaining that large intermediate by maintaining an online maximum, normalization sum and weighted output accumulator. When a new tile raises the maximum, rescale earlier accumulators before combining them. Masking and training's backward needs add contracts. A tiny educational online algorithm demonstrates memory-aware mathematics; it is not a production replacement for specialized attention libraries.

## Mathematical contract

\[
\operatorname{Attention}(Q,K,V)=\operatorname{softmax}\left(\frac{QK^T}{\sqrt{d_k}}+M\right)V
\]

The mask M, softmax axis and scaling dimension d_k are part of the model contract. The first tiny example deliberately states that its scores are unscaled.

## How to run and study this lesson

Open this chapter in `/classroom` and use its saved reading worksheet. The primary
reading pad does not execute CUDA. The two examples, six tasks and separate
explanations are usable offline on macOS, Linux and Windows through WSL 2 with
the ordinary classroom. An AMD, Intel or Apple GPU does not make this CUDA C++
source executable through Docker.

For the bounded CPU calculation, select **CPU model (Python)** in this lesson.
That variant keeps its own source and result history under the same chapter. Its
answer-free starter supplies literal fixtures and the task contract; implement
the model and assertions before replacing its deliberate incomplete-work error.
The separate [CPU reference](../references/cuda-054_cpu.py) uses only Python's
standard library. For an optional terminal workflow, run this from the repository
root in a prepared Python environment:

```sh
python courses/cuda/cpp/references/cuda-054_cpu.py
```

The assertions check the stated numerical result or model invariant. Console text
is evidence of this CPU reference only. The [CUDA C++ study workflow](../README.md)
explains optional GPU compilation, paths, hardware requirements and evidence labels.
No lesson opening downloads a model, installs a driver or starts a GPU job.

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

Tiny floating-point display differences across platforms are acceptable only
where the explicit assertions use a tolerance; integers, shapes and ordering
must still satisfy their exact contracts. A printed hypothetical duration is a
model output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

For 4,096 tokens, a full score matrix has 16,777,216 elements per head and batch item. At four bytes each that is 64 MiB for scores alone. A tiled algorithm's advantage can come from avoiding traffic and storage, even if it recomputes some arithmetic.

Before applying this example to your own program, write down which inputs are
read, which result is produced, and the condition that makes the comparison
valid. Keep the original case as a regression check when changing a boundary.

## Six progressive exercises

### Exercise 1

Predict and trace the first worked example before running its CPU reference. Write every intermediate quantity that leads to the stated result, including units or ownership where applicable.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Start with the literal input and intermediate quantities in worked example 1.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 2

Reconstruct the second worked example without copying its conclusion. Identify the changed input or condition, show the resulting calculation or dependency, and explain why it differs from the first example.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Identify exactly which condition changes in worked example 2.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 3

Apply a causal mask that leaves only the first key in the worked row.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Use the first worked example to establish the relevant quantities, then change only the requested input.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 4

Why must online accumulators rescale when the maximum increases?

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Locate the failed phase or violated dependency before proposing a repair.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 5

What is the policy for a completely masked row?

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Check what the algorithm is allowed to read, write or assume at this boundary.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 6

Design an attention benchmark contract.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** State the output contract and which observations are needed in the new application.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **a short educational attention kernel is a production FlashAttention replacement or validates a complete Transformer.**

For the concrete failure exercise, why must online accumulators rescale when the maximum increases?
Preserve the original input and the stage where behavior diverged. Compare with
the CPU model or dependency diagram before changing hardware configuration.
A compiler result, synthetic timing model, profiler counter and returned numeric
answer support different claims. Record unavailable hardware honestly.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-054_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

These are further technical references. The chapter and local CPU model remain
readable offline. Check the documentation matching your deliberately prepared
toolkit before optional hardware execution.

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
