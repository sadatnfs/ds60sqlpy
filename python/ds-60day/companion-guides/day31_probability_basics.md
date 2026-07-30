# Day 31 — Probability Basics

**Lesson ID:** `python-31` · **Level:** intermediate · **Dependencies:** `data` · **Network:** offline

Probability gives you a language for uncertainty. This lesson is a practical
refresh: simulate distributions, compare samples with theoretical behavior, and
reason about a diagnostic test without treating a probability as a certainty.

## Learning objectives

By the end of the lesson, you can:

- distinguish a Bernoulli trial, a Binomial count, and a continuous Normal draw;
- compute and interpret empirical mean and variance;
- demonstrate the law of large numbers with a seeded simulation;
- use conditional probabilities to reason through a small Bayes problem; and
- explain why simulation approximates a distribution rather than proving a result.

## Prerequisites

- Complete `python-30` (EDA and preprocessing project).
- Be comfortable with NumPy arrays, functions, and Matplotlib from `python-16`
  and `python-25`.
- Recall that a proportion must lie between 0 and 1.

## Vocabulary and mental models

| Term | Precise meaning | Useful mental model |
|---|---|---|
| Random variable | A numeric outcome determined by a random process | A rule that converts an outcome into a number |
| Bernoulli distribution | One trial with result 0 or 1 and success probability \(p\) | One possibly biased coin flip |
| Binomial distribution | Number of successes in \(n\) independent Bernoulli trials with constant \(p\) | “How many successes?” rather than “success or failure?” |
| Expected value | Probability-weighted long-run average | The center repeated samples approach |
| Variance | Expected squared distance from the mean | Spread in squared units |
| Conditional probability | Probability of \(A\) after learning \(B\), written \(P(A\mid B)\) | Restrict the population to cases where \(B\) happened |
| Law of large numbers | A sample average converges toward its expectation as sample size grows | More independent evidence stabilizes an estimate |

Independence is an assumption, not a default property of repeated data. If the
success probability changes between trials, a simple Binomial model is not the
right description.

## Worked example: convergence is noisy, not monotonic

```python
import numpy as np

rng = np.random.default_rng(42)
draws = rng.binomial(n=1, p=0.6, size=10_000)
running_mean = np.cumsum(draws) / np.arange(1, len(draws) + 1)

print(f"first 10 average: {running_mean[9]:.3f}")
print(f"final average:    {running_mean[-1]:.3f}")
```

The running average should finish near `0.6`, but it may move away from `0.6`
for short stretches. The law of large numbers describes eventual convergence;
it does not promise a smooth path or an exact answer in a finite sample.

For a Binomial variable, the theoretical mean is \(np\) and the variance is
\(np(1-p)\). Compare those values with a large simulated sample as a diagnostic,
not as a replacement for the formulas.

## Learner exercises and progressive hints

Complete these in the learner notebook:

1. Simulate `Binomial(n=10, p=0.3)` 10,000 times and plot a histogram.
2. Generate `Normal(0, 1)` values, compute their mean and variance, and overlay
   the probability density function. The standard-library formula is enough;
   SciPy is optional.
3. Given sensitivity `0.95`, specificity `0.90`, and prevalence `0.01`, compute
   \(P(\text{disease}\mid\text{positive})\).

### Progressive hints

1. A single Binomial draw is already a count from 0 through 10. Choose histogram
   bins that keep those integer outcomes visually separate.
2. Use `density=True` for a histogram that can be compared with a density curve.
   Check the empirical values against 0 and 1 before worrying about the plot.
3. Imagine 10,000 people. Separate true positives from false positives before
   dividing by everyone who tested positive.

### Additional mastery practice

Move between probability models, seeded simulation, and diagnostics. A simulation is useful only when its sample space and uncertainty are explicit.

Predict or plan before you run code. Use the hint only after an honest
attempt, and record the evidence that would prove your result correct.

4. **Prediction and uncertainty:** For an event with probability 0.002 observed in 1,000 independent trials, predict the chance of at least one occurrence, simulate it 20,000 times, and quantify Monte Carlo uncertainty.
   **Progressive hint:** Compute 1-(1-p)**n first. Treat each simulated experiment as one Bernoulli outcome and use sqrt(p_hat*(1-p_hat)/runs) for its standard error.
5. **Implementation:** Estimate P(A|B) from two Boolean arrays without using a probability library. Return both the estimate and the denominator so a caller can judge support.
   **Progressive hint:** Count rows where B is true, then count rows where A and B are both true. Decide explicitly what happens when B never occurs.
6. **Debugging and boundaries:** Design and test a Binomial-parameter validator. Include n=0, p=0, p=1, a negative n, a fractional n, and probabilities just outside the valid interval.
   **Progressive hint:** n is a nonnegative integer and p is a finite number in [0, 1]. Remember that bool is a subclass of int in Python.

Before opening the reference solution, explain the relevant assumption,
failure mode, and validation check for every answer.

## Self-check

- Why can a 95%-sensitive test still have a modest positive predictive value?
- What is the difference between `rng.binomial(1, p, size=m)` and
  `rng.binomial(n, p, size=m)`?
- If you change only the random seed, which conclusions should remain stable?
- Can a probability density exceed 1? Why does its total area, rather than its
  height at one point, matter?

Your work is behaving plausibly when the Binomial sample mean is near `3`, the
Normal sample mean is near `0`, and repeated larger samples vary less than small
ones. Do not require exact equality from random draws.

## Pitfalls, diagnostics, and tradeoffs

| Symptom | Likely cause | Diagnostic or response |
|---|---|---|
| Histogram appears shifted by half a bin | Default continuous bin edges | Supply integer-aligned edges |
| Empirical variance seems “wrong” | Small sample or confusion over `ddof` | Increase sample size and state whether you want population or sample variance |
| Bayes answer is close to sensitivity | Base-rate neglect | Include both true and false positives in the denominator |
| Results change dramatically each run | Unseeded or undersized simulation | Use `np.random.default_rng(42)` and report sample size |
| Simulation is treated as proof | Approximation confused with derivation | Compare against a theoretical expectation and state sampling error |

## Next step

- Work in the [Day 31 learner notebook](../notebooks/day31_probability_basics.ipynb).
- After attempting every exercise, compare reasoning with the
  [separate solution](../solutions/day31_probability_basics/day31_solutions.md).
- Continue to [Day 32 — Statistical Inference](day32_statistical_inference.md).
