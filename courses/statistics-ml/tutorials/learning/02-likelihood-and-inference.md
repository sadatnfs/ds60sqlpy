# From Bernoulli likelihood to interval coverage

Tutorial ID: `statistics-learning-002`. Prerequisites: `statistics-learning-001`, `statistics-004`, `statistics-008`. Complete program: [learning_02.py](examples/learning_02.py).

## Key terms

- **Likelihood:** The probability of the fixed observed data viewed as a function of the parameter, proportional to \(p^s(1-p)^{n-s}\) here; it is not a distribution over parameter values.
- **Fisher information:** The expected negative second derivative of the log likelihood, \(n/[p(1-p)]\) for \(n\) Bernoulli trials, which links curvature to large-sample variance.
- **Wald interval:** The estimate plus or minus a normal critical value times the plug-in standard error; it can extend below zero and collapses to [0,0] when no successes occur.
- **Wilson interval:** The set of candidate probabilities not rejected by a score comparison that uses each candidate's own null variance.
- **Coverage:** The long-run share of intervals from a procedure that contain the true parameter, computed exactly here by weighting each possible count by its binomial probability.

## Separate data, parameter and estimator

Suppose independent trials share an unknown success probability \(p\). The observed sequence is fixed while we compare possible parameter values. For \(s\) successes in \(n\) trials, the likelihood is proportional to \(p^s(1-p)^{n-s}\). It is a function of the parameter, not a probability distribution over parameters. A prior plus likelihood would define a Bayesian posterior instead.

Taking logarithms turns products into sums:

\[
\ell(p)=s\log p+(n-s)\log(1-p),\quad
\ell'(p)=\frac{s}{p}-\frac{n-s}{1-p}.
\]

For an interior solution, setting the score to zero gives \(\widehat p=s/n\). When \(s=0\) or \(s=n\), the maximizer is on the boundary and the interior differentiation argument must be modified. The success count is sufficient for the common probability under this model; the ordering could still matter for diagnosing a violated independence assumption.

## Curvature connects the model to precision

Expected negative second derivative gives Fisher information \(I_n(p)=n/[p(1-p)]\). A regular large-sample approximation suggests variance \(p(1-p)/n\), estimated by plugging in the fitted probability. This is a connection between likelihood curvature and repeated-sample precision under the model, not a universal rule that any steep objective implies a calibrated interval.

With one success in 12 trials, the estimate is .0833. The ordinary Wald interval uses this plug-in SE and can extend below zero. Clipping the endpoint to zero makes the printed interval legal but does not fix its coverage. In particular, zero observed successes produce zero estimated variance and the degenerate Wald interval [0,0].

## Invert a score comparison

The Wilson interval solves the inequality

\[
\frac{(\widehat p-p)^2}{p(1-p)/n}\le z_{.975}^2
\]

for candidate values of \(p\), using the null candidate's variance rather than the estimate's variance. Its center is \((\widehat p+z^2/(2n))/(1+z^2/n)\); its halfwidth follows from the quadratic formula. The program calculates both intervals and shows that Wilson has a positive lower bound for the one-success example.

## Evaluate the procedure, not one interval

At a declared true probability .05, enumerate every possible count from zero through 12. Weight each count's coverage indicator by its exact binomial probability. This calculates the coverage of the complete procedure without Monte Carlo noise. Wilson covers much more often than the Wald interval in this setting. Wilson is still an approximation and can have coverage above or below .95 at other probabilities because counts are discrete.

The example's oracle is available only because the data-generating probability is specified. In real data, inspecting the realized interval cannot reveal whether it contains the unknown truth. Robustness analysis should change meaningful assumptions, such as shared latent probabilities or repeated users, not merely rerun the same calculation with another seed.

**Answered discussion: Does a more sophisticated interval fix selected data?** No. If only successful visits are logged, both likelihood and interval analyze a distorted population. Fix the observation model and estimand before selecting an uncertainty formula.

## Worked example: three counts, two intervals

The coverage enumeration in `examples/learning_02.py` uses one success in twelve. Printing the two intervals at zero, one and six successes shows where they differ and where they agree.

```python
import numpy as np
from scipy import stats


def wilson(s, n, z=stats.norm.ppf(0.975)):
    p = s / n
    center = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return center - half, center + half


n, z = 12, stats.norm.ppf(0.975)
for s in (0, 1, 6):
    p = s / n
    half = z * np.sqrt(p * (1 - p) / n)
    lo, hi = wilson(s, n)
    print(f"s={s:2d} wald=[{p - half:6.3f}, {p + half:.3f}] wilson=[{lo:.3f}, {hi:.3f}]")
```

```text
s= 0 wald=[ 0.000, 0.000] wilson=[0.000, 0.242]
s= 1 wald=[-0.073, 0.240] wilson=[0.015, 0.354]
s= 6 wald=[ 0.217, 0.783] wilson=[0.254, 0.746]
```

With no successes the Wald interval is the single point [0.000, 0.000], a confident claim that the probability is exactly zero, while Wilson reports [0.000, 0.242], admitting that rates up to about one in four are compatible with twelve failures. With one success, Wald reaches -0.073, an impossible probability, and Wilson stays inside [0.015, 0.354]. With six successes the two are close, [0.217, 0.783] against [0.254, 0.746], because the plug-in variance is accurate near one half. The Wilson center is pulled toward one half, which is what keeps its lower end positive at small counts.

## Worked example: coverage at several true probabilities

Exact enumeration is cheap, so repeat it at three declared truths instead of one.

```python
import numpy as np
from scipy import stats

n, z = 12, stats.norm.ppf(0.975)
s = np.arange(n + 1)
phat = s / n
half = z * np.sqrt(phat * (1 - phat) / n)
center = (phat + z * z / (2 * n)) / (1 + z * z / n)
whalf = z * np.sqrt(phat * (1 - phat) / n + z * z / (4 * n * n)) / (1 + z * z / n)
for true_p in (0.05, 0.2, 0.5):
    w = stats.binom.pmf(s, n, true_p)
    wald = w @ ((phat - half <= true_p) & (true_p <= phat + half))
    wil = w @ ((center - whalf <= true_p) & (true_p <= center + whalf))
    print(f"p={true_p:.2f} wald coverage={wald:.3f} wilson coverage={wil:.3f}")
```

```text
p=0.05 wald coverage=0.457 wilson coverage=0.980
p=0.20 wald coverage=0.912 wilson coverage=0.981
p=0.50 wald coverage=0.854 wilson coverage=0.961
```

At \(p=.05\) the nominal 95% Wald procedure covers only 45.7% of the time, mostly because the most likely outcome, zero successes, produces the degenerate interval. At \(p=.2\) Wald reaches 91.2% and at \(p=.5\) only 85.4%, below its label even in the symmetric case because twelve trials yield few distinct counts. Wilson covers 98.0%, 98.1% and 96.1%: conservative here, not exact. Neither number is a property of a realized interval; each is the long-run behavior of a rule at a stated truth, which is why a careful report names the interval method rather than only its endpoints.

## Assumptions behind every interval in this unit

Both procedures assume independent trials with one shared probability. Repeated visits from the same user, or a probability that drifts across the collection window, give overdispersion: the true variance exceeds \(p(1-p)/n\) and both intervals become too narrow regardless of their small-sample corrections. A quick diagnostic is to compare the variance of per-group success fractions with the binomial prediction. When the counts are near zero or n, prefer Wilson or an exact method, and say which you used.

Continue to [logistic regression](03-logistic-model-to-decision.md). Related chapter: [estimation](../../chapters/08-estimation-and-statistical-inference.md). Reference: [NIST proportion intervals](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm).
