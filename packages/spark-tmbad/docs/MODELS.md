# Model contracts and statistical scope

The native artifact contains a registry of compiled, trusted C++ models.
`describe` reports the registry declaration for a model, including parameter
order, fit fields, independent unit, prediction targets and forecast targets.
Python and Scala select these declarations. They do not reinterpret arbitrary
Python functions, import executable code from saved models, compile source in
tasks, or run R.

Each input has an explicit name. A model needing `x`, `exposure` and `y` might
be fitted to DataFrame columns named `temperature`, `hours` and `events` by
mapping those three names in `ModelSpec.columns`. A prediction target declares
its own fields. Its mapping may use `future_temperature` and `future_hours`
without requiring `events`. A missing response is valid for a response-free
target; a missing required predictor is an input error.

## Shared parameters and separate models

`fit_shared` estimates one parameter vector across all valid independent units.
The driver optimizer sends the same parameter vector to every task at each
evaluation. Tasks evaluate native objectives and derivatives and Spark combines
accepted task results. This is suitable for a pooled regression or a model
whose independent groups share population parameters.

`fit_groups` estimates a separate parameter vector for each group. A resulting
model for group A does not share its coefficients with group B. Its result is
a Spark DataFrame containing model JSON, and grouped prediction joins future
units to their matching fitted models within Spark. Use this operation when
the scientific model calls for independent fits, such as unrelated series.

The two operations answer different statistical questions. Partitioning a
DataFrame does not change one into the other.

## Complete groups and ordered histories

A row-factorized objective can be reduced in row batches. A complete-unit
objective must receive the entire independent group. For example, a random
intercept couples all observations sharing that intercept. Splitting its group
across independent likelihood evaluations changes the model.

The JVM adapter assembles complete groups before evaluation. It checks row
identities, deterministic within-group order, missing keys, invalid numerical
support and model-specific limits. A group exceeding its declared bound is an
error. Reducing batch size or silently cutting the group into pieces is not an
alternative. A global latent field or cross-group covariance needs a different
factorization or solver and is outside this additive interface.

Forecast input consists of a history DataFrame and a future DataFrame. The
history fields supply observed data required to condition the forecast. The
future fields supply horizons or future predictors required by its declared
target. Group and row identities determine which history belongs to which
future rows. Ordered models require unambiguous ordering; storage partition
order is never a time index. Row identities are checked globally. If a time
index repeats in different groups, use a composite identity such as
`id_columns=["series", "time"]`; the separate group key does not automatically
make a repeated row ID unique.

## Prediction, conditioning and uncertainty

A prediction target names a scientific quantity. A fitted likelihood alone
does not determine whether a caller wants an expected count, a new-group mean,
an existing-group conditional mean, a one-step conditional mean, or a joint
forecast covariance. The caller chooses a target declared by the prepared
model and supplies that target's declared fields.

The initial named Gaussian and AR(1) hooks use these contracts. Inspect the
prepared descriptor to confirm they are present in the selected artifact.

| Model | Operation and target | Numerical target fields | History | Outputs |
| --- | --- | --- | --- | --- |
| `normal` | predict/forecast `response` | none | empty | mean, sd |
| `gaussian_random_intercept` | predict/forecast `existing_group` | none | y | mean, variance, sd |
| `gaussian_random_intercept` | predict/forecast `new_group` | none | empty | mean, variance, sd |
| `ar1` | predict `response` | lag | no | mean, variance, sd |
| `ar1` | forecast `conditional_history` | time | time, y | mean, variance, sd |
| `ar1` | forecast `stationary_new_series` | time | empty | mean, variance, sd |

Row-model forecasting represents independent future observations, using supplied
future predictors when declared. It does not introduce time dependence or use
conditioning history. Each featureless request still carries one identity row
per desired output.
`ar1` fit fields are `time` and `y`, with integer cadence one. Its conditional
future time starts one step after the last history time and then advances by
one. `gaussian_random_intercept` fit fields contain `y` and require complete
groups. Its future observations share a group effect but the tabular hooks
above report marginal per-row variances, not a joint covariance matrix.

Gaussian random-intercept models can calculate exact conditional moments for
an existing group using its history. A new group uses the population random
effect distribution. These answers differ even with the same fitted global
parameters. An AR(1) forecast conditions on a history endpoint and advances
through explicit future horizons; a stationary new-series target uses a
different distribution.

The provided conditional moments treat fitted parameters as fixed. They do
not include uncertainty from estimating those parameters. A reported latent
variance, observation variance or covariance must retain its named target;
none is automatically a confidence interval for the fitted population mean.

## Custom likelihoods and random effects

Custom models are prepared C++ functors compiled into the native registry.
Their descriptors declare parameters, support, factorization, field order,
output columns and separate prediction or forecasting hooks. Preparing a new
functor requires a new content identity and numerical validation before tasks
can select it. See the native authoring contract in [PROTOCOL.md](PROTOCOL.md).

Automatic differentiation of a scalar joint objective does not by itself
integrate random effects. Exact Gaussian integration and a generic Laplace
approximation are distinct algorithms. A generic Laplace backend additionally
needs a valid inner mode, curvature and derivatives of the resulting marginal
objective, including the parameter dependence of the mode and curvature.
Only capabilities actually declared by the prepared native model are usable.
No generic mixed-effects or uncertainty capability is inferred from the
presence of TMBad.

## Identities and saved models

Saved models retain the model source identity, native build identity, fitted
parameter order, data mapping and optimizer diagnostics. Loading requires an
explicit compatible prepared runtime. Absolute deployment paths can change;
the content identities cannot. The binding includes the native binary,
architecture and JAR hash, so preserve that installation or image with the saved
JSON. Matching model names do not authorize a rebuilt artifact, an automatic
ARM64-to-AMD64 migration or mixed-architecture execution. JSON is data only.
Never deserialize Python
pickles or execute a class or module path supplied by a saved model.

The fitting data and history are not silently embedded in a model artifact.
Keep the data version and forecasts' conditioning history alongside scientific
results when reproducibility matters. A successful numerical fit does not
prove a representative dataset, valid causal model or production deployment.

Prediction and forecasting reject unconverged fitted models by default. An
explicit `allow_unconverged: true` option permits diagnostic evaluation while
retaining the failed-fit diagnostics. It does not turn a stalled optimizer into
valid estimation. A converged local score is also separate from identification
or a global optimum.
