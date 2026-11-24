# Logistic regression: probability, uncertainty and action

Tutorial ID: `statistics-learning-003`. Prerequisites: `statistics-learning-002`, `statistics-011`, `statistics-022`. Complete program: [learning_03.py](examples/learning_03.py).

## Key terms

- **Log odds:** The logarithm of \(p/(1-p)\), modeled as the linear predictor in logistic regression and mapped back to a probability by the logistic function.
- **Odds ratio:** The multiplicative change in odds for a one-unit predictor change, obtained by exponentiating a slope; it is conditional on the other covariates and is not a risk ratio.
- **Log loss:** The average negative log likelihood of held-out labels, which heavily penalizes confident wrong probabilities.
- **Brier score:** The average squared difference between predicted probabilities and observed binary outcomes.
- **Calibration:** Agreement between predicted probabilities and observed event fractions, checked here with binned reliability summaries.

## Build a probability model

For binary outcomes, a linear probability expression can leave [0,1]. Logistic regression instead models the log odds \(\eta_i=x_i^{\mathsf T}\beta\), then transforms to \(p_i=1/(1+e^{-\eta_i})\). Odds are \(p/(1-p)\); they are not probability. A baseline probability .2 has odds .25. Doubling odds gives .5 and therefore probability one-third.

The synthetic case contains 500 independent observations with two continuous predictors. An intercept plus those predictors makes a three-column design. The first 350 rows fit the model and the last 150 evaluate it. The fixture is identically distributed and ordered independently, so this boundary has a clear interpretation. Repeated users or time drift would require a different split.

## Derive and fit the objective

Independent Bernoulli contributions yield negative log likelihood

\[
L(\beta)=\sum_i\{\log(1+e^{\eta_i})-y_i\eta_i\},\quad
\nabla L=X^{\mathsf T}(p-y),\quad
H=X^{\mathsf T}WX,
\]

where \(W_{ii}=p_i(1-p_i)\). `logaddexp(0, eta)` avoids overflow in the log-sum-exp term. The program fits using the analytic gradient, checks convergence and the gradient norm, then solves with the observed Hessian for a model-based covariance approximation.

The coefficient interval uses a regular, correctly specified independent Bernoulli model with adequate information. Exponentiating a slope interval gives a conditional odds-ratio interval. It does not give a risk-ratio interval or automatically adjust for dependence, selection or model misspecification. A probability contrast should specify both covariate settings and propagate their joint coefficient covariance.

## Evaluate probabilities and actions separately

Held-out log loss penalizes confident errors; Brier score averages squared probability errors. The example also groups predictions into bins and prints bin counts, mean predicted probability and observed event fraction. Small bins can be noisy, so a visually jagged reliability curve is not automatically evidence of severe miscalibration.

With false-positive cost two and false-negative cost eight, the calibrated-probability threshold is \(2/(2+8)=.2\). The code computes realized held-out cost at that prespecified threshold. It does not use test labels to tune the cutoff. A capacity constraint or an intervention that changes outcomes would require a richer decision model.

## Two contrasts that expose interpretation errors

First, a separable four-point dataset has lower unpenalized loss as the coefficient increases from four to eight. A finite maximizer may not exist. Optimization warnings and huge coefficients reflect a real information problem; penalization creates a different fitted objective rather than proving uncertainty is small.

Second, two equally weighted baseline strata have log odds -2 and +2. Applying the same conditional odds ratio two to both gives a marginal odds ratio smaller than two. The strata have the same weights in both groups, so this difference need not indicate confounding. Odds ratios are noncollapsible: marginalizing a nonlinear probability model can change the ratio even without imbalance. Interpret conditional and population-average quantities separately.

**Answered discussion: Is class weighting just another threshold?** No. It changes the training objective and potentially probability calibration. A threshold changes the action after estimating probabilities. Either can be useful, but their assumptions and interpretation differ.

## Worked example: refit with statsmodels and price two cutoffs

The program `examples/learning_03.py` fits by BFGS with an analytic gradient. Refitting the same 350 training rows with `statsmodels` gives an independent check of the coefficients and standard errors, and the held-out rows then show what the cost-based cutoff buys.

