# Poisson random intercepts and slopes

This example exercises a genuinely two-dimensional latent mode. Each complete group has a random
intercept and random slope, with independent Gaussian priors but generally correlated posterior
coordinates.

## Likelihood and parameterization

\[
\eta_i=\beta_0+\beta_1x_i+u_0+u_1x_i+\log e_i,\quad u_j\sim N(0,\tau_j^2),\quad a(x)=(1,x)^T,\quad v(x)=a(x)^T H^{-1}a(x).
\]

The generic Laplace engine optimizes both latent coordinates and differentiates the full marginal
curvature correction. Existing-group prediction must retain the off-diagonal posterior covariance
term: v(x)=V00+2*x*V01+x squared*V11. Independent priors do not imply independent posterior random
effects.

## The actual fixture

The shared gallery fixture contains 96 observations across 12 complete groups. Its native fit fields
are `x, exposure, y`. Row identity is `row_id`, with explicit `series` group keys. The fixed-seed
generator writes 12 significant digits of canonical precision. These are public synthetic
observations, not a production dataset.

| Stored parameter | Generating value | Optimization start |
| --- | ---: | ---: |
| `beta0` | 0.2 | 0.1 |
| `beta1` | 0.5 | 0.3 |
| `log_tau0` | -0.5108256 | -0.6931472 |
| `log_tau1` | -1.049822 | -1.203973 |

Generating values describe how the fixture was constructed. They are not claimed to be the exact MLE
of a finite sample. Stored log or atanh coordinates must be transformed before interpreting their
original-scale scientific quantities.

## Fit the DataFrame

Run from the package directory with a prepared classic Spark session named `spark`. The common
`frame` helper constructs a bounded SQL `VALUES` DataFrame; it does not introduce a PythonRDD or
Python UDF into the executor plan.

```python
import json
import sys
from pathlib import Path
from ds60_spark_tmbad import ModelSpec, PreparedRuntime, SparkTMBad

sys.path.insert(0, str(Path("python/examples").resolve()))
from gallery.run_gallery import frame

recipe = json.loads(Path("python/examples/gallery/fixtures.json").read_text())["cases"][
    "poisson_random_slope"
]
runtime = PreparedRuntime.from_manifest("/opt/spark-tmbad/artifact.json")
api = SparkTMBad(runtime)
training = frame(spark, recipe["training_rows"], list(recipe["training_rows"][0]), ordered=False)
spec = ModelSpec(
    "poisson_random_slope",
    {"x": "x", "exposure": "exposure", "y": "y"},
    id_columns=["row_id"],
    group_columns=["series"],
    order_columns=[],
)
fitted = api.fit_shared(
    training.repartition(2),
    spec,
    options={
        **recipe["fit_options"],
        "initial_parameters": [0.1, 0.3, -0.69314718056, -1.20397280433],
    },
)
print(fitted.model["parameter_names"])
print(fitted.model["parameters"])
print(fitted.model["fit"])
```

The shared fit uses one population parameter vector across all input partitions. Inspect
`converged`, the raw/projected scores, active bounds and the stop reason. The API withholds
predictions from an unconverged fit by default; do not use a diagnostic override to make an example
appear successful.

## Response-free prediction

```python
history = training.where("series = 's0'")
requested = frame(
    spark,
    [
        {"exposure": 1.0, "row_id": 1000, "series": "s0", "x": -0.5},
        {"exposure": 1.5, "row_id": 1001, "series": "s0", "x": 0.8},
    ],
    ["exposure", "row_id", "series", "x"],
    ordered=False,
)
predicted = fitted.predict(
    requested,
    history=history,
    options={
        "target": "existing_group",
        "columns": {"x": "x", "exposure": "exposure"},
        "output_prefix": "prediction_",
        "history_columns": {"x": "x", "exposure": "exposure", "y": "y"},
    },
)
predicted.orderBy("row_id").show()
```

The requested rows contain no future `y`. A history-dependent target receives its historical
response in a separate DataFrame. Native field names and Spark column names are mapped explicitly
instead of inferred from their spelling.

## Forecast the declared target

```python
future = frame(
    spark,
    [
        {"exposure": 1.0, "row_id": 1000, "series": "s0", "x": -0.5},
        {"exposure": 1.5, "row_id": 1001, "series": "s0", "x": 0.8},
    ],
    ["exposure", "row_id", "series", "x"],
    ordered=False,
)
forecasts = fitted.forecast(
    history,
    future,
    options={
        "target": "existing_group",
        "history_columns": {"x": "x", "exposure": "exposure", "y": "y"},
        "future_columns": {"x": "x", "exposure": "exposure"},
        "output_prefix": "forecast_",
    },
)
forecasts.orderBy("row_id").show()
```

The second worked case requests a new group or stationary series, with an ID absent from training
and an explicitly empty history:

```python
unseen = frame(
    spark,
    [
        {"exposure": 1.0, "row_id": 2000, "series": "unseen", "x": -0.5},
        {"exposure": 1.5, "row_id": 2001, "series": "unseen", "x": 0.8},
    ],
    ["exposure", "row_id", "series", "x"],
    ordered=False,
)
new_group = fitted.forecast(
    training.limit(0),
    unseen,
    options={
        "target": "new_group",
        "history_columns": {"x": "x", "exposure": "exposure", "y": "y"},
        "future_columns": {"x": "x", "exposure": "exposure"},
        "output_prefix": "new_group_",
    },
)
new_group.orderBy("row_id").show()
```

