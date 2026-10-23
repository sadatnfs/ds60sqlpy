# 3. Probability Fundamentals and Stochastic Processes

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-003`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

Probability connects possible outcomes to explicit assumptions. The most common practical mistake is mixing a marginal probability, such as the overall incident rate, with a conditional probability, such as the incident rate after an alert. A joint table makes the conditioning operation visible and prevents base-rate errors.

Independent observations are a special case. Time series, shared customers and common environments create dependence. Laws of averages and central-limit approximations need conditions on that dependence and on tail behavior. Stochastic processes describe the evolving joint distribution rather than only a histogram of isolated values.

## Methods, mechanisms, and limits

### stat-03-01

**Conditional probability**

Compute P(A given B)=P(A and B)/P(B) when P(B)>0. Restrict the population to B before interpreting the rate. Rare conditioning events create unstable empirical estimates even when the formula is simple.

### stat-03-02

**Bayes’ theorem**

Posterior odds equal prior odds times the likelihood ratio. A sensitive alert can still have low positive predictive value when the event is rare. Distinguish P(alert given event) from P(event given alert).

### stat-03-03

**Independence**

Independence factorizes a joint probability into marginal probabilities. Zero correlation only excludes linear association and does not imply independence in general. Independent data collection is an assumption to investigate, not a property of separate rows.

### stat-03-04

**Conditional independence**

Conditional independence means joint behavior factorizes within levels of specified information. Variables can be dependent overall and independent within groups, or become dependent after conditioning on a collider.

### stat-03-05

**Random variables**

A random variable assigns numerical values to uncertain outcomes. Its support constrains valid models: negative event counts or probabilities above one indicate a mismatch between the variable and modeling assumptions.

### stat-03-06

**Joint distributions**

A joint distribution assigns probabilities to combinations. Its row/column structure preserves dependence; multiplying marginals recreates it only under independence. Joint modeling is essential when downstream loss depends on simultaneous events.

### stat-03-07

**Marginal distributions**

Sum or integrate the joint distribution over unwanted variables. A marginal average mixes subgroup behavior using population weights, so it can change when composition changes even if every conditional relationship is stable.

### stat-03-08

**Conditional distributions**

Normalize the relevant joint slice to obtain a conditional distribution. Regression models often target its mean, but decision-making may require tails, quantiles or the entire conditional distribution.

### stat-03-09

**Expectation**

Expectation is a probability-weighted sum or integral. Linearity allows adding expectations without independence. The average need not be a possible observed value, as with a mean of 2.4 customers.

### stat-03-10

**Variance and covariance**

Variance is expected squared deviation from a mean; covariance averages paired deviations. Variance of a sum includes twice every pairwise covariance, so dependence can dominate aggregation risk.

### stat-03-11

**Correlation**

Pearson correlation divides covariance by both standard deviations. It is undefined for a constant variable and sensitive to outliers. A U-shaped deterministic relationship can have correlation near zero.

### stat-03-12

**Law of total expectation**

Average each subgroup's conditional expectation using subgroup probabilities. The resulting marginal mean changes if group proportions change. This identity underlies standardization and exposes accidental unweighted averaging of subgroup rates.

### stat-03-13

**Law of total variance**

Total variance equals average within-group variance plus variance of group means. Pooling observations can hide that most uncertainty comes from different environments rather than noise within an environment.

### stat-03-14

**Law of large numbers**

Under suitable assumptions, sample averages converge to an expectation. It does not promise monotonic improvement with each added observation or protect against biased sampling, infinite means or persistent dependence.

### stat-03-15

**Central limit theorem**

For independent identically distributed observations with finite variance, the standardized mean approaches a normal distribution. Heavy tails or dependence can slow or invalidate familiar approximations; the raw observations need not be normal.

### stat-03-16

**Concentration inequalities**

Bounds such as Markov, Chebyshev and Hoeffding control deviations using progressively stronger assumptions. Hoeffding uses independence and bounded observations. A conservative bound remains valuable when a detailed parametric distribution is unjustified.

### stat-03-17

**Jensen’s inequality**

For convex f, f(E[X]) is no larger than E[f(X)]. Consequently, transforming an average and averaging transformed values differ. Squared loss and exponential growth expose this difference directly.

### stat-03-18

**Exchangeability**

Exchangeability makes the joint law invariant under permutations. It is weaker than independence: shared latent effects can yield exchangeable dependence. Exchangeability supports some predictive constructions but must match the intended resampling or calibration argument.

### stat-03-19

**Markov chains**

A transition matrix gives next-state probabilities conditional on the current state. Multi-step transitions multiply the matrix. A stationary distribution need not describe finite-time behavior before mixing.

### stat-03-20

**Poisson processes**

A homogeneous Poisson process has independent increments and a constant event rate. Counts over time t have mean lambda*t and interarrival times are exponential. Bursty self-exciting incidents violate these assumptions.

### stat-03-21

**Renewal processes**

Independent identically distributed waiting times generate renewal events without requiring exponential waiting. The long-run rate depends on mean waiting time when it exists. Event-age information matters outside the memoryless case.

### stat-03-22

**Martingales**

A martingale's next value has conditional expectation equal to its current value. This formalizes fair cumulative evidence or gains. Optional-stopping conclusions require appropriate integrability and stopping conditions.

### stat-03-23

**Brownian motion**

Brownian motion has continuous paths and independent Gaussian increments with variance proportional to elapsed time. Its paths are not ordinary differentiable curves. Discrete Gaussian steps approximate some functionals but miss continuous boundary crossings.

### stat-03-24

**Ergodicity**

Ergodic behavior permits appropriate time averages to recover ensemble averages. A process trapped in disconnected regimes can have a stationary distribution yet fail to explore it from a single trajectory.

### stat-03-25

**Copulas**

A copula couples marginal distributions into a joint distribution. Matching ordinary correlation does not guarantee matching tail dependence. Joint extreme-risk decisions require checking the selected dependence family explicitly.

## Worked Python demonstrations

Complete offline program: [chapter_03.py](../examples/chapter_03.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_03.py
```

