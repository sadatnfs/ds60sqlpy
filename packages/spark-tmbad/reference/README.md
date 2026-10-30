# Optional R/TMB/glmmTMB reference project

This is an explicitly optional, serial reference environment. It uses the real
R packages TMB and glmmTMB and four original prepared C++ likelihood templates.
The primary Spark/TMBad package remains independent of R. This project is not a
native port of glmmTMB, an arbitrary formula-to-Spark compiler, or distributed
posterior inference.

The complete directory can be copied independently. It contains its own locked
dependencies, Dockerfile, source preparation, R API, bounded Python driver,
synthetic examples, numerical references and tests. It imports no classroom
checkout. Read [source/dependency notices](NOTICE.md) before distributing a
prepared image. The upstream glmmTMB dependency is AGPL-3 and retains its exact
pinned source and license; original glue is MIT.

## Prepare once, then run offline

The default targets R 4.6.1, TMB 1.9.25, RTMB 2.0 and glmmTMB development 1.1.15.9000
at commit `1db3b4692aa4c61ae5c9974b32b9f91555cf5f2c`. The lock contains the full
65-package CRAN closure. Recommended-package pins match the previously qualified
R 4.6.1 environment, including Matrix 1.7-6. Every dependency declaration is
checked against the exact source archive's DESCRIPTION before installation;
package-index metadata alone does not establish source compatibility.
The library is installed into its own directory; existing R/classroom libraries
are not replaced. Dependency and C++ preparation are serial.

From this directory on an engine with permitted image access:

```sh
docker build --tag spark-tmb-reference:0.1.0 .
docker run --rm --network none spark-tmb-reference:0.1.0 --list
```

Image preparation installs the locked dependencies and compiles the four
registered templates. It does not prove every model/example or platform has
passed numerical acceptance. `R_BASE_IMAGE` is an explicit prepared-image
override. `PREPARED_OS_PACKAGES=1` skips apt only when the selected base already
has the declared system dependencies. It does not disable source verification,
R package installation or template compilation.

For a separately prepared R environment, use a fresh destination:

```sh
python3 prepare.py --output /absolute/path/to/prepared --allow-download
```

For offline preparation, populate a directory with the exact archives named in
`dependencies.lock.json` and omit download authorization:

```sh
python3 prepare.py --archives /absolute/path/to/archives \
  --output /absolute/path/to/fresh-prepared
```

The glmmTMB archive filename is `glmmTMB-REVISION.tar.gz`, using the full pinned
revision. All input hashes are verified before installation. Full CRAN/upstream
source archives and complete compressed build logs are retained. A preparation
failure never creates a successful manifest or replaces an existing prepared
installation. Source changes require fresh preparation and qualification.

## Work through concrete examples

The Python driver accepts registry identifiers and bounded data-only options.
It never deserializes executable model text or compiles/downloads at runtime.
With this source and the separately prepared environment:

```sh
python3 python/client.py --case gaussian_ridge --seed 1729 \
  --prepared /absolute/path/to/prepared --output /absolute/path/to/ridge-run
python3 python/client.py --case glmm_family --option family_name=nbinom2 \
  --seed 1729 --prepared /absolute/path/to/prepared --output /absolute/path/to/nb2-run
python3 python/client.py --case glmm_covariance --option structure=ar1 \
  --seed 1729 --prepared /absolute/path/to/prepared --output /absolute/path/to/ar1-run
python3 python/client.py --case panel_ar1 --seed 1729 \
  --prepared /absolute/path/to/prepared --output /absolute/path/to/panel-run
```

Use fresh output paths. In Docker, mount an explicitly owned output directory
and use `/opt/reference-prepared` as the prepared path. The driver uses a separate
R process, retains stdout/stderr, bounds run time/results and kills only its own
process group on timeout. A failed result is retained as failure.

