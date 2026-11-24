# bayes-017: Stan blocks and a conjugate reference model

Tutorial mode. Stage: advanced. Direct prerequisites: `bayes-003`, `bayes-009`.

## A Stan program defines a log density

Stan is a probabilistic programming language whose compiler translates a model into an executable used by inference algorithms. A model file is not a script that repeatedly assigns observed values to unknown parameters. Its declarations and model statements define a target density over unknown quantities conditional on supplied data.

The classroom stages a complete `main.stan` file, compiles it using the prepared CmdStan toolchain and runs two bounded seeded chains. Each has 100 warmup and 100 retained draws, with target acceptance .9. Tiny constants live in `transformed data` because this single-source pad has no separate JSON input editor. The linked external project demonstrates the standard data-block workflow without changing that classroom contract.

## Key terms

- **Stan program:** A declaration of a log density over unknowns, compiled by CmdStan into an executable for inference.
- **Transformed data block:** A block for constants computed once before sampling, used here because the pad has no separate data input.
- **Model block:** The block that adds prior and likelihood terms to the target log density.
- **Generated quantities block:** A block evaluated after each draw for predictions, log likelihoods and derived values that do not affect sampling.

## Worked case 1: connect blocks to a conjugate oracle

`transformed data` declares five measurements, a prior mean of zero, prior standard deviation two and known observation standard deviation one. These values are fixed before sampling. `parameters` declares the unknown mean mu. The `model` block adds its normal prior and the normal observation likelihood. A vectorized sampling statement is a concise density contribution, not a command to replace the observed data with random values.

The exact posterior has precision \(1/4+5=21/4\), variance 4/21 and mean 40/21. The `generated quantities` block calculates those analytic constants alongside a posterior predictive observation and per-observation log likelihood. Their agreement with the sampling result should be assessed using Monte Carlo precision, not an assertion that a random sample mean equals an exact fraction.

The generated predictive observation includes observation variation around mu. The posterior spread of mu instead describes uncertainty about the mean. Confusing those two outputs can produce an interval that is much too narrow for a future measurement.

## Worked case 2: interpret constant and sampled diagnostic rows

The analytic posterior mean and variance are constants across draws. Their between- and within-chain variation is zero, so R-hat or effective-size diagnostics for those generated constants can be undefined. That is different from an unexpectedly constant chain for the sampled mu parameter.

The classroom pad runs two chains with 100 warmup and 100 retained draws each. For sampled parameters such as `mu`, apply the screen from the Markov chain unit: `R_hat` below 1.01, `ESS_bulk` and `ESS_tail` of at least about 100 per chain and no divergent transitions. Two chains of 100 draws can fail it even for this conjugate model, so the run demonstrates the workflow rather than a reportable fit.

Very fast chains can also have elapsed times rounded to zero in a summary. An infinite ESS-per-second entry then reflects timing resolution, not infinite computational efficiency. Inspect retained counts, time precision and parameter diagnostics rather than treating every numeric summary as a scientifically meaningful ratio.

The runner displays actual summaries and trace artifacts when available. Those are records of the execution, not a convergence certificate. The 100-draw demonstration can expose diagnostic limitations and should not be relabeled as a fully qualified production posterior simply because compilation and sampling returned successfully.

## Learn the block boundaries

A standard `data` block declares externally supplied inputs with type and constraint checks. `transformed data` can derive fixed values once. `parameters` defines unknowns; `transformed parameters` defines deterministic functions of those unknowns that participate in model calculations. The `model` block accumulates log density. `generated quantities` calculates retained-draw outputs and supports random-number generation for predictions.

The same arithmetic placed in different blocks can have different computational cost and allowed operations. A random-number generator belongs in an appropriate generated-data context, not in a deterministic log-density evaluation used by Hamiltonian dynamics. File includes, arbitrary compiler flags and a second data document are outside this pad's contract.

Compilation success establishes syntactic and type validity. Sampling success establishes that an execution occurred under the fixed settings. Neither establishes that the model's scientific assumptions are appropriate or that every posterior quantity has adequate Monte Carlo precision. Retain those distinctions when describing the result.

## Answered scientific discussion

**How is this related to the earlier normal-normal calculation?** The statistical target is the same. The exact formula supplies an oracle for a real compiled inference path, allowing implementation and computation to be checked independently of a complex model.

**How should data be handled in a larger project?** Use a reusable data block, a validated data file or interface object, explicit model/data hashes and retained output artifacts. See the [normal-mean project](../projects/normal-mean/README.md) for a complete example. That optional workflow requires its own prepared environment and does not imply hidden classroom file-upload features.

## Worked example: Conjugate oracle, Monte Carlo error and a constant row

```python
import numpy as np

y = np.array([4.1, 5.3, 3.8, 4.9, 5.6, 4.4])
sigma, m0, s0 = 1.0, 0.0, 10.0  # matches normal(0, 10) prior, known sigma
prec = 1 / s0**2 + len(y) / sigma**2
post_mean = (m0 / s0**2 + y.sum() / sigma**2) / prec
post_sd = np.sqrt(1 / prec)
print(f"posterior mean {post_mean:.4f}, sd {post_sd:.4f}")
for ess in (100, 400, 1600):
    print(f"bulk ESS {ess:>4}: MCSE of mean {post_sd / np.sqrt(ess):.4f}")

n_obs = np.full((4, 1000), 6.0)  # a transformed-data value copied into every draw
W = n_obs.var(axis=1, ddof=1).mean()
with np.errstate(invalid="ignore", divide="ignore"):
    print("within-chain variance", W, "R-hat ratio", np.sqrt((W + 0.0) / W))
```

Observed output:

```text
posterior mean 4.6755, sd 0.4079
bulk ESS  100: MCSE of mean 0.0408
bulk ESS  400: MCSE of mean 0.0204
bulk ESS 1600: MCSE of mean 0.0102
within-chain variance 0.0 R-hat ratio nan
```

This check copies the structure of the unit's Stan program, a normal prior on the mean and a normal likelihood with known scale 1, with a wider normal(0, 10) prior and its own six observations, so the sampled mean has a closed-form target. The six observations summing to 28.1 give precision \(0.01+6=6.01\), posterior mean \(28.1/6.01=4.6755\) and standard deviation 0.4079. That reference turns diagnostics into checkable claims. With a bulk effective sample size of 400 the Monte Carlo standard error is \(0.4079/20=0.0204\), so a reported mean between roughly 4.63 and 4.72 is consistent with the oracle and 4.80 would not be. Quadrupling ESS only halves that error. The last line explains rows in the Stan summary that look broken. A value set in transformed data, like the number of observations, is identical in every draw; its within-chain variance is 0.0, and the R-hat ratio becomes \(0/0\), printed as nan. That row is not a convergence failure. It is a constant, and the summary simply has no variability to measure.

## Complete reproducible program

The prepared Stan pad compiles `main.stan` and samples two chains with 100 warmup and 100 retained draws each. Its tiny data are declared in `transformed data`; this pad has no separate JSON editor. The linked project explains standard data-block workflows. These teaching-sized chains can fail the convergence screen from `bayes-006` (R-hat below 1.01, at least 100 bulk and tail effective draws per chain, no divergences); read the printed diagnostics against it before interpreting any estimate. Runtime: `stan-cpu`.

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