### Base rates and hidden mixture variation

The alert detects 90% of events but also fires for 5% of non-events. With 1% prevalence, only about 15.4% of alerts correspond to events. Separately, two subpopulations with variance one yield total variance four because their means differ. The between-group component cannot be learned from within-group standard deviations alone.

### Dynamics and nonlinear averages

The two-state transition matrix moves toward probabilities two-thirds and one-third. The code verifies invariance and a finite-step approximation separately. Squaring values 1 and 3 gives an average of 5, while squaring their average gives 4. That gap is the variance, an exact instance of Jensen's inequality.

### Complete executable example

```python
import numpy as np

def bayes_and_total_variance():
    prevalence, sensitivity, false_positive = .01, .9, .05
    positive = prevalence*sensitivity + (1-prevalence)*false_positive
    posterior = prevalence*sensitivity/positive
    assert .15 < posterior < .16
    weights, means, variances = np.array([.25, .75]), np.array([0., 4.]), np.array([1., 1.])
    mean = weights @ means
    variance = weights @ variances + weights @ (means-mean)**2
    assert mean == 3 and variance == 4
    print("P(event | alert):", round(posterior, 4), "mixture variance:", variance)

def markov_and_jensen():
    transition = np.array([[.8, .2], [.4, .6]])
    stationary = np.array([2/3, 1/3])
    assert np.allclose(stationary @ transition, stationary)
    distribution = np.array([1., 0.]) @ np.linalg.matrix_power(transition, 20)
    assert np.allclose(distribution, stationary, atol=1e-7)
    x = np.array([1., 3.])
    assert np.mean(x*x) > np.mean(x)**2
    print("Long-run state probabilities:", distribution, "variance gap:", np.mean(x*x)-np.mean(x)**2)

def main():
    bayes_and_total_variance()
    markov_and_jensen()

if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: Why is a 99% accurate classifier sometimes useless?** If events occur 1% of the time, predicting no event always achieves 99% accuracy. Examine false negatives, precision, calibration and action costs rather than accuracy in isolation.

**Interview: Does increasing a time series from 100 rows to 10,000 rows guarantee a 10-fold smaller standard error?** Only under the relevant independence or weak-dependence approximation. Closely spaced measurements can contribute little new information, and systematic drift can invalidate the target itself.

## Primary sources and official APIs

- [SciPy statistical distributions and functions](https://docs.scipy.org/doc/scipy/reference/stats.html).

- [NumPy random generator](https://numpy.org/doc/stable/reference/random/generator.html).

## Reading connections

[Previous chapter](02-mathematical-foundations.md) | [Book contents](../README.md) | [Next chapter](04-probability-distributions-you-should-recognize.md)
