# A causal estimate needs identification, overlap and uncertainty

Tutorial ID: `statistics-science-001`. Prerequisites: `statistics-015`, `statistics-017`, `statistics-learning-007`. Complete program: [science_01.py](examples/science_01.py).

## Key terms

- **Conditional exchangeability:** Treatment assignment is independent of the potential outcomes given the measured pretreatment covariates.
- **Positivity:** Every covariate pattern has a positive probability of each treatment, so both arms have support; estimated propensities show this overlap.
- **Cross-fitting:** Fitting nuisance models on other folds and predicting only on the held-out fold, which reduces same-sample overfitting dependence.
- **Double robustness:** The property that the score's conditional bias is zero when either the propensity model or the outcome model is correct.
- **Bias sensitivity:** Shifting the estimate and both interval endpoints down by a plausible residual bias to see whether the decision threshold is still met.

## Specify a world before choosing an estimator

Two pretreatment covariates affect treatment and outcome. The synthetic propensity is \(e(X)=\sigma(.6X_1)\); untreated mean is \(m_0(X)=X_1^2+X_2\); treatment effect is \(1+.5X_1\). Since \(X_1\) is symmetric around zero, the population ATE is one. Assignment is conditionally randomized given X and both treatment probabilities are positive, so conditional exchangeability, consistency and positivity identify the effect in this deliberately known world.

A real analyst cannot verify those assumptions merely by fitting a good propensity model. Here the generating equations provide an oracle so the estimator can be studied separately from identification. No observational algorithm creates a missing confounder.

## Fit nuisance functions on other rows

Split 1,200 observations into three folds. For each held-out fold, train logistic propensity on the other folds and a separate response forest in each treatment arm. Predict the three nuisance quantities only on held-out rows. This produces an actual cross-fitted causal estimator rather than a disconnected demonstration of generic cross-validation.

For each observation, calculate

\[
\phi_i=\widehat m_1(X_i)-\widehat m_0(X_i)
+\frac{A_i\{Y_i-\widehat m_1(X_i)\}}{\widehat e(X_i)}
-\frac{(1-A_i)\{Y_i-\widehat m_0(X_i)\}}{1-\widehat e(X_i)}.
\]

Average these scores. Under the necessary nuisance-rate and regularity conditions, their sample SD divided by \(\sqrt n\) estimates the asymptotic SE. Cross-fitting reduces same-sample overfitting dependence; it does not guarantee those conditions for arbitrary learners.

The example gives an ATE near 1.001, score SE .071 and approximate interval [.861,1.141]. Estimated propensities range roughly .195 to .803. That overlap is favorable in this fixture. Report the distribution of scores and weights in a harder case; clipping extreme probabilities stabilizes arithmetic but can introduce bias and does not repair absent support.

## Explain double robustness algebraically

Let \(\delta_a=\widehat m_a-m_a\). Conditional bias in the score equals

\[
(\widehat e-e)\left\{\frac{\delta_1}{\widehat e}
+\frac{\delta_0}{1-\widehat e}\right\}.
\]

The complete program checks four known-function cases: both correct, only propensity correct, only outcome correct, and both wrong. The first three have zero conditional bias by construction. The deliberately misspecified fourth has average bias about -.423. This proves a bounded algebraic property of the constructed functions, not that either fitted nuisance learner is correct in real data.

## Turn hidden-confounding concern into a decision sensitivity

Suppose a practical benefit must exceed .5 and a domain argument permits positive residual bias B. Shift the estimate and both interval endpoints downward by B. At B=.25 the lower endpoint is about .611; at B=.5 it is about .361, no longer establishing the threshold. The code reports point sensitivity at B=0,.25,.5,1. This is a transparent additive bias scenario, not an identified estimate of hidden confounding. A domain model must justify plausible B values.

**Answered discussion: Is a causal forest automatically better?** A more flexible effect model can change estimation, but identification and support remain. Compare the actual target, nuisance errors, uncertainty and independent policy value before promoting a model name into causal evidence.

## Worked example: four estimators on the same rows

