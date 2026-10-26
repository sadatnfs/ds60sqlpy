# Logistic regression: probability, uncertainty and action

Tutorial ID: `statistics-learning-003`. Prerequisites: `statistics-learning-002`, `statistics-011`, `statistics-022`. Complete program: [learning_02.py](examples/learning_02.py).

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

Continue to [forests](04-forests-and-validation.md). Cross-link: [model evaluation](../../chapters/22-model-validation-and-predictive-performance.md). References: [ISLP classification labs](https://islp.readthedocs.io/en/stable/labs.html), [statsmodels GLM](https://www.statsmodels.org/stable/glm.html).
