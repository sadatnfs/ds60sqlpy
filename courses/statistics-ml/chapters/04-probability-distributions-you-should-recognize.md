# 4. Probability Distributions You Should Recognize

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-004`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

A distribution is a claim about support, shape and how observations arise. Start with the outcome type and mechanism: one binary trial, repeated trials, event counts, waiting times, bounded proportions or extreme events. Then ask whether heterogeneity, dependence, truncation or excess zeros invalidate the simplest family.

Parameters are not interchangeable across libraries. For example, a gamma distribution can be specified with shape and rate, while SciPy's scale is the inverse rate. A distribution's fitted mean may look plausible while its tails badly misrepresent operational risk. Use simulations and probability calculations to inspect consequences before trusting a name.

## Methods, mechanisms, and limits

### stat-04-01

**Bernoulli distribution**

A Bernoulli variable has support zero and one, mean p and variance p(1-p). It models a single trial. Repeated events for one customer usually need a dependence model beyond separate Bernoulli assumptions.

### stat-04-02

**Binomial distribution**

The sum of n independent Bernoulli trials with common p has mean np and variance np(1-p). Varying probabilities or correlated trials produce different count distributions and can make binomial intervals too narrow.

### stat-04-03

**Beta-binomial distribution**

Mix binomial probabilities over a beta distribution to represent group heterogeneity. The extra uncertainty induces positive dependence within a group and overdispersion. It should not replace investigation of omitted systematic group predictors.

### stat-04-04

**Categorical distribution**

A categorical draw selects one of K outcomes with probabilities summing to one. Numerical category codes have no implied distance. The last probability is constrained by the others, which matters for parameter counts.

### stat-04-05

**Multinomial distribution**

Counts of K categories across n independent categorical draws sum to n. That constraint creates negative covariance between categories. Modeling each count independently can assign impossible totals and incorrect uncertainty.

### stat-04-06

**Poisson distribution**

A Poisson count has mean and variance lambda. It suits independent events with a stable exposure-adjusted rate. Different exposure durations require offsets or rate normalization; overdispersion calls for further modeling.

### stat-04-07

**Negative binomial distribution**

A negative binomial permits variance above the mean, often through gamma mixing of a Poisson rate. Parameterizations differ. Overdispersion may reflect heterogeneity, but this model alone does not identify its scientific cause.

### stat-04-08

**Geometric distribution**

Geometric waiting counts arise from independent trials with constant success probability. Some conventions count failures before success and others include the successful trial. State the convention before comparing means or API outputs.

### stat-04-09

**Hypergeometric distribution**

Sampling without replacement from a finite population produces a hypergeometric count. Its variance is smaller than the corresponding with-replacement binomial variance because sampled successes deplete the remaining population.

### stat-04-10

**Normal distribution**

A normal distribution has symmetric bell-shaped density with mean mu and variance sigma-squared. It is often an approximation for averages. Unbounded support makes it unsuitable for some raw positive or bounded measurements.

### stat-04-11

**Multivariate normal distribution**

A mean vector and covariance matrix determine a joint Gaussian law. Linear combinations remain Gaussian. Zero covariance then implies independence, a special property that does not extend to arbitrary multivariate distributions.

### stat-04-12

**Student’s t distribution**

The t distribution has heavier tails controlled by degrees of freedom. It describes a normal mean standardized using an independently estimated variance. Very low degrees of freedom can make means or variances undefined.

### stat-04-13

**Chi-square distribution**

Adding squared independent standard normal variables gives chi-square degrees of freedom equal to the number of terms. It appears in variance inference and likelihood approximations; the asymptotic use needs regularity conditions.

### stat-04-14

**F distribution**

An F variable is a ratio of independent chi-square variables divided by their degrees of freedom. ANOVA uses this structure under its error assumptions. Unequal variances can undermine the classical calibration.

### stat-04-15

**Uniform distribution**

Uniform density is constant over a chosen interval, but uniformity depends on parameterization. A prior uniform on a scale is not uniform on its logarithm. Explicit bounds determine its consequences.

### stat-04-16

**Exponential distribution**

Exponential waiting time has constant hazard and the memoryless property. Its mean is scale=1/rate. Aging hardware or customer learning violates constant hazard even if average waiting time matches.

### stat-04-17

**Gamma distribution**

Gamma distributions model positive skew and sum independent exponential waits with common rate. Shape controls dispersion and behavior near zero. Check the rate-versus-scale convention in every calculation.

### stat-04-18

**Beta distribution**

A beta distribution lives between zero and one, with mean alpha/(alpha+beta). It can represent uncertainty about a probability. Observed values exactly zero or one need special treatment in continuous beta regression.

### stat-04-19

**Dirichlet distribution**

The Dirichlet places probability mass on vectors of nonnegative proportions summing to one. It is conjugate to multinomial counts. Its standard dependence structure may be too restrictive for complex compositional data.

### stat-04-20

**Lognormal distribution**

Exponentiating a normal variable creates a lognormal variable with mean exp(mu+sigma-squared/2), not exp(mu). Multiplicative mechanisms motivate it. Large log-scale variance produces a long right tail and unstable arithmetic averages.

### stat-04-21

**Weibull distribution**

A Weibull shape below one gives decreasing hazard, above one increasing hazard, and one the exponential case. This flexibility helps lifetime modeling; extrapolating beyond observed follow-up remains assumption-sensitive.

### stat-04-22

**Pareto distribution**

Pareto tails decay as a power law. Depending on the tail index, the mean or variance may not exist. Log-log plots alone are weak evidence of a power law because several alternatives mimic short ranges.

### stat-04-23

**Generalized extreme value distribution**

The GEV family describes limiting normalized block maxima under suitable tail and dependence conditions. Block size trades approximation quality against sample count. SciPy's shape convention requires particular care when comparing literature formulas.

### stat-04-24

**Generalized Pareto distribution**

The generalized Pareto approximates exceedances over a sufficiently high threshold. Raising the threshold improves tail approximation but reduces data. Threshold stability and dependence diagnostics are essential for return-level claims.

### stat-04-25

**Mixture distributions**

A mixture averages component distributions with nonnegative weights summing to one. A mixture of normal groups need not be normal. Component labels are interchangeable, and inferred components need not be real populations.

### stat-04-26

**Truncated distributions**

Truncation conditions on inclusion within a range and renormalizes the density. Ignoring unobserved values outside the range biases inference. Censoring instead retains a record with partial knowledge and has a different likelihood.

### stat-04-27

**Zero-inflated distributions**

A zero-inflated model gives probability pi to structural zeros plus 1-pi to a count distribution that can itself generate zeros. A hurdle model excludes zeros from its positive component. Excess zeros alone do not prove a structural-zero mechanism.

## Worked Python demonstrations

Complete offline program: [chapter_04.py](../examples/chapter_04.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_04.py
```

