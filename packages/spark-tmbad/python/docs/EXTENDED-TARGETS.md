# Named targets, fixed evaluation and declared parameters

The 0.2 Python frontend adds explicit named Gaussian priors, selected L1,
fixed nuisance parameters and prediction from declared parameter sets. These
interfaces require the matching prepared JVM adapter. The package import and
all JSON constructors remain lightweight; they do not import PySpark, start a
process, compile a model or download dependencies.

## Define the statistical target

A named target is explicit about its optimization coordinates and normalization:

```python
regularization = {
    "schema_version": 1,
    "coordinate_system": "native_optimizer_parameters",
    "normalization": "summed_likelihood_target",
    "gaussian": {"mu": {"mean": 1.0, "precision": 2.0}},
    "l1": {"mu": 1.0},
}
```

Names match the prepared descriptor exactly. Precision is positive inverse
variance; omitted names are unpenalized. Choosing documented coefficient names
provides coefficient-only regularization. A Gaussian prior on `log_sigma` is a
prior on that coordinate, not on sigma. No implicit parameter Jacobian is added.
Dense priors and arbitrary penalty callbacks are not part of this schema.

For summed data NLL S, normalized selected Gaussian prior NLL P and selected L1
penalty Q, the target is `(S + P + Q) / d`. The denominator is one for `sum` and
the validated likelihood weight mass for `weighted_mean`. Dividing all terms
preserves the same point optimum across these reductions. Arbitrary weights
represent a weighted/power likelihood unless their sampling meaning justifies
frequency replication.

Gaussian terms include their normalizing constants. L1 is reported as an explicit
penalty without a Laplace-density normalizer. The target identifies a MAP or
penalized point-estimation problem; it does not establish a normalized posterior,
evidence calculation or sampler execution. MAP depends on the chosen coordinates.
A fixed-parameter prior is distinct from integrating random effects in a marginal
likelihood.

Legacy `l2_strength` retains its existing all-coordinate, post-reduction meaning.
Nonzero legacy L2 cannot be combined with the new regularization block. Fixed
constraints alone may still accompany the legacy target.

## Fit with selected L1 and a fixed nuisance parameter

For four normal observations `[1, 2, 4, 7]`, fixing sigma to one, the target above
has the analytic positive optimum mu=2.5. Use the prepared normal descriptor's
actual names and a DataFrame with `row_id` and `y`:

```python
from ds60_spark_tmbad import ModelSpec, SparkTMBad

api = SparkTMBad(runtime)
spec = ModelSpec("normal", {"y": "y"}, id_columns=["row_id"])
fitted = api.fit_shared(
    observations,
    spec,
    options={
        "initial_parameters": [0.0, 0.0],
        "regularization": regularization,
        "fixed_parameters": {"log_sigma": 0.0},
        "solver": {
            "method": "proximal_gradient",
            "initial_step": 1.0 / 6.0,
            "kkt_tolerance": 1e-7,
        },
    },
)
print(fitted.model["target"]["stationarity"])
```

The original full initial vector must pass the native domain check. Fixed values
then explicitly replace those coordinates, and the saved target records the
effective initial point. They are exact equality constraints. An all-fixed fit
performs one real evaluation and records `all_parameters_fixed`, zero free
parameters and no optimizer history. It does not claim to estimate a parameter.

Nonempty L1 selects proximal gradient by default; explicit BFGS with L1 is
rejected. At an L1 optimum the smooth projected gradient can remain nonzero.
Use the declared constrained KKT criterion and its units. Proximal records are
stored in `target.proximal_trace`; no BFGS history is invented. A stalled or failed
fit remains unconverged. Existing fitted prediction safeguards remain in force.

## Evaluate a point without running an optimizer

```python
result = api.evaluate_shared(
    observations,
    spec,
    {"log_sigma": 0.0, "mu": 2.5},
    options={
        "regularization": regularization,
        "fixed_parameters": {"log_sigma": 0.0},
        "reduction": "sum",
    },
)
print(result["loss_components"])
print(result["smooth_gradient_sum"])
print(result["l1_subgradient_sum"])
print(result["summed_kkt_inf"])
```

