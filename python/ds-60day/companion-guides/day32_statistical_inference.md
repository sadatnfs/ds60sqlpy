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

## Learner exercises

1. Draw groups from `Normal(0, 1)` and `Normal(0.3, 1)`, then test the
   difference in means with Welch's t-test.
2. Build a contingency table from categorical data and run a chi-square test.
   For a fully offline run, construct a small table directly; a cached Seaborn
   dataset is optional.
3. Compute 90% and 99% confidence intervals for the same mean and compare their
   widths.

### Progressive hints

1. Use the same seeded generator, retain both sample sizes, and set
   `equal_var=False`. Interpret the estimated difference as well as the p-value.
2. Rows and columns represent category levels; cells contain counts, not raw
   labels. Inspect the expected counts returned by `chi2_contingency`.
3. Only the critical value changes when the sample and standard error remain
   fixed. Higher confidence should require a wider interval.

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
