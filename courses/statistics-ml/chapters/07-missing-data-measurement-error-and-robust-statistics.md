# 7. Missing Data, Measurement Error, and Robust Statistics

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-007`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

Missingness is a process, not a special numerical value. A failed sensor, a skipped survey item and an unreported high cost can generate identical blank cells but different inferential problems. Describe what was observed, why observation might depend on outcomes, and what additional assumptions make an analysis possible.

Robustness has a different target: limit damage from contamination or model departures. A robust estimator can resist a few extreme measurements while still being biased by systematic selection. Neither imputation nor outlier resistance substitutes for a credible measurement process.

## Methods, mechanisms, and limits

### stat-07-01

**Missing completely at random**

MCAR requires observation to be independent of all relevant values. Complete-case summaries can then preserve the target, with reduced precision. Observed balance is insufficient to prove independence from unobserved values.

### stat-07-02

**Missing at random**

MAR allows observation to depend on recorded covariates, provided missing values add no dependence after conditioning. Include those predictors in an imputation or weighting model; MAR is not the claim that missingness is random unconditionally.

### stat-07-03

**Missing not at random**

MNAR leaves dependence on unseen values after conditioning on observed data. Observed records generally cannot distinguish all such mechanisms. Use external information or explicitly vary unidentified sensitivity parameters.

### stat-07-04

**Complete-case analysis**

Discard incomplete records only when the resulting estimator's assumptions are justified. Validity depends on the target and model, not just the missing percentage. Listwise deletion can change the population being described.

### stat-07-05

**Single imputation**

Replacing a missing value once treats an uncertain quantity as known in ordinary downstream inference. Mean imputation also distorts variance and covariance. It may serve a predictive pipeline baseline when evaluated honestly.

### stat-07-06

**Multiple imputation**

Generate completed datasets from a model reflecting parameter and missing-value uncertainty, analyze each, then pool. Compatibility between imputation and analysis models matters, especially for interactions, nonlinear terms and hierarchical data.

### stat-07-07

**Chained-equations imputation**

MICE cycles through conditional models for incomplete variables. Flexible conditionals need not correspond to a coherent joint distribution. Inspect convergence, plausible values and the preservation of analysis-model relationships.

### stat-07-08

**Joint-model imputation**

Specify a joint distribution and draw missing entries conditionally. This ensures a coherent probability model but can impose restrictive distributional assumptions, such as joint normality for skewed or categorical variables.

### stat-07-09

**Predictive mean matching**

Match a missing case to observed donors with similar predicted values and sample a donor outcome. This preserves observed support, but cannot extrapolate beyond available donors and can struggle with sparse covariate regions.

### stat-07-10

**Inverse-probability weighting for missingness**

Weight observed outcomes by inverse estimated observation probabilities. Positivity and a credible missingness model are essential. Extreme weights signal limited information, not merely a numerical inconvenience to hide.

### stat-07-11

**Rubin’s rules**

Pool point estimates by averaging; total variance combines mean within-imputation variance and inflated between-imputation variance. The between component represents uncertainty about missing values, which single imputation omits.

### stat-07-12

**Pattern-mixture models**

Model outcome distributions within missingness patterns and connect unobserved portions using sensitivity assumptions. A delta shift for missing outcomes makes departures from MAR explicit rather than pretending they are identified.

### stat-07-13

**Selection models**

Factor the joint model into an outcome distribution and an observation-probability model. MNAR selection parameters are often weakly or nonidentified without restrictions, instruments or validation data.

### stat-07-14

**Missingness sensitivity analysis**

Vary assumptions about unseen outcomes and identify a tipping point for the decision. Report the range considered and why it is plausible; an arbitrary tiny perturbation is weak evidence of robustness.

### stat-07-15

**Measurement error models**

Distinguish classical additive error, systematic bias and differential error related to outcome or treatment. Repeated or validated measurements can identify error properties. Outcome noise and predictor noise affect regression differently.

### stat-07-16

**Errors-in-variables regression**

Noisy explanatory variables can attenuate a simple linear slope under classical independent error. Multivariable and differential-error settings need not attenuate toward zero. Without error information, the true relationship may be unidentified.

### stat-07-17

**Regression calibration**

Replace a noisy predictor with an estimate of its conditional true value using validation information. This can approximately correct certain models; nonlinear outcomes and large error require care about approximation quality.

### stat-07-18

**SIMEX**

Add known amounts of noise, refit repeatedly, then extrapolate the estimate toward negative added-noise variance. SIMEX depends on a credible error model and extrapolation function; extrapolation can amplify instability.

### stat-07-19

**Robust estimators**

Choose location, scale or regression estimators with limited outlier sensitivity. Robustness is relative to a contamination model. Discarding every unusual point can erase the rare failures the decision actually cares about.

### stat-07-20

**M-estimation**

Minimize a sum of losses rho(residual) or solve its score equation. The choice of score controls outlier influence. Robust estimating equations still require suitable dependence-aware uncertainty estimation.

### stat-07-21

**Huber loss**

Huber loss is quadratic for small residuals and linear beyond a threshold. Its bounded score limits large residual influence, but does not automatically protect against high-leverage predictor outliers.

### stat-07-22

**Trimmed and Winsorized estimators**

Trimming removes specified tails before averaging; Winsorization caps them at boundary values. Both change the estimand relative to the ordinary population mean and need an explicit tail fraction.

### stat-07-23

**Median absolute deviation**

MAD is the median absolute deviation from the median. Multiplying by about 1.4826 yields normal-consistent scale. It can be zero in highly discrete samples, so robust z-scores then need a fallback.

### stat-07-24

**Influence functions**

The influence function describes first-order sensitivity to a tiny contaminating mass at a point. Bounded influence controls local contamination effects; it is not the same as resisting a large malicious fraction.

### stat-07-25

**Breakdown point**

The breakdown point measures the contamination fraction needed to make an estimator arbitrarily bad. A median can approach 50% breakdown for location, while the mean can break with one unbounded observation.

## Worked Python demonstrations

Complete offline program: [chapter_07.py](../examples/chapter_07.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_07.py
```

