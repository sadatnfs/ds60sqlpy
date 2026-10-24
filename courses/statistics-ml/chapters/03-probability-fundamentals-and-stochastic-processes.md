# 3. Probability Fundamentals and Stochastic Processes

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-003`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

Probability connects possible outcomes to explicit assumptions. The most common practical mistake is mixing a marginal probability, such as the overall incident rate, with a conditional probability, such as the incident rate after an alert. A joint table makes the conditioning operation visible and prevents base-rate errors.

Independent observations are a special case. Time series, shared customers and common environments create dependence. Laws of averages and central-limit approximations need conditions on that dependence and on tail behavior. Stochastic processes describe the evolving joint distribution rather than only a histogram of isolated values.

## Methods, mechanisms, and limits

### stat-03-01

**Conditional probability**

Compute \(\Pr(A\mid B)=\frac{\Pr(A\cap B)}{\Pr(B)}\) when \(\Pr(B)>0\). Restrict the population to B before interpreting the rate. Rare conditioning events create unstable empirical estimates even when the formula is simple.

### stat-03-02

**Bayes’ theorem**

Posterior odds equal prior odds times the likelihood ratio. A sensitive alert can still have low positive predictive value when the event is rare. Distinguish \(\Pr(\mathrm{alert}\mid\mathrm{event})\) from \(\Pr(\mathrm{event}\mid\mathrm{alert})\).

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

A homogeneous Poisson process has independent increments and a constant event rate. Counts over time t have mean \(\lambda\cdot t\) and interarrival times are exponential. Bursty self-exciting incidents violate these assumptions.

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

<!-- detailed-case-studies:start -->

## Extended case studies and scientific reasoning

### Case study: calculate a diagnostic alert with a population table

Imagine 10,000 cases with event prevalence 1%. There are 100 events and 9,900 nonevents. A detector with sensitivity .9 flags 90 events. At false-positive rate .05 it also flags 495 nonevents. Among 585 total alerts, 90 are real events, giving positive predictive value \(\frac{90}{585}\), about .154.

The calculation is Bayes' rule written as counts. It makes clear why \(\Pr(\mathrm{alert}\mid\mathrm{event})\) and \(\Pr(\mathrm{event}\mid\mathrm{alert})\) differ: their denominators refer to different populations. Improving sensitivity without reducing false-positive rate may leave precision disappointing when events are rare. Changing the deployment prevalence changes alert meaning even if the detector's class-conditional behavior remains fixed.

Conditional probability also clarifies selection. Restricting a table to logged or reviewed cases changes the denominator and potentially the distribution. If review is triggered by both severity and model confidence, performance estimated only among reviewed cases may not describe all cases. The observation mechanism belongs in the probability model.

### Case study: derive total variance from a decomposition

Write X-E[X] as \([X-\mathbb{E}[X\mid G]]+[\mathbb{E}[X\mid G]-\mathbb{E}[X]]\). Squaring and taking expectations yields two squared terms and a cross term. The cross term vanishes because \(\mathbb{E}[X-\mathbb{E}[X\mid G]\mid G]=0\). The remaining terms are \(\mathbb{E}[\operatorname{Var}(X\mid G)]+\operatorname{Var}(\mathbb{E}[X\mid G])\). This derivation shows exactly why between-group mean differences add variability even when every group's internal noise is small.

Suppose two equally frequent environments have means zero and ten and each has variance one. The overall mean is five. Within-environment variance contributes one, while variance of environment means contributes 25, giving total variance 26. A model using the environment label can explain much of that variability. A model omitting it may interpret the same pattern as irreducible noise.

The identity applies to predictive uncertainty as well. Averaging conditional variances alone omits uncertainty in which condition will occur. Simulation must draw the group or shared latent state before drawing within-group noise when the downstream decision depends on total variability or simultaneous outcomes.

### Case study: what the central limit theorem actually says

Let X_i be independent identically distributed observations with mean mu and finite variance sigma-squared. The central limit theorem states that \(\frac{\sqrt{n}(\bar{X}-\mu)}{\sigma}\) converges in distribution to a standard normal. It does not say the raw observations become normal, and it does not say every sample mean is accurate. The standardization changes with n because the mean's variance is sigma-squared/n.

For exponential observations with mean and variance one, the raw distribution is right-skewed. Means of 32 such observations are less skewed, and their standardized fluctuations approximate a normal distribution. A simulation can compare means, variances and quantiles across repeated samples. The approximation improves in a model-dependent way; there is no universal sample size at which n is large enough for every tail probability.

A Cauchy distribution supplies a useful warning. Its mean and variance do not exist, and the average of independent identically distributed standard Cauchy variables remains standard Cauchy. Taking more observations does not concentrate that average around a finite population mean. The usual law-of-large-numbers and CLT arguments are inapplicable, even though software can always print a finite average for a finite sample.

Dependence creates another limitation. If every recorded value repeats the same random draw, a thousand rows contain only one random piece of information. Weak-dependence central limit theorems can apply to some time series, but their variance includes autocovariances. Count independent information rather than assuming every new row reduces SE by the familiar square-root factor.

### Case study: concentration bounds trade precision for assumptions

For a nonnegative variable, Markov's inequality bounds \(\Pr(X\ge a)\) by \(\frac{\mathbb{E}[X]}{a}\). Applying it to squared deviations gives Chebyshev's inequality, \(\Pr(|X-\mu|\ge t)\le\frac{\sigma^2}{t^2}\). These bounds use little distributional information and can be conservative.

For independent variables bounded between zero and one, Hoeffding bounds the sample-mean tail by \(2\exp(-2n\epsilon^2)\). To make that bound at most alpha, choose \(\epsilon=\sqrt{\frac{\log(2/\alpha)}{2n}}\). This bound supports explicit finite-sample guarantees for bounded observations, but it does not apply unchanged to unbounded durations or correlated repeated events.

A bound that is numerically loose can still be valuable when a distributional approximation is unreliable. Conversely, a tighter normal approximation may be practically useful when its assumptions are well supported. State whether an interval is an exact finite-sample result, an asymptotic approximation or a simulation-based assessment.

### Case study: stationarity, mixing and long-run averages

A Markov chain's transition matrix describes one-step conditional behavior. A stationary distribution satisfies \(\pi P=\pi\), but starting the chain in another distribution creates a transient period. Irreducibility and aperiodicity in a finite-state chain support convergence to the stationary law; reducible or periodic chains can fail to mix in the expected way.

Ergodicity concerns whether time averages along one sufficiently long trajectory represent the relevant distributional averages. A process can have a stationary distribution while remaining trapped in one component. This matters for MCMC, service-state models and simulation: a long log file is not necessarily representative of all operating regimes.

Poisson arrivals assume independent increments and a constant rate in the homogeneous case. Real incidents may cluster after a common failure or trigger further failures. Renewal models relax exponential waiting times, while self-exciting or regime models address other mechanisms. A histogram of counts cannot by itself validate the independence and timing assumptions needed for queueing or reliability decisions.

<!-- detailed-case-studies:end -->

## Worked Python demonstrations

Complete offline program: [chapter_03.py](../examples/chapter_03.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_03.py
```