### Same mean, different uncertainty

Binomial and beta-binomial counts both have mean two in this fixture, but the beta-binomial variance is larger. Heterogeneous success probabilities change uncertainty even when the average matches. The tail assertion also verifies that a t distribution with three degrees of freedom assigns more mass beyond three than a standard normal.

### Transformation and observation mechanisms

A lognormal with log mean zero has median one but mean about 1.6487. The truncated-normal calculation explicitly divides by the probability of inclusion. The exponential survival ratio verifies memorylessness: already waiting three units does not change the next two units' survival probability under that particular model.

### Complete executable example

```python
import numpy as np
from scipy import stats

def counts_and_tails():
    n, p = 10, .2
    assert np.isclose(stats.binom.mean(n, p), 2)
    poisson_var = stats.poisson.var(2)
    beta_binomial_var = stats.betabinom.var(n, 2, 8)
    assert beta_binomial_var > stats.binom.var(n, p)
    print("Binomial variance:", stats.binom.var(n,p), "beta-binomial variance:", beta_binomial_var)
    assert poisson_var == 2
    assert stats.t.sf(3, df=3) > stats.norm.sf(3)

def positive_and_truncated():
    mu, sigma = 0., 1.
    arithmetic = stats.lognorm.mean(s=sigma, scale=np.exp(mu))
    median = stats.lognorm.median(s=sigma, scale=np.exp(mu))
    assert arithmetic > median == 1
    conditional = (stats.norm.cdf(1)-stats.norm.cdf(0))/(1-stats.norm.cdf(0))
    assert np.isclose(conditional, stats.truncnorm.cdf(1, 0, np.inf))
    assert np.isclose(stats.expon.sf(5, scale=2)/stats.expon.sf(3, scale=2), stats.expon.sf(2, scale=2))
    print("Lognormal mean/median:", round(arithmetic,4), median, "P(Z<=1 | Z>0):", round(conditional,4))

def main():
    counts_and_tails()
    positive_and_truncated()

if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: A count outcome has variance much larger than its mean. What do you do?** First inspect exposure, repeated units and omitted groups. A negative binomial or quasi-likelihood model can represent extra variance, but neither repairs a wrong time denominator or dependent observation design automatically.

**Interview: Is zero-inflated Poisson always better for many zeros?** No. A low-rate Poisson naturally contains many zeros, and unmodeled heterogeneity can also generate them. Compare predictive checks and plausible mechanisms before introducing a separate latent structural-zero state.

## Primary sources and official APIs

- [SciPy continuous and discrete distribution reference](https://docs.scipy.org/doc/scipy/reference/stats.html).

- [NIST distribution gallery](https://www.itl.nist.gov/div898/handbook/eda/section3/eda366.htm).

## Reading connections

[Previous chapter](03-probability-fundamentals-and-stochastic-processes.md) | [Book contents](../README.md) | [Next chapter](05-sampling-surveys-and-data-collection.md)
