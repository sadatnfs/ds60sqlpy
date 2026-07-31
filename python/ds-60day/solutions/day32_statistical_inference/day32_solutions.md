# Day 32 — Solutions: Statistical Inference (Estimation & Testing)

We perform common tests, compute confidence intervals, and interpret results carefully.

Contents
- Exercise 1: One-sample and two-sample t-tests with interpretation
- Exercise 2: Confidence intervals at 90%, 95%, 99% and width comparison
- Exercise 3: Chi-square test for independence on a contingency table

---

Setup
```python
import numpy as np
from scipy import stats
rng = np.random.default_rng(0)
```

Worked reference for Exercise 1 — One-sample and two-sample t-tests
```python
# One-sample: is the mean different from 0?
x = rng.normal(loc=0.2, scale=1.0, size=200)
t, p = stats.ttest_1samp(x, popmean=0.0)
print({'t': t, 'p': p})
# Interpret: if p<0.05, reject H0: mean==0 at 5% level

# Two-sample Welch t-test (unequal variances)
y = rng.normal(loc=0.0, scale=1.0, size=220)
t2, p2 = stats.ttest_ind(x, y, equal_var=False)
print({'t2': t2, 'p2': p2})
```
Line-by-line
- ttest_1samp compares sample mean to popmean
- Welch t-test is safer by default when variances differ

---

Worked reference for Exercise 2 — Confidence intervals at multiple levels
```python
mean = x.mean(); se = x.std(ddof=1)/np.sqrt(len(x))
ci90 = (mean - 1.645*se, mean + 1.645*se)
ci95 = (mean - 1.960*se, mean + 1.960*se)
ci99 = (mean - 2.576*se, mean + 2.576*se)
print({'mean': mean, 'ci90': ci90, 'ci95': ci95, 'ci99': ci99})
```
Notes
- Higher confidence → wider interval (trade-off between certainty and precision)
- For small n or unknown variance, use t critical values; with large n, z is close

---

Worked reference for Exercise 3 — Chi-square test for independence
```python
import numpy as np
from scipy import stats
# Example contingency table (rows: group A/B, cols: outcome Yes/No)
table = np.array([[30, 20], [15, 35]])
chi2, pval, dof, exp = stats.chi2_contingency(table)
print({'chi2': chi2, 'p': pval, 'dof': dof})
# Interpret p: small p suggests association between group and outcome
```
Pitfalls
- p-values quantify inconsistency with H0, not effect size; report effect sizes and CIs too
- Multiple tests inflate false positives; control FDR or adjust alpha

---

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Solution reasoning lens

A strong solution is not merely code that produces one plausible
output. It establishes a chain from input contract to operation to
verification:

1. **`stats.ttest_1samp(sample, popmean)`:** compares a sample mean with a reference value using a t statistic and estimated standard error.
2. **`stats.ttest_ind(a, b, equal_var=False)`:** runs Welch's two-sample test without assuming equal population variances.
3. **`estimate ± critical_value * standard_error`:** forms an interval only after choosing a confidence level and an appropriate sampling model.
4. **Verification:** Compare the result with an independent invariant, baseline, or failure case before interpreting it.

**Why this approach is appropriate:** Inference starts with the estimand and sampling design, then reports estimate, uncertainty, test evidence, and practical interpretation together.

**Useful alternative:** Bootstrap intervals can approximate uncertainty when their resampling scheme matches the data structure; they are not assumption-free.

**Trade-off:** Higher confidence increases interval coverage but widens the interval; more tests increase the chance of false discoveries.

**Edge case to test:** Constant data, tiny samples, missing values, or empty contingency cells can invalidate formulas or produce undefined statistics.

**Evidence of correctness:** Report the estimate, sample size, standard error or interval, exact hypothesis, assumptions, and a practical effect measure; independently recompute at least one statistic.

When comparing your attempt with the reference, explain which of these
decisions your code made explicitly. If the reference makes a different
choice, compare the contracts and evidence before deciding that one
version is universally better.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Exercise-by-exercise reasoning map

This map connects every learner prompt to a reasoning path. Read the
explanation before copying code: the goal is to understand the assumptions,
the evidence that validates the result, and the edge cases that can make an
apparently correct implementation fail.

### Exercise 1 — Original lesson practice

**Prompt:** Draw groups from `Normal(0, 1)` and `Normal(0.3, 1)`, then test the difference in means with Welch's t-test.

**How to reason about it:** Welch's t-test does not assume equal group variances, but it still assumes independent observations and reasonably stable means. Report sample sizes, the signed mean difference, a confidence interval, and the test result; significance alone does not describe importance.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 1 — sampling uncertainty, confidence intervals, and hypothesis-test evidence — record seed, both sample sizes, sample means/variances, Welch t statistic, degrees of freedom, and p-value; independently recompute the mean difference and state the exact null plus the decision at a declared alpha.

