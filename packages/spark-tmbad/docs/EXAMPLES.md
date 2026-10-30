# Model example gallery

The gallery has a complete Spark DataFrame fitting, prediction and forecasting
example for every one of the 14 prepared native models. Each model has a Python
entrypoint and uses the same public fixture format as the Scala gallery. This
is coverage of the prepared registry. The TMB course also teaches R/TMB APIs
and model families that have a different runtime or are not implemented here;
the mapping below makes those boundaries explicit.

Each Python script takes a prepared manifest, fits an immutable SQL `VALUES` DataFrame,
saves and reloads source-bound model JSON, then evaluates every illustrated
prediction and forecast target. It compares the small returned tables with
independent formulas at the fitted parameters. It never collects training data
or all group models from a cluster to the Python driver. The fixtures are small,
public synthetic data, generated before execution and checked into source.
They use a fixed random seed and 12 significant digits of canonical precision,
so insignificant macOS/Linux math-library rounding does not change the fixture
bytes.

## Run one model or the entire gallery

After [runtime preparation](PREPARATION.md), run one Python example:

```sh
spark-submit --master 'local[2]' \
  --jars /opt/spark-tmbad/spark-tmbad.jar \
  python/examples/gallery/normal.py \
  --manifest /opt/spark-tmbad/artifact.json \
  --output /owned/example-results/normal-run
```

The output directory must be new. It contains the fitted model and an execution
report with parameters, convergence diagnostics, target descriptions, projected
tables, formula checks, artifact identity and source hashes. Without `--output`,
the script uses a temporary directory, verifies the JSON round trip, prints its
report and removes its own temporary files.

Run all models with the shared runner:

```sh
spark-submit --master 'local[2]' \
  --jars /opt/spark-tmbad/spark-tmbad.jar \
  python/examples/gallery/run_gallery.py \
  --manifest /opt/spark-tmbad/artifact.json \
  --model all --output /owned/example-results/all-models
```

The full run requires the gallery and prepared registry to contain the same
model IDs. It fails on missing models, failed optimization, lost row identities
or numerical disagreement. It does not turn missing capabilities into skips.
Unconverged fits retain diagnostics and model JSON but withhold prediction and
forecast evaluation. The examples never use `allow_unconverged` to pass a check.

The corresponding Scala entrypoint is
`io.ds60.spark.tmbad.examples.ModelGallery`, in
[ModelGallery.scala](../jvm/src/main/scala/io/ds60/spark/tmbad/examples/ModelGallery.scala).
It consumes the same [fixtures.json](../python/examples/gallery/fixtures.json).
It checks convergence, every declared target, finite outputs and row identities.
Python gallery and native oracle runs perform the independent formula comparisons.
For example:

```sh
spark-submit --master 'local[2]' \
  --class io.ds60.spark.tmbad.examples.ModelGallery \
  /opt/spark-tmbad/spark-tmbad.jar \
  /opt/spark-tmbad/artifact.json python/examples/gallery/fixtures.json normal
```

Scala source availability and execution status are tracked separately in the coverage
file; a Python run does not prove that the Scala entrypoint ran.

## Row likelihoods and future observations

These models factor by independent row. Their `response` prediction and forecast
targets take the listed predictors and empty history. Forecasting here means
future observations at supplied predictors. It does not introduce a time-series
dependence that the likelihood did not contain.