A complete named map is normalized to the prepared parameter order. A supplied
point must already satisfy fixed values; evaluation never projects it silently.
Optimizer settings and initial parameters are not evaluation options. The result
has no convergence flag or fake fit record. It contains bounded value/gradient,
subgradient, count/weight, partition and data-ledger diagnostics. L1 intervals are
penalty-only intervals in summed-target units, separate from the smooth gradient.
An ordinary derivative of abs at zero or a generic Laplace Hessian is not claimed.

The plan/target-specification digest identifies the model, coordinates, bounds,
selected terms and fixed values. It does not identify observations or certify a
posterior target by itself. The data/weight ledger and prepared artifact identity
are separate required parts of an evaluation receipt.

## Predict from declared truth or an actual supplied posterior draw

A declared point has its own data-only type, without fit, convergence or training
count fields:

```python
from ds60_spark_tmbad import PreparedParameters

truth = PreparedParameters.from_parameters(
    runtime,
    "normal",
    parameters={"mu": 2.0, "log_sigma": 0.0},
    purpose="simulation_truth",
    parameter_set_id="normal-generator-seed-17",
    layout={
        "id_columns": ["row_id"],
        "group_columns": [],
        "order_columns": [],
    },
    provenance={
        "kind": "simulation_truth",
        "generator_source_sha256": generator_source_sha256,
        "seed": 17,
    },
)
predictions = truth.predict(
    future_rows,
    options={"target": "response", "columns": {}},
)
truth.save("normal-truth.json")
```

`generator_source_sha256` is the actual source identity of the declared generator,
not an arbitrary placeholder to report as evidence. A fixture hash is optional.
For `sensitivity`, provenance instead contains kind and `reference_sha256`.
For `posterior_draw`, it contains kind, `posterior_target_sha256`,
`sampler_receipt_sha256`, `chain_id` and `draw_index`. These are structural
provenance checks; the frontend cannot certify that a sampler ran or converged.
The parameter vector contains the descriptor's population/optimization coordinates,
not arbitrary extra latent-effect draws.

`PreparedParameters.from_json/load/save` preserve exact model/artifact binding.
It cannot be loaded as a FittedModel, and `allow_unconverged` is rejected even when
false. Predictive numeric columns carry parameter-set ID, purpose and parameter
digest in Spark metadata. This first interface handles one bounded vector per
call. It does not introduce a batch posterior sampler. Combining real draw
predictions requires their weights and total variance `E[v + mu^2] - E[mu]^2`;
averaging only conditional variances drops parameter uncertainty.

Complete-unit models still require group keys, and ordered models require order
keys. Conditional prediction needs explicit `history_columns`; forecasting uses
`future_columns` plus the declared history/future layouts. Prediction retains the
prepared model's conditioning and approximation semantics for each supplied point.
A posterior label does not change a local Laplace approximation into exact latent
conditioning.

## Runtime acceptance and compatibility

The new [runtime validation program](../examples/validate_extended.py) performs
real named-target fits and fixed evaluations, source-bound persistence, fitted
prediction and declared AR1 prediction/forecasting against the unchanged gallery's
independent innovation formulas. It checks numeric-column provenance metadata.
Run it only with a fresh noneditable 0.2 wheel and matching native/JVM artifact:

```sh
spark-submit --jars /opt/spark-tmbad/spark-tmbad.jar \
  examples/validate_extended.py \
  --manifest /opt/spark-tmbad/artifact.json \
  --output /owned/fresh-extended-acceptance.json
```

The program's existence is not an execution receipt. Its actual run, copied-project
and separate-worker qualification belong to their recorded acceptance gates.
Only its small requested predictions are collected; observations and grouped models
remain on Spark's execution side.

The frontend reads supported 0.1.0 and 0.2.0 artifact metadata. Every document must
match its selected runtime version and exact source/binary/JAR identities. This
does not migrate historical models onto new artifacts. New method calls inspect
the loaded JAR capability and fail clearly when an old adapter is active; create
a new correctly prepared Spark session instead of trying to attach a JAR after
startup. Historical fixtures and receipts remain unchanged.
