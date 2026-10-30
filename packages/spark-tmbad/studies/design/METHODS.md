# Simulation methods and evidence contract

A study begins with a scientific question, an estimand, a data-generating process,
a fitting target and an evaluation protocol. A successful optimizer status alone
is none of those. Every record states the optimized coordinates, likelihood
normalization, weight interpretation, penalty placement, parameter bounds,
initialization rule and scientific independence unit.

## Shared original fixtures

A fixture is indexed by study, scenario, replicate and split. Random streams for
covariates, latent effects, observation noise and future innovations are separate.
Changing the number of forecast rows must not change the training sample. Adding
a new method must not regenerate a different dataset. Both packages consume the
same canonical retained JSON bytes and report their SHA256, rather than merely
using an apparently similar random seed in two different libraries.

The initial fixture generator is bounded and runs outside Spark. Its synthetic
values are therefore already available to an independent serial oracle. This is
not evidence that the packages collect real training observations onto the driver.
Spark receives explicit SQL fixtures for small smoke cases; a later scale study
uses a separately materialized immutable dataset with a retained source receipt.
No study reads historical application databases or downloads data inside a fit.

## Targets and units

For independent rows, the data target is

\[
 L(\theta)=\sum_i w_i\ell_i(\theta).
\]

For independent complete units, the unit marginal or joint loss replaces the row
term and its weight applies once. Shared parameter estimation sums these losses;
independent fits estimate a different vector for each group. Neither operation
permits splitting a coupled latent covariance across independent partitions.

The current L2 convention adds \(\lambda\|\theta\|^2/2\) once after the selected
sum or weighted-mean reduction. Under a summed likelihood this is a normal prior
on those optimization coordinates, up to constants relevant to point estimation.
It may penalize an intercept and log-scale. A selected-coefficient prior, a prior
on a positive scale, and a survey-weighted pseudo-likelihood are different targets.
See [the prior study](../guides/priors-and-parameterization.md).

## Smoke versus Monte Carlo

A smoke preset exercises a few fixed replicates, exact small-case oracles,
invalid support, partition/weight contracts and report generation. Its purpose is
to reveal coding mistakes. It cannot establish estimator coverage, robustness,
consistency, cluster scaling or performance superiority.

A larger Monte Carlo experiment fixes the scenario grid and replication count
before examining results. For estimates \(\hat\theta_r\) from independent
successful replications, report the conditional bias estimate and its Monte Carlo
standard error:

\[
 \widehat{\mathrm{bias}}=\overline{\hat\theta}-\theta_0,
 \qquad \operatorname{MCSE}(\widehat{\mathrm{bias}})
 =s_{\hat\theta}/\sqrt{R_{\mathrm{success}}}.
\]

For squared errors \(q_r\), estimate MSE as their average and use
\(s_q/\sqrt{R_{\mathrm{success}}}\) for its MCSE. RMSE is a transformed summary;
state whether its uncertainty uses a delta approximation or a replicate-level
bootstrap. A method comparison on shared simulated data uses paired replicate
loss differences, whose MCSE is the sample SD of those differences divided by
\(\sqrt R\), rather than pretending methods saw independent datasets.

For a coverage indicator, the binomial MCSE is
\(\sqrt{\hat p(1-\hat p)/R}\). Around 95% coverage, 2000 independent replicates give
an MCSE near 0.0049. A handful of smoke runs cannot distinguish 94% from 96%.
For a zero observed failure count, do not report an estimated failure rate of
exactly zero without uncertainty; include a binomial interval or an explicit
upper-bound calculation. Correlated rolling origins are not independent Monte
Carlo replications. Aggregate within a generated dataset before estimating MCSE
across independently generated datasets.

## Keep failures in the study

A failed fit produces a record with its stage, declared category, source/runtime
identity and elapsed time. It is not dropped or replaced by a more favorable
seed. Report failure proportion over all attempted replications. Bias/RMSE among
returned estimates is explicitly conditional on success. Report both interval
coverage conditional on a returned interval and procedural coverage over all
attempted replications, where no reported interval is a failure to cover.

Validate finite objective/parameters, raw and projected score, bounds, meaningful
curvature when used, and independent numerical oracles. A small loss change with
a large score is stalling. A numerical candidate rejection is distinct from an
invalid initial dataset, transport failure or incompatible artifact. Initial
failures and unreviewed backend failures remain failures, not silently successful
simulations. Multiple starts use a predetermined training-objective selection
rule and retain every attempt; holdout outcomes never select the start.

## Honest uncertainty

Record separately: observation noise, future process innovations, conditional
latent-effect uncertainty, and fixed/population-parameter uncertainty. The law of
total variance is

\[
 \operatorname{Var}(Y_*\mid D)=
 E_{\theta\mid D}[\operatorname{Var}(Y_*\mid\theta,D)]
 +\operatorname{Var}_{\theta\mid D}[E(Y_*\mid\theta,D)].
\]

Plug-in predictions omit the second term. A native random-effect Laplace integral
approximates integration over latent effects to produce a marginal likelihood.
A Gaussian approximation to a fixed-parameter posterior is a separate operation,
requiring an actual prior and appropriate posterior curvature. Neither is MCMC.
An exact conjugate posterior reference is genuine posterior inference under its
stated model, but does not mean either distributed package supplies a generic
posterior sampler.

## Backtesting and model selection

Split by time before fitting transformations, lag features, hyperparameters or
models. A rolling origin can use only observations and covariates available at
that origin. Keep outer forecast assessment separate from inner tuning origins.
A known-group test conditions on the group's observed prefix; an unseen-group
test excludes that group's entire history from parameter fitting and conditioning.
Store split IDs and actual input availability, not just a random seed.

For cluster bootstrap, resample complete independent units. Repeated bootstrap
copies receive distinct unit and observation identities; merging them under the
same latent-group key changes the likelihood. Pointwise interval coverage and
whole-path coverage are different metrics. See
[the forecast study](../guides/forecast-conditioning-and-coverage.md).

## Runtime and reproducibility

Each result binds fixture SHA, study source SHA, package versions and installed
source identities, prepared native/JVM identities where applicable, architecture,
partition count, thread settings, optimizer settings and seed keys. Numerical
oracles, actual library execution, real Spark tasks, CPU timing, multi-node timing
and GPU timing remain distinct evidence. Reusing a completed exact-identity record
is a checkpoint operation, not a new experiment. Changed inputs or artifacts need
new records; immutable prior evidence is retained.

CI should run source checks and bounded smoke cases, not automatically launch
thousands of Monte Carlo fits. Large runs need explicit resource selection and a
retained completion/failure ledger. Report performance only with warmup policy,
backend/version details, repeated timings and the same scientific target.
