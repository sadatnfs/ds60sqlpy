# bayes-003: Conjugacy, posterior prediction and duplicated observations

Tutorial mode. Stage: beginner. Direct prerequisites: `bayes-002`.

## A posterior predicts through a distribution

For independent Bernoulli outcomes with unknown success probability \(p\), a beta prior is conjugate. Starting from \(p\sim\operatorname{Beta}(a,b)\), observing \(s\) successes in \(n\) trials gives \(p\mid y\sim\operatorname{Beta}(a+s,b+n-s)\). Conjugacy provides exact calculations against which more general computation can be checked.

The prior's concentration controls how much it favors particular probability ranges. It is sometimes described using pseudo-count language, but those quantities are not necessarily real independent observations. The origin of a prior and the evidence already incorporated in it must remain explicit.

Posterior prediction averages the sampling model over posterior uncertainty. It is not generally equivalent to inserting a posterior mean into the likelihood. The distinction matters for tail probabilities, uncertainty and decisions.

## Key terms

- **Conjugate prior:** A prior whose posterior stays in the same family, such as Beta(a, b) becoming Beta(a + s, b + n - s) after s successes in n Bernoulli trials.
- **Posterior predictive distribution:** The sampling model averaged over posterior uncertainty, not the likelihood evaluated at a posterior mean.
- **Beta-binomial distribution:** The predictive distribution of future successes when a binomial count is averaged over a beta posterior.
- **Double counting:** Conditioning on the same observations twice, which overstates certainty because the duplicates carry no new information.

## Worked case 1: derive the beta-binomial prediction

A Beta(2,2) prior and eight successes in ten trials produce a Beta(10,4) posterior. For \(K\) successes in five future trials, the integrated probability is

\[
P(K=k\mid y)=\binom{5}{k}\frac{B(10+k,4+5-k)}{B(10,4)}.
\]

The program calculates these probabilities using log gamma and log beta functions, avoiding unnecessarily large factorials. It checks that they sum to one and that the predictive mean is five times the posterior mean probability.

The integrated predictive variance is larger than the variance from a Binomial(5,10/14) distribution. The latter treats the estimated probability as known. The law of total variance makes the missing component visible:

\[
\operatorname{Var}(K\mid y)=
\mathbb{E}[\operatorname{Var}(K\mid p,y)\mid y]
+\operatorname{Var}(\mathbb{E}[K\mid p,y]\mid y).
\]

The second term represents uncertainty in the parameter that also affects future outcomes. More data can reduce it, but it is not removed simply because a posterior mean is easy to report.

## Worked case 2: duplicate a batch of observations

The same ten outcomes are now mistakenly counted twice. The resulting update is Beta(18,6). Its parameter variance is smaller than the correct Beta(10,4) variance, and its mean also changes because the prior has been given less relative weight. The program records both variances.

That update would be appropriate for a genuine additional independent batch with the same observed counts under the same model. It is inappropriate for duplicate rows, repeat ingestion or cached evidence representing the original batch. The mathematical formula cannot determine which situation occurred.

This is one reason to preserve record identities and the data-processing path used by a model. A posterior can become more confident after a pipeline bug that multiplies rows in a join. The code can be numerically correct while its likelihood counts the wrong number of independent outcomes.

## Examine the exchangeability assumption

The simple Bernoulli model uses one common probability. Outcomes varying systematically by group, time or exposure may need a richer model. A hierarchy can allow related probabilities while sharing information; a temporal model can represent changing behavior. A beta-binomial predictive distribution from one fixed probability should not be treated as a universal model for all overdispersed binary data.

Prediction also requires a target horizon and population. Five new trials from the same modeled process differ from five trials after a policy change or in a new population. An intervention can change both the success mechanism and which units are observed. Those changes need assumptions beyond the conjugate update.

Small exact models are valuable because their full probability distributions can be inspected. Compare the entire predictive mass function rather than only its mean. Two models can agree on an expected count while disagreeing on a rare but consequential outcome.

## Answered scientific discussion

**Is plug-in prediction always unacceptable?** It can be a useful approximation when parameter uncertainty is negligible for the decision. The approximation should be assessed rather than assumed. Here the exact distribution exposes the omitted variance directly.