| Case | Actual code path and numerical check |
| --- | --- |
| `gaussian_ridge` | Prepared TMB Gaussian likelihood, selected nonzero-mean slope prior, fixed noise scale, analytic ridge/MAP solution and two-step gradient check |
| `gaussian_random_slope` | Prepared correlated random intercept/slope model; TMB Laplace compared with exact dense Gaussian marginal likelihood and BLUP conditioning |
| `nonlinear_growth` | Prepared saturating growth with Gaussian log-amplitude effects; conditional-mode versus integrated new-group means and a numerical quadrature contrast |
| `panel_ar1` | Original exact Gaussian panel model with fixed trend/covariates, random intercept/slope, observed AR1 residuals and time-varying scale; independent dense likelihood and future conditional moments |
| `regularization_posterior` | Exact Gaussian lasso coordinate descent/KKT, orthogonal soft-threshold oracle, proper conjugate coefficient posterior and independent posterior draws |
| `glmm_family` | Real upstream Gaussian, Poisson, NB1, NB2, beta, beta-binomial, Gamma, Student-t or lognormal fit/predict/simulate; explicit family option required |
| `glmm_zero_inflation` / `glmm_hurdle` | Real upstream NB2 or zero-truncated NB2 with distinct zero and dispersion models; verifies response mean decomposition |
| `glmm_map` | Real upstream coefficient priors checked against an independent logistic MAP objective |
| `glmm_covariance` | Real upstream AR1, OU, CS, diagonal, Toeplitz or unstructured covariance; explicit structure option, positive-definite result, no redundant free residual diagonal |
| `glmm_ar_forecast` | Real latent-AR1-plus-measurement-noise fit, followed by an explicitly independent Gaussian conditional forecast calculation |

These entries describe implemented source, not completed execution receipts.
Consult [qualification status](QUALIFICATION.md) for the actual observed checks.
Other upstream families/covariances remain available through the ordinary
trusted R glmmTMB API; their presence upstream does not qualify every combination
in this project or add them to the primary native registry.

## Use the standalone R API

Set `R_LIBS_USER` and `R_LIBS_SITE` to the prepared `library` directory before
starting R. Source `R/common.R`, then create a checked engine:

```r
source("R/common.R")
engine <- reference_engine(normalizePath("."), "/absolute/path/to/prepared")
X <- cbind(1, seq(-1, 1, length.out = 20))
y <- as.numeric(X %*% c(1, 0.5)) + rep(c(-0.1, 0.1), 10)
objective <- reference_objective(
  engine, "gaussian_linear",
  list(X = X, y = y, prior_center = c(0, 0), prior_precision = c(0, 2)),
  list(beta = c(0, 0), log_sigma = log(0.2)),
  map = list(log_sigma = factor(NA))
)
fit <- reference_fit(objective)
fit$diagnostics
```

These are trusted live R data/parameter objects. The prepared registry and binary
hashes are checked before loading. The data-only Python request surface exposes
only the maintained cases and enumerated options. To add a custom template,
write original source, add its declared registry/admission contract, prepare a
fresh artifact and qualify it before use. Do not put executable R/C++ text into
a saved model document.

## Simulations and uncertainty

```sh
python3 python/simulate.py --case gaussian_random_slope --replications 3 \
  --seed 1729 --time-budget 600 --prepared /absolute/path/to/prepared \
  --output /absolute/path/to/fresh-study
```

This smoke runs independent generated datasets with deterministic seeds. It
retains every failed attempt, reports successful/attempted counts, conditional
parameter bias/MSE and MCSE, and a Wilson failure-rate interval. Where available,
pointwise forecast coverage is averaged within each dataset before estimating
MCSE across datasets. Three repetitions cannot establish calibration. Larger
runs require an explicit replication count and time budget; incomplete runs are
marked incomplete rather than silently extended or relabeled.

Read [likelihoods and forecasts](docs/MODELS.md) and
[priors and simulation interpretation](docs/INFERENCE.md). Random-effect
integration can produce marginal ML. Priors plus optimization produce MAP.
Neither automatically supplies a posterior over population parameters. The
conjugate Gaussian example is a genuine exact posterior reference with known
noise scale, separate from the MAP and random-effect Laplace examples.
