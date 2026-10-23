# 8. Estimation and Statistical Inference

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-008`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

An estimate is a function of data. Its uncertainty comes from imagining a repeated data-generating or sampling process, not from the number of decimal places printed. A standard error summarizes the variation of the estimator; the standard deviation summarizes variation among observations. Confusing them can understate predictive uncertainty by orders of magnitude.

Choose the target first, then the estimation rule and uncertainty procedure. Likelihood, moment equations and resampling supply different routes. Their assumptions determine validity, especially at boundaries, with dependence, or after data-driven selection. A confidence interval for a population mean does not cover most future individuals.

## Methods, mechanisms, and limits

### stat-08-01

**Point estimation**

A point estimator maps a sample to one number or vector. Different estimators of the same target trade bias, variance and robustness. A single value should retain its population, scale and time-horizon meaning.

### stat-08-02

**Sampling distributions**

The sampling distribution is the distribution of an estimator under repeated samples. It is distinct from the empirical distribution of raw observations. Simulation can visualize it when the generating model is specified.

### stat-08-03

**Standard errors**

A standard error estimates the standard deviation of an estimator's sampling distribution. For independent observations, the mean's SE is sample SD divided by sqrt(n). Dependence changes that calculation.

### stat-08-04

**Bias**

Bias is E[estimate] minus the target under a specified model and sampling process. One observed estimate's error is not its bias. Regularization intentionally introduces bias that may reduce total error.

### stat-08-05

**Consistency**

Consistency requires convergence to the target as information grows. An estimator can be consistent yet biased in finite samples. Increasing rows does not repair systematic selection or a wrong target.

### stat-08-06

**Efficiency**

Efficiency compares variance among estimators under specified conditions or asymptotic regimes. An efficient normal-model estimator may be fragile under contamination; efficiency claims must name the model and competitor class.

### stat-08-07

**Mean squared error**

MSE equals variance plus squared bias for scalar estimation. The identity explains why shrinkage can outperform an unbiased estimator. It does not choose the loss function when operational harms are asymmetric.

### stat-08-08

**Maximum likelihood estimation**

MLE maximizes the likelihood as a function of parameters with observed data fixed. Likelihood is not a probability distribution over parameters. Boundaries, separation and multimodality can invalidate convenient asymptotic formulas.

### stat-08-09

**Maximum a posteriori estimation**

MAP maximizes likelihood times prior density. It resembles penalized fitting, but the mode changes under nonlinear reparameterization. A MAP point alone does not represent posterior uncertainty.

### stat-08-10

**Method of moments**

Match sample moments to theoretical expressions and solve for parameters. Easy computation can come at an efficiency cost or produce invalid parameter values when observed moments lie outside the model's feasible range.

### stat-08-11

**Generalized method of moments**

GMM solves weighted discrepancies between empirical moments and zero. Valid moment restrictions are its scientific foundation. Weighting affects efficiency, while invalid instruments or moments bias the estimator regardless of optimization success.

### stat-08-12

**Estimating equations**

Set a sample sum of scores or residual-based functions to zero. Unbiased estimating equations can identify parameters without specifying a full distribution. Multiple roots and weak derivatives can create unstable solutions.

### stat-08-13

**Sufficient statistics**

A sufficient statistic retains all likelihood information about a parameter under a specified family. For Bernoulli trials, the success count is sufficient for common p. It need not retain information about model misspecification.

### stat-08-14

**Fisher information**

Fisher information measures expected likelihood curvature or score variance under regularity. More curvature implies more local precision. Singular information signals nonidentifiability or boundary complications that normal approximations may miss.

### stat-08-15

**Cramér–Rao bounds**

Cramer-Rao bounds limit unbiased estimator variance under differentiability and regularity assumptions. They are not universal limits for biased estimators or irregular models. Attaining a bound is conditional on the assumed model.

### stat-08-16

**Asymptotic normality**

After suitable scaling, many regular estimators approach a Gaussian distribution. This is an approximation in finite samples. Rare events, boundaries, weak identification or heavy tails can make it poor.

### stat-08-17

**Delta method**

Linearize a smooth transformation g around an estimate and propagate covariance with its gradient. Ratios become unstable near a zero denominator; a first-order delta approximation may then be misleading.

### stat-08-18

**Confidence intervals**

A 95% confidence procedure covers a fixed parameter in 95% of hypothetical repetitions under its assumptions. The realized interval is not a 95% posterior probability statement without a Bayesian model.

### stat-08-19

**Prediction intervals**

A prediction interval includes irreducible outcome variability as well as estimation uncertainty. It is usually wider than a confidence interval for the conditional mean and must match the future observation's setting.

### stat-08-20

**Tolerance intervals**

A tolerance interval aims to contain a specified fraction of a population with a stated confidence. Its two percentages answer different questions. It is not merely a wide confidence interval for the mean.

### stat-08-21

**Profile likelihood**

For each candidate target parameter, maximize likelihood over nuisance parameters and compare the resulting profile. This can reveal asymmetry that a Hessian approximation misses, though reference cutoffs still need justification.

### stat-08-22

**Sandwich variance estimation**

Sandwich covariance combines score variability with sensitivity of estimating equations. It can protect standard errors against selected model deviations, but does not make a biased estimand or an invalid causal model correct.

### stat-08-23

**Cluster-robust standard errors**

Aggregate score contributions within independent clusters before estimating covariance. Many sufficiently informative clusters are important; thousands of records in four clusters do not provide large-cluster asymptotics.

### stat-08-24

**Heteroskedasticity-robust standard errors**

Heteroskedasticity-consistent covariance permits nonconstant conditional variance under suitable independence and design assumptions. It adjusts uncertainty, not the conditional mean specification or omitted-variable bias.

### stat-08-25

**Bootstrap**

Resample observations and recompute the complete statistic to approximate its sampling behavior. The resampling unit must match dependence. Ordinary bootstrap can fail for nonsmooth extremes or unidentified parameters.

### stat-08-26

**Jackknife**

Delete one observation or one independent group at a time and assess estimate changes. The jackknife works well for some smooth statistics but can behave poorly for statistics such as sample medians.

### stat-08-27

**Parametric bootstrap**

Simulate datasets from the fitted model and refit each. This captures model-implied uncertainty but inherits model misspecification. Including refitting is essential when the statistic depends on estimated parameters.

### stat-08-28

**Block bootstrap**

Resample contiguous blocks to retain local dependence. Block length trades dependence preservation against the number of independent blocks. Nonstationarity or long-range dependence requires additional design choices.

### stat-08-29

**Wild bootstrap**

Multiply residuals by random mean-zero weights while preserving the design. Wild bootstrap methods can address heteroskedastic regression settings; cluster variants require cluster-level multipliers and appropriate small-cluster care.

## Worked Python demonstrations

Complete offline program: [chapter_08.py](../examples/chapter_08.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_08.py
```

