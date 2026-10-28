# bayes-020: Stan noncentered hierarchies and prediction targets

Tutorial mode. Stage: advanced. Direct prerequisites: `bayes-018`, `bayes-010`.

## Separate group variation from observation noise

A hierarchy distinguishes variation among group means from variation among observations within a group. The fixture has three groups with unequal numbers of observations and a known within-group standard deviation .5. Unknown population mean mu and between-group scale tau describe the distribution of group means.

The noncentered representation uses \(z_j\sim\mathcal N(0,1)\) and \(\theta_j=\mu+\tau z_j\). This is a computational parameterization of a normal hierarchy. Its usefulness depends on how strongly group effects are informed by data; it is not a universal rule that every hierarchy must be noncentered.

## Worked case 1: connect typed indices to partial pooling

The `group` array contains one-based indices into the theta vector. Each observed outcome receives the mean for its own group. The code uses an explicit loop so the likelihood's indexing can be followed directly. An incorrectly ordered group array can produce a perfectly valid compiled model for the wrong data mapping.

Small groups generally provide less direct information about their own means, so the population model can exert more influence. The amount of pooling also depends on the estimated tau and the observation scale. Equal sample sizes do not guarantee equal posterior uncertainty if other aspects of the design differ.

The earlier Python tutorial supplies a conditional closed-form shrinkage calculation. Here mu and tau are sampled, so the full posterior incorporates uncertainty in the population distribution. A plug-in shrinkage formula with fixed hyperparameters should not be mistaken for an exact description of that full uncertainty.

## Worked case 2: distinguish existing-group and new-group predictions

The generated quantities include a new group mean drawn from Normal(mu,tau) and a new observation from the first known group. The known-group observation conditions on the posterior theta for a group with observed data, then adds within-group observation noise. The new-group mean instead includes a fresh draw from the population distribution.

A new observation from a new group would include both a new group effect and observation noise. Reporting the uncertainty of only the new-group mean as an interval for that observation would omit one level of variation. Conversely, prediction for a known group can legitimately use evidence about its existing group effect.

The prediction target also depends on whether the new group is exchangeable with those modeled. A new region with different eligibility, measurement or operating conditions can require covariates or a transport argument. A generic group index does not establish that the shared population distribution applies.

## Inspect geometry and prior implications

A small tau creates strong dependence between group effects and their population center in a centered representation. Noncentering can improve exploration in a weak-data regime, but an informative likelihood can create a different geometry in the z coordinates. Review actual parameter and derived-quantity diagnostics after choosing the representation.

Priors on scale parameters deserve scrutiny. A prior that concentrates near zero encourages similar groups; a heavy tail allows greater heterogeneity. Both choices affect prediction for new groups. Conduct prior predictive checks in meaningful outcome units before treating a scale prior as a harmless default.

The two short classroom chains are enough to demonstrate actual compilation, sampling and summaries, not to certify all group-level tails. Undefined diagnostics on constants differ from concerning diagnostics on tau, mu or theta. Divergences, poor effective sizes or inconsistent chains should lead to investigation and an explicitly prepared longer analysis.

## Answered scientific discussion

**Can adding more observations to one group resolve every group estimate?** It improves information about that group and may inform the population distribution, but other groups can remain weakly observed. The hierarchy's structure determines how information is shared.

**Which prediction should be used for a deployment region?** First decide whether it is a known modeled group or a new group, and whether exchangeability is plausible. Then include every relevant uncertainty level. A prediction function cannot decide that scientific interpretation from an integer ID alone.

## Complete reproducible program

The prepared Stan pad compiles and samples `main.stan` with fixed bounded settings. Its tiny data are declared in `transformed data`; this pad has no separate JSON editor. The linked project explains standard data-block workflows. Runtime: `stan-cpu`.

```stan
transformed data {
  int J = 3;
  int N = 10;
  array[N] int group = {1, 1, 2, 2, 2, 3, 3, 3, 3, 3};
  vector[N] y = [-2, -1.5, -0.4, 0, 0.3, 0.8, 1.2, 1.1, 0.9, 1]';
  real observation_sd = 0.5;
}
parameters {
  real mu;
  real<lower=0> tau;
  vector[J] z;
}
transformed parameters {
  vector[J] theta = mu + tau * z;
}
model {
  mu ~ normal(0, 2);
  tau ~ normal(0, 1);
  z ~ std_normal();
  for (n in 1 : N)
    y[n] ~ normal(theta[group[n]], observation_sd);
}
generated quantities {
  real new_group_mean = normal_rng(mu, tau);
  real known_group_outcome = normal_rng(theta[1], observation_sd);
  vector[N] log_lik;
  for (n in 1 : N)
    log_lik[n] = normal_lpdf(y[n] | theta[group[n]], observation_sd);
}
```

## Primary references

- [Stan regression and hierarchical models](https://mc-stan.org/docs/stan-users-guide/regression.html)
