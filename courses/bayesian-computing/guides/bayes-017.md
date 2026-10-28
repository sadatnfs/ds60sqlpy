# bayes-017: Stan blocks and a conjugate reference model

Tutorial mode. Stage: advanced. Direct prerequisites: `bayes-003`, `bayes-009`.

## A Stan program defines a log density

Stan is a probabilistic programming language whose compiler translates a model into an executable used by inference algorithms. A model file is not a script that repeatedly assigns observed values to unknown parameters. Its declarations and model statements define a target density over unknown quantities conditional on supplied data.

The classroom stages a complete `main.stan` file, compiles it using the prepared CmdStan toolchain and runs two bounded seeded chains. Each has 100 warmup and 100 retained draws, with target acceptance .9. Tiny constants live in `transformed data` because this single-source pad has no separate JSON input editor. The linked external project demonstrates the standard data-block workflow without changing that classroom contract.

## Worked case 1: connect blocks to a conjugate oracle

`transformed data` declares five measurements, a prior mean of zero, prior standard deviation two and known observation standard deviation one. These values are fixed before sampling. `parameters` declares the unknown mean mu. The `model` block adds its normal prior and the normal observation likelihood. A vectorized sampling statement is a concise density contribution, not a command to replace the observed data with random values.

The exact posterior has precision \(1/4+5=21/4\), variance 4/21 and mean 40/21. The `generated quantities` block calculates those analytic constants alongside a posterior predictive observation and per-observation log likelihood. Their agreement with the sampling result should be assessed using Monte Carlo precision, not an assertion that a random sample mean equals an exact fraction.

The generated predictive observation includes observation variation around mu. The posterior spread of mu instead describes uncertainty about the mean. Confusing those two outputs can produce an interval that is much too narrow for a future measurement.

## Worked case 2: interpret constant and sampled diagnostic rows

The analytic posterior mean and variance are constants across draws. Their between- and within-chain variation is zero, so R-hat or effective-size diagnostics for those generated constants can be undefined. That is different from an unexpectedly constant chain for the sampled mu parameter.

Very fast chains can also have elapsed times rounded to zero in a summary. An infinite ESS-per-second entry then reflects timing resolution, not infinite computational efficiency. Inspect retained counts, time precision and parameter diagnostics rather than treating every numeric summary as a scientifically meaningful ratio.

The runner displays actual summaries and trace artifacts when available. Those are records of the execution, not a convergence certificate. The 100-draw demonstration can expose diagnostic limitations and should not be relabeled as a fully qualified production posterior simply because compilation and sampling returned successfully.

## Learn the block boundaries

A standard `data` block declares externally supplied inputs with type and constraint checks. `transformed data` can derive fixed values once. `parameters` defines unknowns; `transformed parameters` defines deterministic functions of those unknowns that participate in model calculations. The `model` block accumulates log density. `generated quantities` calculates retained-draw outputs and supports random-number generation for predictions.

The same arithmetic placed in different blocks can have different computational cost and allowed operations. A random-number generator belongs in an appropriate generated-data context, not in a deterministic log-density evaluation used by Hamiltonian dynamics. File includes, arbitrary compiler flags and a second data document are outside this pad's contract.

Compilation success establishes syntactic and type validity. Sampling success establishes that an execution occurred under the fixed settings. Neither establishes that the model's scientific assumptions are appropriate or that every posterior quantity has adequate Monte Carlo precision. Retain those distinctions when describing the result.

## Answered scientific discussion

**How is this related to the earlier normal-normal calculation?** The statistical target is the same. The exact formula supplies an oracle for a real compiled inference path, allowing implementation and computation to be checked independently of a complex model.

**How should data be handled in a larger project?** Use a reusable data block, a validated data file or interface object, explicit model/data hashes and retained output artifacts. See the [normal-mean project](../projects/normal-mean/README.md) for a complete example. That optional workflow requires its own prepared environment and does not imply hidden classroom file-upload features.

## Complete reproducible program

The prepared Stan pad compiles and samples `main.stan` with fixed bounded settings. Its tiny data are declared in `transformed data`; this pad has no separate JSON editor. The linked project explains standard data-block workflows. Runtime: `stan-cpu`.

```stan
// A self-contained classroom model. External project uses a separate data block.
transformed data {
  int N = 5;
  vector[N] y = [1.0, 1.5, 2.0, 2.5, 3.0]';
  real prior_mean = 0;
  real prior_sd = 2;
  real observation_sd = 1;
}
parameters {
  real mu;
}
model {
  mu ~ normal(prior_mean, prior_sd);
  y ~ normal(mu, observation_sd);
}
generated quantities {
  real y_rep = normal_rng(mu, observation_sd);
  real posterior_variance = inv(inv_square(prior_sd) + N / square(observation_sd));
  real posterior_mean = posterior_variance
                        * (prior_mean / square(prior_sd) + sum(y) / square(observation_sd));
  vector[N] log_lik;
  for (n in 1 : N)
    log_lik[n] = normal_lpdf(y[n] | mu, observation_sd);
}
```

## Primary references

- [Stan language reference](https://mc-stan.org/docs/reference-manual/)
- [CmdStan sampling configuration](https://mc-stan.org/docs/cmdstan-guide/mcmc_config.html)