### Base rates and hidden mixture variation

The alert detects 90% of events but also fires for 5% of non-events. With 1% prevalence, only about 15.4% of alerts correspond to events. Separately, two subpopulations with variance one yield total variance four because their means differ. The between-group component cannot be learned from within-group standard deviations alone.

### Dynamics and nonlinear averages

The two-state transition matrix moves toward probabilities two-thirds and one-third. The code verifies invariance and a finite-step approximation separately. Squaring values 1 and 3 gives an average of 5, while squaring their average gives 4. That gap is the variance, an exact instance of Jensen's inequality.

### Simulate the central limit theorem's standardized quantity

Six thousand independent samples each contain 32 exponential observations. Their means are centered at the known mean one and multiplied by \(\sqrt{32}\), because the population SD is one. The resulting mean is near zero and variance near one, with less skew than the raw observations. This demonstrates the CLT for this finite-variance independent model; it does not validate a universal sample-size rule.

### Complete executable example

```python
import numpy as np


def bayes_and_total_variance():
    prevalence, sensitivity, false_positive = 0.01, 0.9, 0.05
    positive = prevalence * sensitivity + (1 - prevalence) * false_positive
    posterior = prevalence * sensitivity / positive
    assert 0.15 < posterior < 0.16
    weights, means, variances = np.array([0.25, 0.75]), np.array([0.0, 4.0]), np.array([1.0, 1.0])
    mean = weights @ means
    variance = weights @ variances + weights @ (means - mean) ** 2
    assert mean == 3 and variance == 4
    print("P(event | alert):", round(posterior, 4), "mixture variance:", variance)


def markov_and_jensen():
    transition = np.array([[0.8, 0.2], [0.4, 0.6]])
    stationary = np.array([2 / 3, 1 / 3])
    assert np.allclose(stationary @ transition, stationary)
    distribution = np.array([1.0, 0.0]) @ np.linalg.matrix_power(transition, 20)
    assert np.allclose(distribution, stationary, atol=1e-7)
    x = np.array([1.0, 3.0])
    assert np.mean(x * x) > np.mean(x) ** 2
    print(
        "Long-run state probabilities:",
        distribution,
        "variance gap:",
        np.mean(x * x) - np.mean(x) ** 2,
    )


def central_limit_simulation():
    rng = np.random.default_rng(303)
    samples = rng.exponential(size=(6000, 32))
    standardized = np.sqrt(32) * (samples.mean(axis=1) - 1)
    assert abs(standardized.mean()) < 0.06
    assert abs(standardized.var(ddof=1) - 1) < 0.08
    raw_skew = np.mean((samples[:, 0] - samples[:, 0].mean()) ** 3) / samples[:, 0].std() ** 3
    mean_skew = np.mean((standardized - standardized.mean()) ** 3) / standardized.std() ** 3
    assert abs(mean_skew) < abs(raw_skew)
    print(
        "CLT standardized mean/variance:",
        standardized.mean(),
        standardized.var(ddof=1),
        "raw/mean skew:",
        raw_skew,
        mean_skew,
    )


def main():
    central_limit_simulation()
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