**What does conjugacy buy us?** It provides an analytic posterior and a clear numerical oracle. It does not validate independent trials, stable probabilities, correct record counts or the relevance of the future prediction target.

## Worked example: Splitting predictive variance for the next five trials

```python
import numpy as np
from scipy import stats

a, b = 2 + 7, 2 + 3  # Beta(2, 2) prior, 7 successes in 10 trials
m = 5
pred = stats.betabinom(m, a, b)
print("P(Y = 0..5):", pred.pmf(np.arange(m + 1)).round(4))
p_mean = a / (a + b)
p_var = a * b / ((a + b) ** 2 * (a + b + 1))
within = m * (p_mean * (1 - p_mean) - p_var)  # E[m p (1 - p)]
between = m**2 * p_var  # Var(m p)
print(f"predictive mean {pred.mean():.4f}, variance {pred.var():.4f}")
print(
    f"E[binomial variance] {within:.4f} + Var[conditional mean] {between:.4f} = {within + between:.4f}"
)
print(f"plug-in Binomial(5, {p_mean:.4f}) variance {m * p_mean * (1 - p_mean):.4f}")
```

Observed output:

```text
P(Y = 0..5): [0.0147 0.0735 0.1838 0.2889 0.2889 0.1502]
predictive mean 3.2143, variance 1.4541
E[binomial variance] 1.0714 + Var[conditional mean] 0.3827 = 1.4541
plug-in Binomial(5, 0.6429) variance 1.1480
```

After 7 successes in 10 trials under a Beta(2, 2) prior, the posterior is Beta(9, 5) with mean \(9/14=0.6429\). Predicting five new trials, the beta-binomial puts equal mass 0.2889 on three and four successes and keeps 0.0147 on zero. Its variance, 1.4541, splits into two named parts by the law of total variance. The expected binomial variance, \(E[5p(1-p)]=1.0714\), is the coin-flip noise that would remain even if \(p\) were known. The second part, \(\mathrm{Var}(5p)=25\times0.01531=0.3827\), is uncertainty about \(p\) itself. The plug-in Binomial(5, 0.6429) variance of 1.1480 ignores that second part and understates the spread by about 21 percent. More data shrinks only the parameter term; after thousands of trials the predictive variance would approach \(5p(1-p)\), never zero. Duplicating records would shrink the parameter term too, but falsely, since repeated rows carry no new information about \(p\).

## Complete reproducible program

Run the complete program in the classroom's declared prepared profile. Every run starts a fresh process with tiny offline synthetic data. This is a worked tutorial, with no exam or hidden solution. Runtime: `python-core`.

```python
"""Complete bounded synthetic Bayesian investigation; no external data."""

from __future__ import annotations

import json

import numpy as np
from scipy import special, stats


def predictive_mass(k, trials, alpha, beta):
    k = np.asarray(k)
    log_choose = (
        special.gammaln(trials + 1) - special.gammaln(k + 1) - special.gammaln(trials - k + 1)
    )
    return np.exp(
        log_choose + special.betaln(alpha + k, beta + trials - k) - special.betaln(alpha, beta)
    )


def run_cases():
    a, b = 2 + 8, 2 + 2
    future = 5
    k = np.arange(future + 1)
    probabilities = predictive_mass(k, future, a, b)
    mean = float(k @ probabilities)
    variance = float(((k - mean) ** 2) @ probabilities)
    plugin = future * (a / (a + b)) * (b / (a + b))
    assert (
        np.isclose(probabilities.sum(), 1)
        and np.isclose(mean, future * a / (a + b))
        and variance > plugin
    )
    duplicated_variance = stats.beta.var(18, 6)
    correct_variance = stats.beta.var(a, b)
    assert duplicated_variance < correct_variance
    return dict(
        posterior_mean=a / (a + b),
        future_probabilities=probabilities.tolist(),
        predictive_variance=variance,
        plug_in_variance=plugin,
        correct_parameter_variance=float(correct_variance),
        duplicated_record_variance=float(duplicated_variance),
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("bayes-003 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
```

## Primary references

- [Stan posterior and prior predictive checks](https://mc-stan.org/docs/stan-users-guide/ppcs.html)
