# bayes-021: Stan logistic likelihoods and separation-aware priors

Tutorial mode. Stage: advanced. Direct prerequisites: `bayes-018`, `bayes-014`.

## Model the binary observation on a stable scale

A logistic model represents a binary outcome through a linear predictor \(\eta_i=\alpha+\beta x_i\) and probability \(p_i=\operatorname{logit}^{-1}(\eta_i)\). Stan's Bernoulli-logit density accepts the linear predictor directly and evaluates the log likelihood stably. Computing a probability with an extreme exponential and then taking its logarithm can lose precision unnecessarily.

The synthetic fixture contains eight covariate values and overlapping outcomes, so the positive and negative classes are not perfectly separated. The priors are proper normal distributions on intercept and slope. Their scales have meaning in the units of x and should be reviewed through prior prediction.

## Worked case 1: follow likelihood, probabilities and replicas

The model block contributes a Bernoulli-logit likelihood for every observed outcome. The generated quantities calculate fitted probabilities, pointwise log likelihood and replicated binary outcomes. These are different objects: a probability is a parameter-derived prediction, while a replicated outcome includes a Bernoulli draw conditional on that prediction.

The probability at x equal to zero depends only on the intercept and provides a simple interpretation anchor. The slope is an additive effect on log odds per unit of x, not a constant change in probability. The same slope can imply different probability changes at different starting risks.

The code stores `bernoulli_logit_lpmf` contributions rather than reconstructing log probabilities from rounded displayed values. Rounding a probability to zero or one for display must not alter the likelihood calculation or create artificial negative infinity values in evaluation.

## Worked case 2: reason about complete separation

Consider replacing the outcomes with zeros for every negative x and ones for every positive x. An unregularized logistic likelihood can keep improving as a separating coefficient grows without a finite maximum. A proper normal prior yields a proper posterior for this bounded likelihood, but the likelihood may still provide limited information about how large the coefficient should be.

This is not evidence that priors are merely numerical workarounds. They define the model in weakly informed directions and can materially influence predictions, especially away from the observed covariates. The appropriate analysis examines prior sensitivity and posterior prediction rather than treating any finite coefficient as data-determined.

Prior predictive behavior depends on covariate scale. A slope prior with standard deviation 2.5 can imply very extreme probabilities when x spans a broad range. Calling that prior weak without examining the resulting probabilities is incomplete. Standardizing x can clarify prior meaning, but its transformation must be retained for future predictions.

## Prediction, calibration and decisions

Binary predictive evaluation should consider calibration, discrimination and decision utility separately. A ranking metric can be high while predicted probabilities are poorly calibrated. A fixed .5 threshold can be inappropriate when errors have unequal consequences or when the operational constraint is a limited number of actions.

The observation process matters too. Case-control sampling, selective labels and missing outcomes can alter the relationship between observed data and a population probability. A correctly fitted logistic likelihood for the observed sample does not automatically identify a population risk or causal effect. Define the target and any sampling adjustments before interpreting the probability.

The classroom's short chains demonstrate the actual compiled model. Inspect coefficient and prediction diagnostics and retain warnings. A stable-looking fitted probability at one x value does not guarantee adequate exploration of a weakly identified tail coefficient or extrapolated probability.

## Answered scientific discussion

**Why use the logit density instead of a manually computed sigmoid in the likelihood?** It preserves the intended calculation at extreme linear predictors and avoids unnecessary precision loss. It does not change the statistical model or solve separation by itself.

**Does a credible interval excluding zero imply a useful intervention?** It concerns a parameter conditional on the model. Practical utility, transport, intervention identification and predictive performance require additional questions and evidence. The tutorial supplies a complete computational path without collapsing those scientific distinctions.

## Complete reproducible program

The prepared Stan pad compiles and samples `main.stan` with fixed bounded settings. Its tiny data are declared in `transformed data`; this pad has no separate JSON editor. The linked project explains standard data-block workflows. Runtime: `stan-cpu`.

```stan
transformed data {
  int N = 8;
  vector[N] x = [-2, -1.5, -1, -0.5, 0.5, 1, 1.5, 2]';
  array[N] int y = {0, 0, 1, 0, 1, 0, 1, 1};
}
parameters {
  real alpha;
  real beta;
}
model {
  alpha ~ normal(0, 1.5);
  beta ~ normal(0, 2.5);
  y ~ bernoulli_logit(alpha + beta * x);
}
generated quantities {
  vector[N] probability = inv_logit(alpha + beta * x);
  vector[N] log_lik;
  array[N] int y_rep;
  for (n in 1 : N) {
    log_lik[n] = bernoulli_logit_lpmf(y[n] | alpha + beta * x[n]);
    y_rep[n] = bernoulli_rng(probability[n]);
  }
  real probability_at_zero = inv_logit(alpha);
}
```

## Primary references

- [Stan logistic and probit regression](https://mc-stan.org/docs/stan-users-guide/regression.html)
