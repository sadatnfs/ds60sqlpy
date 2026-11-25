# cuda-050: Randomness and parallel Monte Carlo

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-006`, `cuda-020`, `cuda-039`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Implement reproducible parallel Monte Carlo sampling with independent streams and report uncertainty intervals.

**Scope:** Seed, stream/subsequence, state, independence assumptions, parallel reproducibility, sampling error and numerical error.

**Evidence to produce:** Reproducible setup metadata, uncertainty intervals and correct stream partitioning.

## Purpose, vocabulary and mental model

Parallel random-number generation needs a reproducible mapping from logical samples to independent streams or subsequences. Giving every thread identical initial state can repeat the same draws and destroy effective sample size. A seed identifies an experiment, but the generator, stream partition and sample-count mapping are also part of it. Monte Carlo error is sampling uncertainty, distinct from floating-point error or a bug. Increasing independent sample count usually reduces standard error at a square-root rate. RNG initialization can be expensive, so report setup separately from sustained generation when evaluating performance.

### Key terms

- **Subsequence:** A cuRAND offset that gives each thread a non-overlapping portion of one generator sequence.
- **Monte Carlo estimate:** An average over random samples whose standard error typically shrinks in proportion to one over the square root of the sample count.
- **Standard error:** The estimated standard deviation of a sample mean, used to build an uncertainty interval.
- **Counter-based generator:** A generator such as Philox that computes any random value directly from a key and a counter.

## Mathematical contract

\[
\operatorname{SE}(\overline X)\approx\frac{s}{\sqrt n}
\]

This familiar sampling-error estimate assumes independent draws and suitable finite variance. Duplicated streams violate the independent-sample interpretation.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-050_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-050_cpu.py
```

## Worked example 1: trace the mechanism

Estimate the integral of x squared on \([0,1]\) by averaging squared uniform samples. The exact answer is one third. A fixed CPU seed produces a reproducible educational estimate; its closeness is not evidence about cuRAND or independent GPU streams. Keep a broad deterministic sanity check separate from statistical claims.

**Why:** The expectation of U squared is one third, and 10,000 samples land near it.

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

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'CPU_integral_estimate': 0.3322235056104499, 'exact_integral': 0.3333333333333333, 'duplicated_stream_unique_draws': 2}
```

**Check:** The reference asserts the estimate is within 0.03 of 1 / 3 and prints 0.3322 for seed 7.

## Worked example 2: change a meaningful condition

Four workers initialized with exactly the same stream each draw \([0.1,0.7]\). Concatenating gives eight entries but only two distinct draws repeated four times. Treating them as eight independent observations understates uncertainty. A correct design gives workers nonoverlapping documented subsequences.

**Why:** Four copies of [0.1, 0.7] hold two distinct values, so eight entries carry two observations of information.

**Check:** The reference asserts the repeated list has length 8 but only 2 distinct values.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Average squared uniform draws from a fixed CPU seed to estimate the integral of x squared on [0, 1].

**Trap to avoid:** Treating a close CPU estimate as validation of cuRAND confuses one generator's result with another's.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Give each worker a distinct subsequence or seed so draws do not repeat.

**Trap to avoid:** Counting eight samples in the standard error understates uncertainty by treating repeats as independent.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

How does standard error change with four times as many independent samples?

**Trap to avoid:** Dividing by four assumes error falls linearly with sample count.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A GPU result differs from a CPU seed-matched result. Is it necessarily wrong?

**Trap to avoid:** Demanding identical numbers to a seeded CPU run rejects a valid GPU generator.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What should zero samples return?

**Trap to avoid:** Returning 0 claims an estimate that no data supports.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design a Monte Carlo receipt.

**Trap to avoid:** Recording only the final number makes the run impossible to reproduce or assess.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Giving every thread the same seed creates independent samples, or statistical disagreement alone proves a coding defect.** Identical states give identical draws, so worked example 2 gets eight numbers but only two distinct values, and the true sample size is far smaller. Each worker needs its own stream or subsequence. Conversely, a GPU estimate that differs from a CPU estimate may only reflect sampling error, which shrinks with the square root of the sample count, so compare within standard errors before suspecting a bug.

## Self-check, retrieval and transfer

1. How much does standard error shrink with 100 times more independent samples?
2. What is the exact value targeted in worked example 1?
3. What should a Monte Carlo receipt record besides the seed?

Short answers are in the [separate explanations](../solutions/cuda-050_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

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