The cross-fitted forest estimator in `examples/science_01.py` is one of several ways to use the same 1,200 rows. This snippet fits simpler in-sample nuisances, a logistic propensity and arm-specific linear outcome models, and compares the resulting estimators.

```python
import numpy as np
from scipy import special
from sklearn.linear_model import LinearRegression, LogisticRegression

rng = np.random.default_rng(1701)
n = 1200
x = rng.uniform(-2, 2, size=(n, 2))
e = special.expit(0.6 * x[:, 0])
a = rng.binomial(1, e)
y = x[:, 0] ** 2 + x[:, 1] + a * (1 + 0.5 * x[:, 0]) + rng.normal(size=n)
eh = LogisticRegression(C=100).fit(x, a).predict_proba(x)[:, 1]
m0 = LinearRegression().fit(x[a == 0], y[a == 0]).predict(x)
m1 = LinearRegression().fit(x[a == 1], y[a == 1]).predict(x)
aipw = m1 - m0 + a * (y - m1) / eh - (1 - a) * (y - m0) / (1 - eh)
print(f"difference in means: {y[a == 1].mean() - y[a == 0].mean():.3f}")
print(f"linear outcome model only: {np.mean(m1 - m0):.3f}")
print(f"IPW only: {np.mean(a * y / eh - (1 - a) * y / (1 - eh)):.3f}")
print(f"AIPW: {aipw.mean():.3f} (se {aipw.std(ddof=1) / np.sqrt(n):.3f})")
```

```text
difference in means: 1.157
linear outcome model only: 1.089
IPW only: 1.081
AIPW: 1.089 (se 0.105)
```

The raw difference in means is 1.157, about 0.16 above the population ATE of one because treated units have larger \(X_1\) and therefore larger effects and outcomes. The linear outcome model, IPW and AIPW all land near 1.09. The linear models omit \(X_1^2\), yet their contrast is nearly right because the missing curvature is shared by both arms and cancels in \(m_1-m_0\); misspecification hurts the effect only where it differs between arms. The AIPW standard error of 0.105 is larger than the 0.071 from the forest version: residuals that still contain the \(X_1^2\) curve are bigger, and the score variance inherits them. A better outcome model buys precision even when a cruder one is already roughly unbiased.

## Worked example: weights when overlap thins

Positivity is easiest to appreciate by breaking it. Keep the same covariate, steepen the propensity slope from 0.6 to 3.0, and summarize the inverse weights.

```python
import numpy as np
from scipy import special

rng = np.random.default_rng(1701)
x1 = rng.uniform(-2, 2, size=1200)
for slope in (0.6, 3.0):
    e = special.expit(slope * x1)
    a = rng.binomial(1, e)
    w = np.where(a == 1, 1 / e, 1 / (1 - e))
    ess = w.sum() ** 2 / np.sum(w**2)
    print(
        f"slope {slope}: propensity range [{e.min():.3f}, {e.max():.3f}] "
        f"max weight {w.max():.1f} effective n {ess:.0f}"
    )
```

```text
slope 0.6: propensity range [0.232, 0.768] max weight 4.3 effective n 1067
slope 3.0: propensity range [0.003, 0.998] max weight 142.2 effective n 128
```

At the guide slope, propensities stay within [0.232, 0.768], the largest weight is 4.3, and the Kish effective sample size is 1,067 of 1,200. At slope 3.0 the range spreads to [0.003, 0.998], one unit carries a weight of 142.2, and the effective sample size collapses to 128. The estimator is still defined, but a handful of rows now decide it, and its variance and sensitivity to a single outcome soar. Clipping those weights would lower variance by quietly changing the population being described.

## Diagnostics to report with any doubly robust estimate

Show the propensity distribution by arm and the effective sample size of the weights. Report the score distribution and its largest contributions. Compare AIPW with outcome-only and weighting-only estimates; large disagreement points to a nuisance problem worth investigating. State which covariates were measured before treatment, since adjusting for a post-treatment variable biases every estimator here equally.

Continue to [longitudinal regimes](08-longitudinal-regimes-and-target-trials.md). Primary reference: [Causal Inference: What If](https://miguelhernan.org/whatifbook).
