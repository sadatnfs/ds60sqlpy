# Day 32 — Statistical Inference

**Lesson ID:** `python-32` · **Level:** intermediate · **Dependencies:** `data` · **Network:** offline

Descriptive statistics summarize the sample you observed. Statistical inference
uses that sample, plus explicit assumptions, to quantify uncertainty about a
larger population.

## Learning objectives

By the end of the lesson, you can:

- state null and alternative hypotheses before running a test;
- apply one-sample and Welch two-sample t-tests with SciPy;
- construct and compare confidence intervals at several confidence levels;
- run a chi-square test of independence on a contingency table; and
- distinguish statistical significance, uncertainty, and practical importance.

## Prerequisites

- Complete `python-31` (probability basics).
- Be able to compute means, standard deviations, and proportions with NumPy.
- Understand that the data-generating process determines whether observations
  are independent.

## Vocabulary and mental models

| Term | Definition |
|---|---|
| Parameter | A fixed, usually unknown population quantity |
| Estimator | A rule that maps a sample to an estimate of a parameter |
| Standard error | Estimated sample-to-sample variability of an estimator |
| Confidence interval | A procedure whose intervals cover the true parameter at a stated long-run rate under its assumptions |
| Null hypothesis | A precise reference claim used to calculate a test statistic |
| p-value | Probability, assuming the null and model assumptions, of a result at least as incompatible with the null as the observed result |
| Effect size | Magnitude of a difference or association, expressed in meaningful or standardized units |
| Type I error | Rejecting a true null hypothesis |

A 95% confidence interval does not assign a 95% probability to a fixed parameter
after the interval has been computed. It describes the long-run coverage of the
interval-building procedure.

## Worked example: estimate and test answer different questions

```python
import numpy as np
from scipy import stats

rng = np.random.default_rng(0)
x = rng.normal(loc=0.2, scale=1.0, size=200)

estimate = x.mean()
standard_error = stats.sem(x)
t_stat, p_value = stats.ttest_1samp(x, popmean=0.0)
critical = stats.t.ppf(0.975, df=len(x) - 1)
ci_95 = (
    estimate - critical * standard_error,
    estimate + critical * standard_error,
)
```

The estimate and interval communicate location and uncertainty. The p-value
addresses compatibility with the specific null value `0.0`. Report all three
with the sample size and assumptions; a p-value alone hides the effect magnitude.

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

1. Open the Day 32 learner notebook from this guide's **Next
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

## Concept deep dive — sampling uncertainty, confidence intervals, and hypothesis-test evidence

### The mental model

Statistical inference reasons from a finite sample toward an unknown
population quantity. An estimator such as a sample mean varies across
hypothetical repeated samples; its **standard error** describes that
sampling variability. A confidence interval is a procedure with a
long-run coverage property, not a probability statement about a fixed
parameter after the data are observed.

A hypothesis test asks how incompatible an observed statistic is with
a precisely stated null model. The p-value is conditional on that null
model and its assumptions. It is not the probability that the null is
true, and it does not measure whether an effect is useful.

### Worked examples and syntax anatomy

- **`stats.ttest_1samp(sample, popmean)`:** compares a sample mean with a reference value using a t statistic and estimated standard error.
- **`stats.ttest_ind(a, b, equal_var=False)`:** runs Welch's two-sample test without assuming equal population variances.
- **`estimate ± critical_value * standard_error`:** forms an interval only after choosing a confidence level and an appropriate sampling model.

Read an API call from the inside out: identify the data entering the
operation, the state learned (if any), the value returned, and the
evidence that would make the result trustworthy. A method returning
without an exception proves only that the syntax and immediate runtime
path worked.

### Focused example A — see interval width respond to sample size

Before running the example, predict the shape, type, or direction of the
result. Write the prediction down so that a surprise becomes evidence
rather than something to overlook.

