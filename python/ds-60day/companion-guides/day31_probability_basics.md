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

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

1. Open the Day 31 learner notebook from this guide's **Next
   step** section in VS Code or JupyterLab.
2. Select the `Python (ds60sqlpy)` kernel. Start at the top and use
   **Run All** only after making the written predictions; every added
   worked example is bounded and offline after bootstrap.
3. Keep experiments in new scratch cells. Do not edit the official
   solution while attempting the numbered practice.
4. Restart the kernel and run from the first cell before calling the
   lesson complete. A clean run catches hidden state and stale
   variables.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m jupyter lab
```

macOS/Linux:

```bash
.venv/bin/python -m jupyter lab
```

If the Windows environment uses the documented conda-prefix fallback,
use `.\.venv\python.exe` in place of
`.\.venv\Scripts\python.exe`.

## Concept deep dive — probability models, conditional evidence, and simulation error

### The mental model

Probability separates a **model** from one observed dataset. A random
variable specifies which numeric outcome is recorded; a distribution
assigns probability to those outcomes; a sample is one finite set of
draws. The expected value is a property of the model, while a sample
mean is an estimate that changes across samples.

Conditional probability changes the denominator. `P(A | B)` asks what
fraction of the cases where `B` occurred also satisfy `A`. Bayes'
theorem reverses a condition by accounting for every route into the
observed evidence. Simulation is a useful numerical check, but its
accuracy depends on the number and independence of simulated runs.

### Worked examples and syntax anatomy

- **`rng = np.random.default_rng(seed)`:** creates an isolated reproducible random-number generator; the seed is an experiment input.
- **`rng.binomial(n, p, size)`:** returns `size` independent counts, each between zero and `n`, under constant success probability `p`.
- **`event.mean()`:** estimates a probability only when the Boolean or 0/1 array represents the event at the intended experimental grain.

Read an API call from the inside out: identify the data entering the
operation, the state learned (if any), the value returned, and the
evidence that would make the result trustworthy. A method returning
without an exception proves only that the syntax and immediate runtime
path worked.

### Focused example A — solve an at-least-one event by its complement

Before running the example, predict the shape, type, or direction of the
result. Write the prediction down so that a surprise becomes evidence
rather than something to overlook.

```python
import numpy as np

event_probability = 0.002
opportunities = 1_000
analytic = 1 - (1 - event_probability) ** opportunities

rng = np.random.default_rng(3101)
counts = rng.binomial(opportunities, event_probability, size=20_000)
simulated = np.mean(counts >= 1)
print({"analytic": analytic, "simulated": simulated})
assert abs(simulated - analytic) < 0.02
```

**Expected observation:** Both values are near 0.865; they are close rather than exactly equal.

**Assumption to name:** The 1,000 opportunities are independent and all use the same event probability.

### Focused example B — make the Bayes denominator visible with counts

This second example changes one important condition. Compare it with
Example A instead of reading it as unrelated syntax.

```python
population = 10_000
prevalence = 0.01
sensitivity = 0.95
specificity = 0.90

diseased = population * prevalence
healthy = population - diseased
true_positives = diseased * sensitivity
false_positives = healthy * (1 - specificity)
positive_predictive_value = true_positives / (true_positives + false_positives)
print({"true_positive": true_positives,
       "false_positive": false_positives,
       "P(disease|positive)": positive_predictive_value})
