# cuda-050: Randomness and parallel Monte Carlo

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-006`, `cuda-020`, `cuda-039`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Work through *Randomness and parallel Monte Carlo* with the concrete cases below. Finish with this evidence:
reproducible setup metadata, uncertainty intervals and correct stream partitioning. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

Parallel random-number generation needs a reproducible mapping from logical samples to independent streams or subsequences. Giving every thread identical initial state can repeat the same draws and destroy effective sample size. A seed identifies an experiment, but the generator, stream partition and sample-count mapping are also part of it. Monte Carlo error is sampling uncertainty, distinct from floating-point error or a bug. Increasing independent sample count usually reduces standard error at a square-root rate. RNG initialization can be expensive, so report setup separately from sustained generation when evaluating performance.

## Mathematical contract

\[
\operatorname{SE}(\overline X)\approx\frac{s}{\sqrt n}
\]

This familiar sampling-error estimate assumes independent draws and suitable finite variance. Duplicated streams violate the independent-sample interpretation.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-050_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-050_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

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

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

Four workers initialized with exactly the same stream each draw \([0.1,0.7]\). Concatenating gives eight entries but only two distinct draws repeated four times. Treating them as eight independent observations understates uncertainty. A correct design gives workers nonoverlapping documented subsequences.

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

How does standard error change with four times as many independent samples?

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A GPU result differs from a CPU seed-matched result. Is it necessarily wrong?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What should zero samples return?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design a Monte Carlo receipt.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **giving every thread the same seed creates independent samples, or statistical disagreement alone proves a coding defect. .**

For the concrete failure exercise, a GPU result differs from a CPU seed-matched result. Is it necessarily wrong?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-050_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

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