```python
import numpy as np
from scipy import stats

rng = np.random.default_rng(3201)

def mean_interval(sample, confidence=0.95):
    sample = np.asarray(sample, dtype=float)
    se = sample.std(ddof=1) / np.sqrt(sample.size)
    critical = stats.t.ppf((1 + confidence) / 2, df=sample.size - 1)
    return sample.mean() + np.array([-1, 1]) * critical * se

small = rng.normal(loc=2.0, scale=1.0, size=25)
large = rng.normal(loc=2.0, scale=1.0, size=400)
small_ci, large_ci = mean_interval(small), mean_interval(large)
print({"small": small_ci, "large": large_ci})
assert np.ptp(large_ci) < np.ptp(small_ci)
```

**Expected observation:** The larger sample normally produces a much narrower interval because its standard error is smaller.

**Assumption to name:** The observations are independent and the mean's t-based sampling model is reasonable.

### Focused example B — separate statistical detection from practical size

This second example changes one important condition. Compare it with
Example A instead of reading it as unrelated syntax.

```python
import numpy as np
from scipy import stats

rng = np.random.default_rng(3202)
sample = rng.normal(loc=0.02, scale=1.0, size=100_000)
result = stats.ttest_1samp(sample, popmean=0.0)
standardized_effect = sample.mean() / sample.std(ddof=1)
print({"p_value": result.pvalue, "standardized_effect": standardized_effect})
assert abs(standardized_effect) < 0.05
```

**Expected observation:** A very small effect can have a small p-value when the sample is large.

**Assumption to name:** The operational decision depends on effect size and uncertainty, not a significance threshold alone.

### From first attempt to independent use

| Stage | What to do | Evidence to keep |
|---|---|---|
| Recall | Define sampling uncertainty, confidence intervals, and hypothesis-test evidence in your own words and identify its input and output. | A definition that does not rely on the library name. |
| Predict | Predict the examples before execution, including shape and direction. | A written prediction and an explanation of any mismatch. |
| Implement | Recreate one example with a changed but valid input. | Code plus an assertion for the central invariant. |
| Debug | Trigger the named mistake or edge case intentionally. | The observed symptom and the smallest diagnostic that isolates it. |
| Transfer | Apply the idea to a different local dataset or decision. | A stated assumption, metric, and reason the method is suitable. |

### Common mistake and debugging path

**Mistake:** Reporting `p < 0.05` without the estimate, interval, assumptions, sample size, or practical decision threshold.

**Debug it deliberately:** Reconstruct the test statistic from estimate divided by standard error, inspect the data-generating grain, and calculate an effect size.

**Stop condition:** Do not make a population claim when independence, selection, multiplicity, or the measurement process is unexplained.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Learner exercises and progressive hints

1. Draw groups from `Normal(0, 1)` and `Normal(0.3, 1)`, then test the
   difference in means with Welch's t-test.

**Verify:** Practice 1 — sampling uncertainty, confidence intervals, and hypothesis-test evidence — record seed, both sample sizes, sample means/variances, Welch t statistic, degrees of freedom, and p-value; independently recompute the mean difference and state the exact null plus the decision at a declared alpha.

2. Build a contingency table from categorical data and run a chi-square test.
   For a fully offline run, construct a small table directly; a cached Seaborn
   dataset is optional.

**Verify:** Practice 2 — sampling uncertainty, confidence intervals, and hypothesis-test evidence — print the observed and expected contingency tables, chi-square statistic, degrees of freedom, and p-value; assert observed and expected totals match and flag any expected cell below 5.

3. Compute 90% and 99% confidence intervals for the same mean and compare their
   widths.

**Verify:** Practice 3 — sampling uncertainty, confidence intervals, and hypothesis-test evidence — from one unchanged sample, print its mean, standard error, and both interval endpoints; assert the 99% interval is wider than the 90% interval and both are centered on the same sample mean.

### Progressive hints

1. Use the same seeded generator, retain both sample sizes, and set
   `equal_var=False`. Interpret the estimated difference as well as the p-value.
2. Rows and columns represent category levels; cells contain counts, not raw
   labels. Inspect the expected counts returned by `chi2_contingency`.
