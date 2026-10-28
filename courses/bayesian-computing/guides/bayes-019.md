# bayes-019: Stan constraints, log-rate transformations and Jacobians

Tutorial mode. Stage: advanced. Direct prerequisites: `bayes-017`, `bayes-004`.

## Declared constraints and manual coordinates are different mechanisms

Stan internally represents constrained parameters on an unconstrained scale for sampling and accounts for its declared transforms. If a model author introduces an additional manual coordinate and writes a density for the transformed quantity, the author must account for the associated change of variables correctly.

The fixture uses five Poisson counts 0,1,2,0,3 and a Gamma(2,1) prior under the shape/rate convention. Its posterior is Gamma(8,6), with mean 8/6 and variance 8/36. That exact target provides a tractable oracle for comparing parameterizations.

The program deliberately contains two independent copies of this posterior. One uses a declared positive rate lambda. The other uses an unconstrained z with rate \(\exp(z)\). They are computational replicas for a comparison; they are not two separate pieces of evidence to multiply onto a single rate parameter.

## Worked case 1: use a declared positive rate

The first parameter is `real<lower=0> lambda`. Its prior and likelihood are expressed directly on the positive rate scale. Stan handles the internal constrained-to-unconstrained parameter transform. Adding another `log(lambda)` merely because the declaration is positive would generally double-count a transformation term.

The generated quantities calculate the exact posterior moments. Those constant rows have undefined sampling diagnostics, as explained in the first Stan unit. The sampled lambda row is the relevant object for checking actual exploration and agreement with the analytic distribution.

A gamma rate and scale are inverses, so parameter conventions must be stated. Changing from rate one to scale one happens to leave the same numeric value in this fixture; other values would not. A robust test should therefore understand the formula rather than infer the convention from a single convenient number.

## Worked case 2: introduce an unconstrained log rate

For the manual coordinate, \(\lambda=\exp(z)\) and \(d\lambda/dz=\exp(z)\). The target density written with respect to z therefore contains

\[
\log p_\Lambda(\exp z)+z+\log p(y\mid\exp z).
\]

The code includes the `+ z` term explicitly. Its `lambda_from_z` output should have the same target marginal distribution as the directly constrained lambda. Finite sampled means need not be identical, so comparison should use Monte Carlo precision and the exact moments rather than equality of every output digit.

Omitting the Jacobian samples a different target. A sampler could explore it efficiently and report attractive diagnostics. The earlier quadrature example showed that such a mistake can be exposed through an independent moment calculation even when normalization and trace appearance seem plausible.

## Review the intended probability measure

A deterministic function calculated only for reporting does not itself require a target adjustment. The adjustment is required when the density is re-expressed in different variables. Distinguish a transformed parameter that receives its density through an underlying correctly modeled variable from a manually transformed variable whose density is assigned on another scale.

Dimensions matter in multivariate transforms. A componentwise log transform contributes a sum of log-Jacobian terms; a more general transformation requires the determinant of the relevant derivative matrix. Treating every transform as a scalar log term can fail even when the code compiles.

The two replicas here are intentionally independent conditional targets. Their posterior difference is a computational diagnostic, not a new scientific parameter. Do not combine their samples as if they represented independent new datasets or multiply their evidence values to strengthen a claim about the same observations.

## Answered scientific discussion

**Can a compiler detect a missing Jacobian?** It can sometimes warn about suspicious transformed sampling statements, but syntactically valid target increments can still encode the wrong density. A derivation and an independent reference case remain necessary.

**Why compare two parameterizations inside one tiny program?** It makes the target relationship explicit and keeps data and priors identical. The exact gamma posterior provides a stronger check than visual similarity between two short histograms. In an ordinary analysis, select a justified parameterization and retain its mathematical explanation.

## Complete reproducible program

The prepared Stan pad compiles and samples `main.stan` with fixed bounded settings. Its tiny data are declared in `transformed data`; this pad has no separate JSON editor. The linked project explains standard data-block workflows. Runtime: `stan-cpu`.

```stan
// Two independent copies of one posterior compare parameterizations.
transformed data {
  int N = 5;
  array[N] int y = {0, 1, 2, 0, 3};
  real prior_shape = 2;
  real prior_rate = 1;
}
parameters {
  real<lower=0> lambda;
  real z;
}
model {
  // Declared constraints have their internal Jacobian handled by Stan.
  lambda ~ gamma(prior_shape, prior_rate);
  y ~ poisson(lambda);
  // The manually introduced log-rate transform needs its own Jacobian.
  target += gamma_lpdf(exp(z) | prior_shape, prior_rate) + z;
  target += poisson_lpmf(y | exp(z));
}
generated quantities {
  real lambda_from_z = exp(z);
  real exact_posterior_mean = (prior_shape + sum(y)) / (prior_rate + N);
  real exact_posterior_variance = (prior_shape + sum(y)) / square(prior_rate + N);
}
```

## Primary references

- [Stan change-of-variable accounting](https://mc-stan.org/docs/stan-users-guide/reparameterization.html)
