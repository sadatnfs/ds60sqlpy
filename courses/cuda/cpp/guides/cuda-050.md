# cuda-050: Randomness and parallel Monte Carlo

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-006`, `cuda-020`, `cuda-039`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Explain randomness and parallel Monte Carlo using the concrete cases below. Produce reproducible setup metadata, uncertainty intervals and correct stream partitioning.
Distinguish an algorithmic calculation, a compiled artifact and an actual device
observation when explaining what your work establishes.

## Purpose, vocabulary and mental model

Parallel random-number generation needs a reproducible mapping from logical samples to independent streams or subsequences. Giving every thread identical initial state can repeat the same draws and destroy effective sample size. A seed identifies an experiment, but the generator, stream partition and sample-count mapping are also part of it. Monte Carlo error is sampling uncertainty, distinct from floating-point error or a bug. Increasing independent sample count usually reduces standard error at a square-root rate. RNG initialization can be expensive, so report setup separately from sustained generation when evaluating performance.

## Mathematical contract

\[
\operatorname{SE}(\overline X)\approx\frac{s}{\sqrt n}
\]

This familiar sampling-error estimate assumes independent draws and suitable finite variance. Duplicated streams violate the independent-sample interpretation.

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
The separate [CPU reference](../references/cuda-050_cpu.py) uses only Python's
standard library. For an optional terminal workflow, run this from the repository
root in a prepared Python environment:

```sh
python courses/cuda/cpp/references/cuda-050_cpu.py
```

The assertions check the stated numerical result or model invariant. Console text
is evidence of this CPU reference only. The [CUDA C++ study workflow](../README.md)
explains optional GPU compilation, paths, hardware requirements and evidence labels.
No lesson opening downloads a model, installs a driver or starts a GPU job.

## Worked example 1: trace the mechanism

Estimate the integral of x squared on \([0,1]\) by averaging squared uniform samples. The exact answer is one third. A fixed CPU seed produces a reproducible educational estimate; its closeness is not evidence about cuRAND or independent GPU streams. Keep a broad deterministic sanity check separate from statistical claims.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
import random

rng = random.Random(7)
samples = [rng.random() ** 2 for _ in range(10000)]
estimate = sum(samples) / len(samples)
assert abs(estimate - 1 / 3) < 0.03
repeated = [0.1, 0.7] * 4
assert len(repeated) == 8 and len(set(repeated)) == 2
print(
    {
        "CPU_integral_estimate": estimate,
        "exact_integral": 1 / 3,
        "duplicated_stream_unique_draws": 2,
    }
)
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'CPU_integral_estimate': 0.3322235056104499, 'exact_integral': 0.3333333333333333, 'duplicated_stream_unique_draws': 2}
```

Tiny floating-point display differences across platforms are acceptable only
where the explicit assertions use a tolerance; integers, shapes and ordering
must still satisfy their exact contracts. A printed hypothetical duration is a
model output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

Four workers initialized with exactly the same stream each draw \([0.1,0.7]\). Concatenating gives eight entries but only two distinct draws repeated four times. Treating them as eight independent observations understates uncertainty. A correct design gives workers nonoverlapping documented subsequences.

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

How does standard error change with four times as many independent samples?

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Use the first worked example to establish the relevant quantities, then change only the requested input.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 4

A GPU result differs from a CPU seed-matched result. Is it necessarily wrong?

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Locate the failed phase or violated dependency before proposing a repair.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 5

What should zero samples return?

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Check what the algorithm is allowed to read, write or assume at this boundary.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 6

Design a Monte Carlo receipt.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** State the output contract and which observations are needed in the new application.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **giving every thread the same seed creates independent samples, or statistical disagreement alone proves a coding defect. .**

For the concrete failure exercise, a GPU result differs from a CPU seed-matched result. Is it necessarily wrong?
Preserve the original input and the stage where behavior diverged. Compare with
the CPU model or dependency diagram before changing hardware configuration.
A compiler result, synthetic timing model, profiler counter and returned numeric
answer support different claims. Record unavailable hardware honestly.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-050_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

These are further technical references. The chapter and local CPU model remain
readable offline. Check the documentation matching your deliberately prepared
toolkit before optional hardware execution.

- [cuRAND documentation](https://docs.nvidia.com/cuda/curand/index.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-050: Randomness and parallel Monte Carlo.
Read courses/cuda/cpp/guides/cuda-050.md and courses/cuda/cpp/lessons/cuda-050.md.
Direct prerequisites: `cuda-006`, `cuda-020`, `cuda-039`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-050_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-050_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