### Which uncertainty belongs to the question?

For five normal-model observations, both intervals use a t critical value with four degrees of freedom. Mean uncertainty divides SD by sqrt(n); a new individual's uncertainty multiplies SD by sqrt(1+1/n). The code verifies that prediction uncertainty exceeds uncertainty about the mean.

### Resampling and local propagation

The bootstrap repeatedly samples from the empirical distribution, whose variance uses divisor n, and its simulated SE is compared with that exact conditional target. The delta method uses the derivative of log(theta), 1/theta, so variance 0.25 at theta 4 yields log-scale SE 0.125.

### Complete executable example

```python
import numpy as np
from scipy import stats

def mean_and_prediction():
    x = np.array([8.,9.,10.,11.,12.])
    n, mean, sd = len(x), x.mean(), x.std(ddof=1)
    critical = stats.t.ppf(.975, n-1)
    mean_halfwidth = critical*sd/np.sqrt(n)
    prediction_halfwidth = critical*sd*np.sqrt(1+1/n)
    assert prediction_halfwidth > mean_halfwidth
    assert np.isclose(mean_halfwidth, 1.9632431615)
    print("Mean:", mean, "mean CI halfwidth:", mean_halfwidth, "prediction halfwidth:", prediction_halfwidth)

def bootstrap_and_delta():
    rng = np.random.default_rng(8)
    x = np.array([1.,2.,3.,4.,5.])
    means = rng.choice(x, size=(4000,len(x)), replace=True).mean(axis=1)
    expected_bootstrap_se = x.std(ddof=0)/np.sqrt(len(x))
    assert abs(means.std(ddof=1)-expected_bootstrap_se) < .04
    theta, variance = 4., .25
    log_se = np.sqrt(variance)/theta
    assert log_se == .125
    print("Bootstrap SE:", means.std(ddof=1), "delta log SE:", log_se)

def main():
    mean_and_prediction()
    bootstrap_and_delta()

if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: Why does a bootstrap not solve every uncertainty problem?** It approximates the process represented by the resampling scheme. If rows are clustered, selected or missing systematically, resampling them independently reproduces the wrong process. It also cannot invent information about an unidentified target.

**Interview: Can a biased estimator be preferable?** Yes, under a stated loss. If a small bias substantially reduces variance, mean squared error falls. The scientific question is whether the tradeoff improves the decision and whether any inferential intervals account for that bias.

## Primary sources and official APIs

- [SciPy bootstrap API](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html).

- [statsmodels robust regression covariance](https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.RegressionResults.get_robustcov_results.html).

## Reading connections

[Previous chapter](07-missing-data-measurement-error-and-robust-statistics.md) | [Book contents](../README.md) | [Next chapter](09-hypothesis-tests-and-group-comparisons.md)