| Model guide with Python and Scala calls | Fitted response model | Target inputs | Returned moments |
| --- | --- | --- | --- |
| [normal](models/normal.md) | Gaussian mean and standard deviation | none | mean, sd |
| [linear_gaussian](models/linear_gaussian.md) | Gaussian linear mean in x | x | mean, variance, sd |
| [quadratic_gaussian](models/quadratic_gaussian.md) | Gaussian mean with an x-squared term | x | mean, variance, sd |
| [poisson_exposure](models/poisson_exposure.md) | Poisson count with log-linear rate and exposure | x, exposure | expected count, count variance, sd |
| [bernoulli_logistic](models/bernoulli_logistic.md) | Binary response with logistic probability | x | probability, Bernoulli variance, sd |
| [negative_binomial2](models/negative_binomial2.md) | Overdispersed count with estimated positive shape | x, exposure | mean, \(\mu+\mu^2/k\), sd |
| [gamma_regression](models/gamma_regression.md) | Positive continuous response with log-linear mean | x | mean, \(\mu^2/k\), sd |
| [saturating_growth](models/saturating_growth.md) | Gaussian response around \(b+A(1-e^{-rt})\) | nonnegative time | mean, observation variance, sd |

Positive scales, shape, amplitude and rate use the descriptor's log transforms.
The gallery records generating parameters and fit starts separately from the
estimated values. A finite random sample generally does not have its generating
parameters as the exact maximum-likelihood estimate. The target check therefore
uses independent formulas at the returned estimate, while independent native
likelihood checks cover values and derivatives at fixed, non-optimal parameters.

## Complete groups, random effects and ordered series

| Model guide with Python and Scala calls | Unit and marginalization | Prediction/forecast cases |
| --- | --- | --- |
| [gaussian_random_intercept](models/gaussian_random_intercept.md) | Complete group; exact Gaussian integration | Existing-group posterior moments and new-group prior moments |
| [gaussian_random_intercept_laplace](models/gaussian_random_intercept_laplace.md) | Same complete group; generic dense Laplace calculation | Same named cases and the same fixture as the exact model |
| [poisson_random_intercept](models/poisson_random_intercept.md) | Complete count group; one latent intercept, Laplace | Existing-group approximate posterior moments and exact new-group prior moments |
| [poisson_random_slope](models/poisson_random_slope.md) | Complete count group; latent intercept and slope, Laplace | Uses the full two-dimensional posterior covariance for future x/exposure |
| [ar1](models/ar1.md) | Complete directly observed Gaussian AR(1) series | One-step lag prediction, conditional multi-step forecast, new stationary series |
| [gaussian_ar1_random_intercept](models/gaussian_ar1_random_intercept.md) | Complete group; exact shared-intercept plus stationary AR(1) covariance | History-conditioned future moments and new stationary group moments |

Ordered examples use consecutive integer time steps and explicit group/order
columns. Conditional future steps begin immediately after the last history time.
New-group cases deliberately use group IDs absent from training and supply empty
history. Their rows must survive the Spark join. A conditional target with a
missing history group must fail rather than silently drop that future group.

Random-effect and time-series outputs here are pointwise observation moments
conditional on fitted population parameters. They exclude uncertainty from
estimating those parameters. They are not simultaneous intervals, posterior
simulation draws or full cross-step covariance tables.

Independent per-group estimation is a separate API. The
[installed acceptance example](../python/examples/validate_installed.py) includes
`fit_groups` for two distinct Gaussian populations, distributed model-row joins,
response-free predictions and persisted model rows. The gallery's complete-group
examples estimate shared population parameters across groups using `fit_shared`.
Fitting a separate variance-component model to each single group would change
the statistical question and can destroy identifiability.

## Independent numerical checks

[numerical_oracles.py](../python/examples/numerical_oracles.py) contains original
analytic Gaussian and Poisson random-effect references plus dense covariance
conditioning. [validate_native_oracles.py](../python/examples/validate_native_oracles.py)
compares actual framed native calls with those references. It checks exact
Gaussian/Laplace parity, whole-unit weights, implicit-mode contributions to
Laplace gradients, full random-slope posterior covariance and AR(1) innovation
propagation. The combined Gaussian oracle uses a dense covariance factorization
independent of the native AR precision calculation.

