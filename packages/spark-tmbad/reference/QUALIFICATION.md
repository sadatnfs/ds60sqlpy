# Qualification status

The optional reference has passed native Linux ARM64 dependency/template
preparation and all 24 registered serial modeling cases. The exact preparation
manifest and unmodified case reports are retained in
[the qualification index](qualification/index-v2.json). The
[earlier case index](qualification/index.json) remains unchanged. This used an explicitly
prepared system-package base, followed by installation of the complete locked
R dependency closure and compilation of the four original templates. It does
not qualify a different default Docker base or another architecture.

The accepted source refresh verified the original preparation manifest, recorded
package and native-library hashes, all locked source archives, installed versions
and R/platform identities. It copied unchanged dependencies/templates into a
fresh directory, admitted only explicit R-controller/test changes, and ran R
parsing and pure checks. The old manifest remains preserved in the refresh's
provenance. Additional hashes for every copied file are fresh observations;
they are not misrepresented as historical preparation hashes. No dependency
installation or compilation occurred during source refresh or model execution.

## Actual accepted cases

| Scope | Cases and evidence |
| --- | --- |
| Custom TMB | Gaussian ridge, correlated random slope, nonlinear growth, panel AR(1) |
| Regularization/posterior | Exact selected L1/KKT, Gaussian prior MAP, proper conjugate Gaussian posterior and predictive moments |
| Upstream families | Gaussian, Poisson, NB1, NB2, beta, beta-binomial, Gamma, Student-t, lognormal |
| Zero components | Zero-inflated and hurdle negative-binomial fits with separate zero/dispersion predictors |
| Upstream covariance | AR(1), OU, compound symmetry, diagonal, Toeplitz, unstructured |
| Upstream MAP/forecast | Nonzero-mean Gaussian coefficient prior MAP and conditional AR(1) forecasting |

Each case retains its seed, synthetic fixture hash, prepared-manifest hash,
parameters, diagnostic checks, numerical references and prediction or forecast
interpretation. The custom tests include independent density/derivative checks,
quadrature comparisons where declared, and restoration of TMB's mutable latent
state. Upstream simulations preserve beta-binomial success/failure matrix shape.
These case results are execution and numerical evidence. They are not a claim of
uniform estimator calibration, a generic posterior sampler, or a native TMBad
implementation of upstream glmmTMB.

The held-out forecast extension also completed sixteen independent datasets each
for nonlinear growth, the custom panel model and the upstream AR(1) model. The
original training values and fitted parameters were checked unchanged. Future
observations are generated afterward with a separate seed stream and never enter
the fit or response-free prediction inputs. The nonlinear interval uses a normal
quantile and mixture standard deviation; it is not an exact mixture quantile.

| Scenario | Successful datasets | Held-out prediction MSE (MCSE) | Pointwise coverage (dataset MCSE) |
| --- | --- | --- | --- |
| Nonlinear new group | 16/16 | 0.222 (0.077) | 0.938 (0.063) |
| Custom panel conditional forecast | 16/16 | 0.136 (0.028) | 0.958 (0.028) |
| Upstream latent AR(1) conditional forecast | 16/16 | 0.287 (0.065) | 1.000 (0.000 observed) |

Each dataset contributes one average across its correlated future observations;
future rows are not counted as independent replications. A zero empirical MCSE
in this small sample does not establish certain coverage. These are bounded
simulation checks, not a calibration guarantee. Two fixed-training-data posterior
draw checks separately confirm that the aggregator withholds dataset MCSE and
failure-rate intervals when only posterior draws change.

An [earlier seven-scenario, sixteen-repetition batch](qualification/historical-simulations.json) retained two Gaussian
random-slope solver line-search failures despite small gradients. They remain
failed fits. Its deterministic regularization case repeated the same dataset;
the corrected derived analysis withholds independent-dataset MCSE for that case.
The original ledgers and old summaries were preserved rather than rewritten.

## Retained failures and repairs

The first installation failed while compiling Matrix 1.7-4 against R 4.6.1.
The exact source DESCRIPTION files showed that earlier index-derived version
restrictions were wrong. The corrected lock uses compatible recommended-package
archives, including Matrix 1.7-6, and verifies their metadata before installation.
The failed build and logs remain historical failures.

The first serial case pass had 9 successes and 15 failures. Eight failures were
serialization of glmmTMB's S3 coefficient object; coefficients now have explicit
component names, parameter names and numeric values. Serialization failure itself
now produces a failed result instead of leaving no case receipt.

Seven cases failed optimizer status or score admission despite positive curvature.
The custom route retains its first nlminb attempt and, when necessary, runs a
bounded L-BFGS-B refinement of the same objective and bounds. The upstream route
uses glmmTMB's supported optimizer control to build a complete BFGS refit, keeping
its latent state and sdreport consistent. It never patches only the fitted vector.
All original attempts and warnings remain visible. The first custom refinement
still stopped on relative function reduction too early; tightening that stopping
condition resolved the remaining two cases. The original projected-score,
upstream score, finite-value, optimizer-status and positive-curvature gates were
not relaxed.

## Evidence still required for other claims

The independent directory and prepared-source copies execute without a classroom
checkout. A neutral default-base Docker build, AMD64, Spark/multiple-machine
execution of this optional reference, and arbitrary upstream formula compatibility
remain separate unqualified scopes. Repeated studies retain failed fits and
compute Monte Carlo uncertainty; a few repetitions do not establish calibration.
Read each study's complete ledger and denominator rather than inferring a study
result from the single-seed case matrix.