Targets take future x and exposure, then return Poisson/lognormal observation moments.
Existing-group moments use the local Gaussian Laplace posterior; new-group prior moments are exact
at fixed parameters. There is no time dynamics in the future-covariate forecast hook.

## A fixed-parameter calculation

For a new group, latent variance is tau0 squared+x squared*tau1 squared. For an existing group it is
V00+2*x*V01+x squared*V11, so changing the sign of x changes the covariance contribution. The
expected count uses exp of the latent mean plus half this variance.

This calculation explains the target at stated parameters. It is distinct from the actual estimated
values recorded by a gallery execution.

## Concrete Python and Scala runs

```sh
spark-submit --master 'local[2]' --jars /opt/spark-tmbad/spark-tmbad.jar \
  python/examples/gallery/poisson_random_slope.py \
  --manifest /opt/spark-tmbad/artifact.json --output /owned/results/poisson_random_slope

spark-submit --master 'local[2]' \
  --class io.ds60.spark.tmbad.examples.ModelGallery \
  /opt/spark-tmbad/spark-tmbad.jar /opt/spark-tmbad/artifact.json \
  python/examples/gallery/fixtures.json poisson_random_slope
```

The Python script saves and reloads model JSON and checks the small predicted tables against
independent formulas at the returned fit. The Scala counterpart exercises the same JVM facade,
fixture and declared targets, checking convergence, finite outputs and retained row identities.
Those are separate execution records.

## Recorded execution

Observed in the installed Python wheel on Linux arm64, Spark 4.0.1, `local[2]`.

The native build is `324c97bdfa9c` and JAR digest is `80e5f77b54db`. The [retained
report](../../qualification/arm64-python-gallery.json) contains full identities, source hashes,
diagnostics and unrounded values.

| Stored parameter | Observed estimate | Original-scale interpretation |
| --- | --- | --- |
| `beta0` | 0.52332102 | 0.52332102 |
| `beta1` | 0.62602593 | 0.62602593 |
| `log_tau0` | -0.38660223 | tau0 = 0.67936127 |
| `log_tau1` | -1.3505902 | tau1 = 0.2590873 |

The fit converged with projected gradient norm 1.2121172e-06; raw gradient norm 1.2121172e-06. It
used 13 iterations and 28 objective calls, including 0 reviewed numerical candidate rejections.
Observed objective value: 180.09259. Active bound indices: `[]`.

### Observed prediction: `existing_group`

| `row_id` | `series` | `x` | `exposure` | `mean` | `variance` | `sd` |
| --- | --- | --- | --- | --- | --- | --- |
| 1000 | s0 | -0.5 | 1 | 1.6016892 | 1.7445495 | 1.320814 |
| 1001 | s0 | 0.8 | 1.5 | 3.9305691 | 4.9679026 | 2.2288792 |

These returned values passed the independent target formula check at the fitted parameters.
Uncertainty: Poisson/lognormal moments under multivariate Laplace approximation; no parameter
uncertainty.

### Observed prediction: `new_group`

| `row_id` | `series` | `x` | `exposure` | `mean` | `variance` | `sd` |
| --- | --- | --- | --- | --- | --- | --- |
| 2000 | unseen | -0.5 | 1 | 1.5674729 | 3.0744583 | 1.7534133 |
| 2001 | unseen | 0.8 | 1.5 | 5.3755083 | 24.335528 | 4.9331053 |

These returned values passed the independent target formula check at the fitted parameters.
Uncertainty: exact prior Poisson/lognormal moments; shared latent effects induce cross-row
dependence.

### Observed forecast: `existing_group`

| `row_id` | `series` | `x` | `exposure` | `mean` | `variance` | `sd` |
| --- | --- | --- | --- | --- | --- | --- |
| 1000 | s0 | -0.5 | 1 | 1.6016892 | 1.7445495 | 1.320814 |
| 1001 | s0 | 0.8 | 1.5 | 3.9305691 | 4.9679026 | 2.2288792 |

These returned values passed the independent target formula check at the fitted parameters.
Uncertainty: Poisson/lognormal moments under multivariate Laplace approximation; no parameter
uncertainty.

### Observed forecast: `new_group`

| `row_id` | `series` | `x` | `exposure` | `mean` | `variance` | `sd` |
| --- | --- | --- | --- | --- | --- | --- |
| 2000 | unseen | -0.5 | 1 | 1.5674729 | 3.0744583 | 1.7534133 |
| 2001 | unseen | 0.8 | 1.5 | 5.3755083 | 24.335528 | 4.9331053 |

These returned values passed the independent target formula check at the fitted parameters.
Uncertainty: exact prior Poisson/lognormal moments; shared latent effects induce cross-row
dependence.

The estimates above are actual finite-sample results, not the fixture's generating values. This
local execution does not establish multi-node scale, a global optimum or general model adequacy.

## Common mistakes

- Dropping posterior covariance V01 because the latent priors were independent.
- Changing covariate centering or scaling between historical and future rows.
- Using this bounded q=2 example as evidence for a globally coupled sparse random-field solver.

See [the gallery](../EXAMPLES.md), [preparation](../PREPARATION.md), and [custom-model
contracts](../CUSTOM-MODELS.md) for the full execution and scope boundaries. A local run is not a
cluster-scale or global-optimum guarantee.