[build_row_references.py](../python/examples/build_row_references.py) uses an
explicitly prepared optional SciPy installation to create independent
distribution-normalization and analytic-gradient fixtures.
[validate_row_references.py](../python/examples/validate_row_references.py) checks
actual native row-model values, gradients, Hessians and targets. The NB2/Gamma
fixtures include shape endpoints, count 64/65 behavior, counts up to one million,
unequal exposures, near-mean large counts and small positive likelihood values.
The logistic examples include extreme logits. SciPy is not a production package
dependency.

The bounded native log-Gamma approximation used by NB2/Gamma has a separate
[actual AD versus SciPy validator](../python/examples/validate_special_functions.py).
Checking the helper and checking the complete distribution are separate tests;
normalization can suffer cancellation even when an individual log-Gamma value
is accurate. No production gradient uses finite differences.

Native process tests do not qualify the JVM or Spark path. Likewise, a local
two-thread Spark execution is not multi-node recovery or a scaling benchmark.
The machine-readable [coverage.json](../python/examples/gallery/coverage.json)
lists authored examples, reference coverage and actual execution status. Only
a retained report for the selected source/artifact establishes a passed run.

## Relationship to the TMB course

The existing [TMB course](../../../courses/tmb-modeling/README.md) retains its
full R/TMB templates and public-API inventory. Model-family correspondence is
not unchanged-template compatibility or evidence that every TMB API is present.

| Course model or topic | Native example coverage | Retained boundary |
| --- | --- | --- |
| `normal_mean.cpp`, Gaussian likelihood and regression | `normal`, `linear_gaussian`, `quadratic_gaussian` | Original native functors; no R data macros or automatic REPORT translation |
| `poisson_exposure.cpp`, count distributions | `poisson_exposure`, logistic and NB2 examples | Native support/domain contracts are explicit; counts and binary responses differ |
| Positive continuous distribution likelihoods | `gamma_regression` | This does not provide every TMB density helper |
| `random_intercept.cpp`, fixed/random effects and Laplace | Exact/Laplace Gaussian RI, Poisson RI and random slope | Bounded independent groups, local mode, dense q <= 8 and d+q <= 16 |
| `nonlinear.cpp`, nonlinear trend | `saturating_growth` demonstrates a nonlinear Gaussian mean | The course template is positive-amplitude exponential decay, a different parameterization and direction; it is not copied unchanged |
| `panel_trend.cpp`, nonlinear trend plus group effects | Group conditioning concepts are shown by native random-effect examples | The exact nonlinear-decay plus random-intercept template remains in the R/TMB project |
| `ar1.cpp`, latent AR states plus measurement noise | Directly observed AR(1), plus shared-intercept/AR covariance | The course latent-state model has separate observation noise; neither native example silently claims to be that model |
| `censored_weibull.cpp` | Custom input-mapping/authoring contract can represent extra fields | Censored Weibull is not in the prepared native registry |
| `parallel_gaussian.cpp`, OpenMP accumulators | Spark distributes independent units with a common parameter vector | It does not expose TMB OpenMP/autopar configuration or thread benchmarks |
| `density_forms.cpp`, arbitrary MVN/GMRF and sparse fields | Bounded named Gaussian covariance models | No generic globally coupled sparse random-field solver |
| `stable_mixture.cpp`, separable arrays and atomic functions | Smoothness and derivative contracts are explained in custom authoring | These course templates and custom atomic APIs remain in the full TMB route |
| `MakeADFun`, parameter maps, REPORT/ADREPORT and sdreport | Explicit prepared descriptors, data-only JSON and named prediction targets | No R object emulation, automatic delta-method report or parameter-uncertainty output |
| Profiles, profile roots, simulation/checkConsistency and oneStepPredict diagnostics | Explicit forecast targets and numerical oracle examples | No automatic likelihood profiling, simulator or generic residual-diagnostic API |

For a new native family, follow [custom-model authoring](CUSTOM-MODELS.md), add
its independent references and gallery recipe, rebuild the source-bound artifact,
then record actual native and Spark execution. Unsupported course models remain
available through their separately prepared R/TMB projects until a native
implementation is explicitly authored and qualified.