```python
import numpy as np
import statsmodels.api as sm
from scipy import special

rng = np.random.default_rng(1102)
x = rng.normal(size=(500, 2))
design = np.column_stack([np.ones(len(x)), x])
y = rng.binomial(1, special.expit(design @ np.array([-0.4, 1.0, -0.7])))
fit = sm.Logit(y[:350], design[:350]).fit(disp=0)
print("coefficients:", np.round(fit.params, 3), "se:", np.round(fit.bse, 3))
print("odds ratio x1:", np.round(np.exp(fit.conf_int()[1]), 3))
test_p = fit.predict(design[350:])
for cutoff in (0.2, 0.5):
    act = test_p > cutoff
    cost = np.mean(2 * (act & (y[350:] == 0)) + 8 * (~act & (y[350:] == 1)))
    print(f"cutoff {cutoff}: flagged {act.sum()} of 150, mean cost {cost:.3f}")
```

```text
coefficients: [-0.601  1.224 -0.673] se: [0.13  0.163 0.137]
odds ratio x1: [2.472 4.682]
cutoff 0.2: flagged 106 of 150, mean cost 1.067
cutoff 0.5: flagged 55 of 150, mean cost 2.120
```

The coefficients -0.601, 1.224 and -0.673 sit near the generating values -0.4, 1.0 and -0.7; the intercept and first slope are each about 1.5 standard errors away, an ordinary amount of sampling noise for 350 rows. The odds-ratio interval for the first predictor is [2.472, 4.682], so a one-unit increase multiplies the odds by roughly two and a half to four and a half, holding the other predictor fixed. At the cost-derived cutoff of 0.2, the model flags 106 of 150 held-out cases and averages 1.067 cost units per case. The familiar 0.5 cutoff flags only 55 and costs 2.120, nearly double, because each missed positive costs four times a false alarm. Nothing was tuned on the test rows: the 0.2 came from the costs, and 0.5 is shown only as the common default.

## Worked example: how stratum spread shrinks the marginal odds ratio

Hold the conditional odds ratio at two and widen the gap between two equally weighted strata.

```python
import numpy as np
from scipy import special

for gap in (0.0, 1.0, 2.0, 4.0):
    base = np.array([-gap, gap])
    p0, p1 = special.expit(base).mean(), special.expit(base + np.log(2)).mean()
    marginal = p1 / (1 - p1) / (p0 / (1 - p0))
    print(f"strata log odds +/-{gap}: p0={p0:.3f} p1={p1:.3f} marginal OR={marginal:.3f}")
```

```text
strata log odds +/-0.0: p0=0.500 p1=0.667 marginal OR=2.000
strata log odds +/-1.0: p0=0.500 p1=0.634 marginal OR=1.734
strata log odds +/-2.0: p0=0.500 p1=0.575 marginal OR=1.352
strata log odds +/-4.0: p0=0.500 p1=0.513 marginal OR=1.054
```

When both strata share log odds zero, the marginal odds ratio equals the conditional value 2.000. As the strata separate to plus and minus 1, 2 and 4, the marginal ratio falls to 1.734, 1.352 and 1.054, even though the arms have identical composition and every individual still has doubled odds. The baseline probability \(p_0\) stays at 0.500 throughout; only the averaging over heterogeneous strata changes. A trial that reports a marginal odds ratio of 1.35 and an adjusted model that reports 2 can both be correct, and comparing them is not a test of confounding.

## Failure modes when the model leaves the notebook

Calibration fitted on one population drifts when prevalence changes, which moves the cost-optimal threshold even if the ranking is unchanged. Separation in a rare category produces enormous coefficients and useless standard errors; check the largest absolute coefficient and the condition of \(X^{\mathsf T}WX\). Report probability contrasts at named covariate settings when readers need risk language.

Continue to [forests](04-forests-and-validation.md). Cross-link: [model evaluation](../../chapters/22-model-validation-and-predictive-performance.md). References: [ISLP classification labs](https://islp.readthedocs.io/en/stable/labs.html), [statsmodels GLM](https://www.statsmodels.org/stable/glm.html).