3. Only the critical value changes when the sample and standard error remain
   fixed. Higher confidence should require a wider interval.

### Additional mastery practice

Separate effect estimation from decision thresholds. Report uncertainty, assumptions, and practical magnitude rather than treating a p-value as a verdict.

Predict or plan before you run code. Use the hint only after an honest
attempt, and record the evidence that would prove your result correct.

4. **Prediction:** Hold the true mean difference and variance fixed, then predict how increasing each group's sample size from 20 to 200 affects standard error, confidence-interval width, power, and effect size.
   **Progressive hint:** Standard error shrinks approximately with 1/sqrt(n); the underlying standardized effect does not grow merely because more rows were collected.

**Verify:** Prediction — with a seeded simulation at n=20 and n=200 per group, print standard error, interval width, power, and standardized effect; verify standard error/width shrink by about sqrt(10), power rises, and the population effect size remains fixed.

5. **Implementation:** Build a seeded percentile-bootstrap confidence interval for a median difference. Validate empty groups and expose the number of resamples as a parameter.
   **Progressive hint:** Resample each group independently with replacement, compute one median difference per resample, then take symmetric quantiles.

**Verify:** Implementation — with a declared seed and at least 5,000 resamples, print observed median difference and percentile endpoints; assert repeatability, resample count, and a ValueError for either empty group.

6. **Multiple-comparison reasoning:** You test 20 unrelated null hypotheses at alpha=0.05. Estimate the chance of at least one false positive, then compare Bonferroni and false-discovery-rate control for a planned analysis.
   **Progressive hint:** Under independent true nulls, use 1-(1-alpha)**20. Bonferroni controls family-wise error; Benjamini-Hochberg targets the expected false-discovery proportion among rejections.

**Verify:** Multiple-comparison reasoning — show family-wise false-positive probability 1 - 0.95^20 (about 0.6415), Bonferroni per-test alpha 0.0025, and a sorted Benjamini-Hochberg decision table with original hypothesis order restored.

Before opening the reference solution, explain the relevant assumption,
failure mode, and validation check for every answer.

## Self-check

- What assumptions make Welch's t-test more appropriate than the pooled test?
- Why does a tiny p-value not guarantee a useful or large effect?
- If a 99% interval is narrower than the 90% interval from the same data, what
  should you debug?
- What does a chi-square test say about association, and what does it not say
  about causation or direction?

Expected behavior: the 99% interval is widest, and the expected-count table has
the same shape and total count as the observed contingency table.

## Pitfalls, diagnostics, and tradeoffs

| Pitfall | Why it matters | Better practice |
|---|---|---|
| Choosing hypotheses after seeing results | Inflates false-positive risk | Write hypotheses and analysis rules first |
| Replacing a small p-value with “important” | Significance depends on sample size | Report effect size and confidence interval |
| Running many tests without adjustment | Increases family-wise false positives | Control the family or false-discovery rate |
| Using z critical values automatically | Can understate small-sample uncertainty | Use a t critical value when variance is estimated |
| Sparse expected cells in chi-square | Approximation may be unreliable | Combine defensible categories or use an exact method |
| Ignoring paired or repeated measures | Violates independence | Use a paired or hierarchical method appropriate to the design |

## Next step

- Work in the [Day 32 learner notebook](../notebooks/day32_statistical_inference.ipynb).
- Then consult the
  [Day 32 solution](../solutions/day32_statistical_inference/day32_solutions.md).
- Continue to [Day 33 — Linear Algebra](day33_linear_algebra_matrices.md).

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-32` — Day 32 — Statistical Inference.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize sampling uncertainty, confidence intervals, and hypothesis-test evidence. Use exactly these maintained learner materials:
- guide: `python/ds-60day/companion-guides/day32_statistical_inference.md`
- learner artifact: `python/ds-60day/notebooks/day32_statistical_inference.ipynb`

Treat me as a beginner except for these direct catalog prerequisites:
`python-31`. Do not assume knowledge beyond them or skip the
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