### Exercise 2 — Original lesson practice

**Prompt:** Build a contingency table from categorical data and run a chi-square test. For a fully offline run, construct a small table directly; a cached Seaborn dataset is optional.

**How to reason about it:** A chi-square test consumes counts, not raw category labels or percentages. Inspect expected cell counts and combine levels or choose an exact method when sparse cells make the asymptotic approximation weak.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 2 — sampling uncertainty, confidence intervals, and hypothesis-test evidence — print the observed and expected contingency tables, chi-square statistic, degrees of freedom, and p-value; assert observed and expected totals match and flag any expected cell below 5.

### Exercise 3 — Original lesson practice

**Prompt:** Compute 90% and 99% confidence intervals for the same mean and compare their widths.

**How to reason about it:** For the same data and method, a 99% interval is wider than a 90% interval because it must cover the parameter under more repeated samples. The center should stay the same; only the critical value changes.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 3 — sampling uncertainty, confidence intervals, and hypothesis-test evidence — from one unchanged sample, print its mean, standard error, and both interval endpoints; assert the 99% interval is wider than the 90% interval and both are centered on the same sample mean.

### Exercise 4 — Prediction

**Prompt:** Hold the true mean difference and variance fixed, then predict how increasing each group's sample size from 20 to 200 affects standard error, confidence-interval width, power, and effect size.

**Reasoning before implementation:** Standard error shrinks approximately with 1/sqrt(n); the underlying standardized effect does not grow merely because more rows were collected.

Larger samples generally narrow the interval and increase power because the
sampling distribution of the mean becomes tighter. The population difference
and standardized effect remain unchanged. A tiny effect can therefore become
statistically detectable without becoming practically important.

Simulate many datasets at both sizes with one seeded generator, but summarize
the distribution of rejection rates rather than selecting a convenient run.
Also verify that the observations are independent; duplicated customers would
inflate the apparent sample size.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Prediction — with a seeded simulation at n=20 and n=200 per group, print standard error, interval width, power, and standardized effect; verify standard error/width shrink by about sqrt(10), power rises, and the population effect size remains fixed.

### Exercise 5 — Implementation

**Prompt:** Build a seeded percentile-bootstrap confidence interval for a median difference. Validate empty groups and expose the number of resamples as a parameter.

**Reasoning before implementation:** Resample each group independently with replacement, compute one median difference per resample, then take symmetric quantiles.

The bootstrap approximates the estimator's sampling distribution without
assuming that the raw values are Normal.

```python
import numpy as np

def bootstrap_median_difference(
    left: np.ndarray,
    right: np.ndarray,
    *,
    confidence: float = 0.95,
    resamples: int = 5_000,
    seed: int = 32,
) -> tuple[float, float]:
    if left.size == 0 or right.size == 0:
        raise ValueError("both groups must contain observations")
    if not 0.0 < confidence < 1.0 or resamples < 100:
        raise ValueError("invalid confidence or too few resamples")
    rng = np.random.default_rng(seed)
    differences = np.empty(resamples)
    for index in range(resamples):
        a = rng.choice(left, size=left.size, replace=True)
        b = rng.choice(right, size=right.size, replace=True)
        differences[index] = np.median(a) - np.median(b)
    tail = (1.0 - confidence) / 2.0
    low, high = np.quantile(differences, [tail, 1.0 - tail])
    return float(low), float(high)
```

This percentile interval is a useful teaching baseline. Strong skew, tiny
samples, dependence, or clustered observations call for a more suitable
resampling design or a BCa/analytic interval.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Implementation — with a declared seed and at least 5,000 resamples, print observed median difference and percentile endpoints; assert repeatability, resample count, and a ValueError for either empty group.

### Exercise 6 — Multiple-comparison reasoning

**Prompt:** You test 20 unrelated null hypotheses at alpha=0.05. Estimate the chance of at least one false positive, then compare Bonferroni and false-discovery-rate control for a planned analysis.

**Reasoning before implementation:** Under independent true nulls, use 1-(1-alpha)**20. Bonferroni controls family-wise error; Benjamini-Hochberg targets the expected false-discovery proportion among rejections.

The chance of at least one false positive is about
`1 - 0.95**20`, or 64%, under the simplified independence assumption.
Bonferroni would compare each p-value with `0.05/20`; it is conservative and
fits a small set of confirmatory claims. Benjamini-Hochberg is often more
powerful for exploratory discovery, but answers a different error question.

Choose the hypothesis family and correction before inspecting results. Tests
that were added after seeing the data should be labeled exploratory rather
than quietly folded into the confirmatory analysis.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Multiple-comparison reasoning — show family-wise false-positive probability 1 - 0.95^20 (about 0.6415), Bonferroni per-test alpha 0.0025, and a sorted Benjamini-Hochberg decision table with original hypothesis order restored.