### An extreme value and a bounded score

One added value of 1,000 raises the mean above 100 while the median stays 10. Trimming one observation from each tail gives 10.25. These are different summaries, not interchangeable repairs. The clipped Huber score shows exactly how a residual of 100 contributes no more score than 1.5 beyond the chosen cutoff.

### Missing values add uncertainty

Three imputation-specific estimates average to 2.5. Their disagreement adds one-third to variance beyond the within-imputation variance 0.04. The sensitivity calculation then shifts the missing 30% of outcomes by minus two, zero or plus two, yielding means 1.4, 2 and 2.6. Those scenarios are assumptions, not estimates of unseen data.

### Complete executable example

```python
import numpy as np
from scipy import stats

def robust_location():
    clean = np.array([9.,10.,10.,11.,10.])
    contaminated = np.append(clean, 1000.)
    median = np.median(contaminated)
    trimmed = stats.trim_mean(contaminated, proportiontocut=1/6)
    assert median == 10 and trimmed == 10.25
    assert contaminated.mean() > 100
    residual = np.array([0., 1., 100.])
    huber_score = np.clip(residual, -1.5, 1.5)
    assert huber_score[-1] == 1.5
    print("Mean/median/trimmed:", contaminated.mean(), median, trimmed, "Huber scores:", huber_score)

def imputation_uncertainty():
    estimates = np.array([2., 2.5, 3.])
    within_variance = np.array([.04, .04, .04])
    m = len(estimates)
    between = estimates.var(ddof=1)
    total = within_variance.mean() + (1+1/m)*between
    assert np.isclose(total, .04+1/3) and total > within_variance.mean()
    observed_mean, missing_fraction = 2., .3
    deltas = np.array([-2., 0., 2.])
    sensitivity = observed_mean + missing_fraction*deltas
    assert np.allclose(sensitivity, [1.4,2.,2.6])
    print("Pooled estimate/SE:", estimates.mean(), np.sqrt(total), "MNAR scenarios:", sensitivity)

def main():
    robust_location()
    imputation_uncertainty()

if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: Can a missingness test prove MAR?** No. MAR concerns dependence on values that are missing. Observed patterns can challenge simple models, but different MAR and MNAR mechanisms can generate the same observed-data distribution.

**Interview: Why is mean imputation dangerous for inferential uncertainty?** It adds repeated central values and ignores the uncertainty of their replacement. This usually compresses variance and distorts relationships. Multiple imputation propagates uncertainty if the imputation and analysis assumptions are adequate.

## Primary sources and official APIs

- [statsmodels multiple imputation documentation](https://www.statsmodels.org/stable/imputation.html).

- [SciPy trimmed-mean API](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.trim_mean.html).

## Reading connections

[Previous chapter](06-measurement-exploratory-analysis-and-data-quality.md) | [Book contents](../README.md) | [Next chapter](08-estimation-and-statistical-inference.md)