assert 0 < positive_predictive_value < sensitivity
```

**Expected observation:** False positives greatly outnumber true positives, so the posterior is about 8.8%, not 95%.

**Assumption to name:** Sensitivity and specificity apply to this population and the stated prevalence is credible.

### From first attempt to independent use

| Stage | What to do | Evidence to keep |
|---|---|---|
| Recall | Define probability models, conditional evidence, and simulation error in your own words and identify its input and output. | A definition that does not rely on the library name. |
| Predict | Predict the examples before execution, including shape and direction. | A written prediction and an explanation of any mismatch. |
| Implement | Recreate one example with a changed but valid input. | Code plus an assertion for the central invariant. |
| Debug | Trigger the named mistake or edge case intentionally. | The observed symptom and the smallest diagnostic that isolates it. |
| Transfer | Apply the idea to a different local dataset or decision. | A stated assumption, metric, and reason the method is suitable. |

### Common mistake and debugging path

**Mistake:** Using sensitivity as `P(disease | positive)` reverses the condition and ignores the base rate.

**Debug it deliberately:** Draw a two-by-two count table for a concrete population and verify that true and false positives both appear in the denominator.

**Stop condition:** Do not interpret a probability until the event, denominator, independence assumption, and simulation grain are explicit.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Learner exercises and progressive hints

Complete these in the learner notebook:

1. Simulate `Binomial(n=10, p=0.3)` 10,000 times and plot a histogram.

**Verify:** Practice 1 — probability models, conditional evidence, and simulation error — with seed 731, produce exactly 10,000 integer draws in [0, 10]; assert the sample mean is within 0.08 of 3.0, and save a labeled 11-bin histogram whose counts sum to 10,000.

2. Generate `Normal(0, 1)` values, compute their mean and variance, and overlay
   the probability density function. The standard-library formula is enough;
   SciPy is optional.

**Verify:** Practice 2 — probability models, conditional evidence, and simulation error — with a declared seed and 10,000 draws, print sample size, mean, and population variance; require |mean| < 0.05 and |variance - 1| < 0.08, and overlay the labeled standard-normal PDF on a density-scaled histogram.

3. Given sensitivity `0.95`, specificity `0.90`, and prevalence `0.01`, compute
   \(P(\text{disease}\mid\text{positive})\).

**Verify:** Practice 3 — probability models, conditional evidence, and simulation error — show the Bayes numerator 0.95 × 0.01, denominator 0.95 × 0.01 + 0.10 × 0.99, and posterior 0.0876 (about 8.76%); verify the false-positive term is included.

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

**Verify:** Prediction and uncertainty — show the analytic probability 1 - (1 - 0.002)^1000 (about 0.8648); with seed 731 and 20,000 experiments, report the simulated rate and Monte Carlo standard error and require the analytic value to fall within three standard errors.

5. **Implementation:** Estimate P(A|B) from two Boolean arrays without using a probability library. Return both the estimate and the denominator so a caller can judge support.
   **Progressive hint:** Count rows where B is true, then count rows where A and B are both true. Decide explicitly what happens when B never occurs.

**Verify:** Implementation — for A=[True, True, False, True] and B=[True, False, True, True], return estimate 2/3 and denominator 3; assert unequal lengths fail and a zero-true B denominator raises the documented exception.

6. **Debugging and boundaries:** Design and test a Binomial-parameter validator. Include n=0, p=0, p=1, a negative n, a fractional n, and probabilities just outside the valid interval.
   **Progressive hint:** n is a nonnegative integer and p is a finite number in [0, 1]. Remember that bool is a subclass of int in Python.

**Verify:** Debugging and boundaries — assert (n,p) values (0,0), (0,1), and (10,0.5) pass; negative/fractional n and p just below 0 or above 1 must raise named ValueErrors, while booleans are rejected as integer/probability inputs.

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

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-31` — Day 31 — Probability Basics.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize probability models, conditional evidence, and simulation error. Use exactly these maintained learner materials:
- guide: `python/ds-60day/companion-guides/day31_probability_basics.md`
- learner artifact: `python/ds-60day/notebooks/day31_probability_basics.ipynb`

Treat me as a beginner except for these direct catalog prerequisites:
`python-30`. Do not assume knowledge beyond them or skip the
guide's declared setup boundary. Do not open or quote anything under
`solutions/` unless I explicitly ask after an honest attempt. First
explain one concept in plain language and show a tiny example. Then ask
me to predict what happens before I run code.
Give me one bounded task at a time and wait for my code, output, error,
or written reasoning. If I am stuck, reveal only one rung of a
progressive hint ladder at a time.

Run or inspect my learner artifact when safe, distinguish observed
evidence from inference, and help me diagnose tracebacks instead of
replacing my work. Finish with two or three retrieval questions and
one transfer task.

Done when I can explain the core mechanism without notes, complete one
fresh attempt without copied solution code, produce the guide's stated
verification evidence from a clean run, answer the retrieval questions,
and explain how the transfer task changes the assumptions. A cell that
merely ran is not evidence of mastery.
```
