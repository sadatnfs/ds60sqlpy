# bayes-020: Stan noncentered hierarchies and prediction targets

Tutorial mode. Stage: advanced. Direct prerequisites: `bayes-018`, `bayes-010`.

## Separate group variation from observation noise

A hierarchy distinguishes variation among group means from variation among observations within a group. The fixture has three groups with unequal numbers of observations and a known within-group standard deviation .5. Unknown population mean mu and between-group scale tau describe the distribution of group means.

The noncentered representation uses \(z_j\sim\mathcal N(0,1)\) and \(\theta_j=\mu+\tau z_j\). This is a computational parameterization of a normal hierarchy. Its usefulness depends on how strongly group effects are informed by data; it is not a universal rule that every hierarchy must be noncentered.

## Key terms

- **Between-group scale:** The parameter tau describing how much group means vary around the population mean mu.
- **Partial pooling:** Combining each group's own data with the population distribution, so small groups borrow more strength.
- **Noncentered representation:** theta_j = mu + tau z_j with z_j standard normal, which often helps weakly informed groups.
- **New-group prediction:** A draw of a new group mean from Normal(mu, tau), plus observation noise when predicting a new observation.

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

The two short classroom chains are enough to demonstrate actual compilation, sampling and summaries, not to certify all group-level tails. Undefined diagnostics on constants differ from concerning diagnostics on tau, mu or theta. Any divergence, an R-hat at or above 1.01, bulk or tail effective sizes below about 100 per chain or inconsistent chains should lead to investigation and an explicitly prepared longer analysis.

## Answered scientific discussion

**Can adding more observations to one group resolve every group estimate?** It improves information about that group and may inform the population distribution, but other groups can remain weakly observed. The hierarchy's structure determines how information is shared.

**Which prediction should be used for a deployment region?** First decide whether it is a known modeled group or a new group, and whether exchangeability is plausible. Then include every relevant uncertainty level. A prediction function cannot decide that scientific interpretation from an integer ID alone.

## Worked example: Predictive sd for an existing group by sample size and for a new group

```python
import numpy as np

mu, tau, sigma = 10.0, 2.0, 4.0  # hyperparameters held fixed for clarity
ybar = 14.0
for n_j in (1, 5, 50):
    prec = 1 / tau**2 + n_j / sigma**2
    mean = (mu / tau**2 + n_j * ybar / sigma**2) / prec
    sd_theta = np.sqrt(1 / prec)
    print(
        f"existing group, n={n_j:>2}: theta mean {mean:.3f}, sd {sd_theta:.3f}, new-observation sd {np.sqrt(sd_theta**2 + sigma**2):.3f}"
    )
print(
    f"new group: theta mean {mu:.3f}, sd {tau:.3f}, new-observation sd {np.sqrt(tau**2 + sigma**2):.3f}"
)
```

Observed output:

```text
existing group, n= 1: theta mean 10.800, sd 1.789, new-observation sd 4.382
existing group, n= 5: theta mean 12.222, sd 1.333, new-observation sd 4.216
existing group, n=50: theta mean 13.704, sd 0.544, new-observation sd 4.037
new group: theta mean 10.000, sd 2.000, new-observation sd 4.472
```

Holding the hyperparameters at \(\mu=10\), \(\tau=2\) and \(\sigma=4\) isolates how group size shapes prediction. An existing group whose observed mean is 14 is pulled toward 10 in proportion to how little it has seen. With one observation its effect is estimated at 10.800 with standard deviation 1.789; with five it is 12.222 and 1.333; with fifty it reaches 13.704 and 0.544. Predicting a new observation from that group adds the within-group noise, so the standard deviation runs from 4.382 down to 4.037 and can never fall below \(\sigma=4\). A brand-new group has no data of its own. Its effect is drawn from the population distribution with mean 10 and standard deviation 2, and its next observation has standard deviation \(\sqrt{4+16}=4.472\). The gap between 4.472 and 4.037 is the value of fifty observations from that group. In Stan, the existing-group prediction indexes theta[j], while the new-group prediction must first draw a new effect with normal_rng(mu, tau).

## Complete reproducible program

The prepared Stan pad compiles `main.stan` and samples two chains with 100 warmup and 100 retained draws each. Its tiny data are declared in `transformed data`; this pad has no separate JSON editor. The linked project explains standard data-block workflows. These teaching-sized chains can fail the convergence screen from `bayes-006` (R-hat below 1.01, at least 100 bulk and tail effective draws per chain, no divergences); read the printed diagnostics against it before interpreting any estimate. Runtime: `stan-cpu`.

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
