# Poisson counts with a latent group intercept

This model introduces within-group count dependence through a shared Gaussian latent intercept. It
estimates shared beta and tau from complete groups and uses a one-dimensional Laplace approximation
to the marginal likelihood.

## Likelihood and parameterization

\[
Y_i\mid u\sim\operatorname{Poisson}(e_i e^{\beta+u}),\quad u\sim N(0,\tau^2),\quad f_u=\sum_i e_i e^{\beta+u}-\sum_i y_i+u/\tau^2,\quad H_{uu}=\sum_i e_i e^{\beta+u}+1/\tau^2.
\]

The scalar score is strictly increasing, so the independent reference can bracket its mode. The
marginal gradient includes the effect of that mode on curvature. Existing-group moments use the
local Gaussian Laplace posterior; new-group moments use the exact Gaussian prior for the log rate.

## The actual fixture

The shared gallery fixture contains 80 observations across 10 complete groups. Its native fit fields
are `exposure, y`. Row identity is `row_id`, with explicit `series` group keys. The fixed-seed
generator writes 12 significant digits of canonical precision. These are public synthetic
observations, not a production dataset.

| Stored parameter | Generating value | Optimization start |
| --- | ---: | ---: |
| `beta` | 0.2 | 0.1 |
| `log_tau` | -0.5108256 | -0.6931472 |

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
    "poisson_random_intercept"
]
runtime = PreparedRuntime.from_manifest("/opt/spark-tmbad/artifact.json")
api = SparkTMBad(runtime)
training = frame(spark, recipe["training_rows"], list(recipe["training_rows"][0]), ordered=False)
spec = ModelSpec(
    "poisson_random_intercept",
    {"exposure": "exposure", "y": "y"},
    id_columns=["row_id"],
    group_columns=["series"],
    order_columns=[],
)
fitted = api.fit_shared(
    training.repartition(2),
    spec,
    options={**recipe["fit_options"], "initial_parameters": [0.1, -0.69314718056]},
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
        {"exposure": 0.75, "row_id": 1000, "series": "s0"},
        {"exposure": 1.5, "row_id": 1001, "series": "s0"},
    ],
    ["exposure", "row_id", "series"],
    ordered=False,
)
predicted = fitted.predict(
    requested,
    history=history,
    options={
        "target": "existing_group",
        "columns": {"exposure": "exposure"},
        "output_prefix": "prediction_",
        "history_columns": {"exposure": "exposure", "y": "y"},
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
        {"exposure": 0.75, "row_id": 1000, "series": "s0"},
        {"exposure": 1.5, "row_id": 1001, "series": "s0"},
    ],
    ["exposure", "row_id", "series"],
    ordered=False,
)
forecasts = fitted.forecast(
    history,
    future,
    options={
        "target": "existing_group",
        "history_columns": {"exposure": "exposure", "y": "y"},
        "future_columns": {"exposure": "exposure"},
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
        {"exposure": 0.75, "row_id": 2000, "series": "unseen"},
        {"exposure": 1.5, "row_id": 2001, "series": "unseen"},
    ],
    ["exposure", "row_id", "series"],
    ordered=False,
)
new_group = fitted.forecast(
    training.limit(0),
    unseen,
    options={
        "target": "new_group",
        "history_columns": {"exposure": "exposure", "y": "y"},
        "future_columns": {"exposure": "exposure"},
        "output_prefix": "new_group_",
    },
)
new_group.orderBy("row_id").show()
```

An existing-group target uses posterior mode and inverse curvature as a Gaussian approximation, then
applies Poisson/lognormal moment formulas. The prior new-group formula is exact at fixed population
parameters. Parameter uncertainty is excluded from both.

## A fixed-parameter calculation

For a new group with beta=0, tau=1 and exposure=1, the expected count is exp(1/2), not exp(beta)=1.
Under a Gaussian latent distribution with mean m and variance v, expected count is e*exp(beta+m+v/2)
and variance is mean+mean squared*expm1(v).

This calculation explains the target at stated parameters. It is distinct from the actual estimated
values recorded by a gallery execution.

## Concrete Python and Scala runs

```sh
spark-submit --master 'local[2]' --jars /opt/spark-tmbad/spark-tmbad.jar \
  python/examples/gallery/poisson_random_intercept.py \
  --manifest /opt/spark-tmbad/artifact.json --output /owned/results/poisson_random_intercept

spark-submit --master 'local[2]' \
  --class io.ds60.spark.tmbad.examples.ModelGallery \
  /opt/spark-tmbad/spark-tmbad.jar /opt/spark-tmbad/artifact.json \
  python/examples/gallery/fixtures.json poisson_random_intercept
```

The Python script saves and reloads model JSON and checks the small predicted tables against
independent formulas at the returned fit. The Scala counterpart exercises the same JVM facade,
fixture and declared targets, checking convergence, finite outputs and retained row identities.
Those are separate execution records.

## Recorded execution

Observed in the installed Python wheel on Linux arm64, Spark 4.0.1, `local[2]`.

The native build is `324c97bdfa9c` and JAR digest is `754b4bb08f25`. The [retained report](../../qualification/arm64-python-gallery.json) contains full identities, source hashes, diagnostics and unrounded values.

| Stored parameter | Observed estimate | Original-scale interpretation |
| --- | --- | --- |
| `beta` | 0.45712866 | 0.45712866 |
| `log_tau` | -0.15501993 | tau = 0.85639811 |

The fit converged with projected gradient norm 4.0397448e-07; raw gradient norm 4.0397448e-07. It used 10 iterations and 18 objective calls, including 0 reviewed numerical candidate rejections. Observed objective value: 153.03877. Active bound indices: `[]`.

### Observed prediction: `existing_group`

| `row_id` | `series` | `exposure` | `mean` | `variance` | `sd` |
| --- | --- | --- | --- | --- | --- |
| 1000 | s0 | 0.75 | 0.38342429 | 0.41001512 | 0.64032423 |
| 1001 | s0 | 1.5 | 0.76684859 | 0.8732119 | 0.93445808 |

These returned values passed the independent target formula check at the fitted parameters. Uncertainty: Poisson/lognormal moments under Laplace posterior approximation; no parameter uncertainty.

### Observed prediction: `new_group`

| `row_id` | `series` | `exposure` | `mean` | `variance` | `sd` |
| --- | --- | --- | --- | --- | --- |
| 2000 | unseen | 0.75 | 1.7094223 | 4.8717009 | 2.207193 |
| 2001 | unseen | 1.5 | 3.4188445 | 16.067959 | 4.0084859 |

These returned values passed the independent target formula check at the fitted parameters. Uncertainty: exact prior Poisson/lognormal moments; no parameter uncertainty.

### Observed forecast: `existing_group`

| `row_id` | `series` | `exposure` | `mean` | `variance` | `sd` |
| --- | --- | --- | --- | --- | --- |
| 1000 | s0 | 0.75 | 0.38342429 | 0.41001512 | 0.64032423 |
| 1001 | s0 | 1.5 | 0.76684859 | 0.8732119 | 0.93445808 |

These returned values passed the independent target formula check at the fitted parameters. Uncertainty: Poisson/lognormal moments under Laplace posterior approximation; no parameter uncertainty.

### Observed forecast: `new_group`

| `row_id` | `series` | `exposure` | `mean` | `variance` | `sd` |
| --- | --- | --- | --- | --- | --- |
| 2000 | unseen | 0.75 | 1.7094223 | 4.8717009 | 2.207193 |
| 2001 | unseen | 1.5 | 3.4188445 | 16.067959 | 4.0084859 |

These returned values passed the independent target formula check at the fitted parameters. Uncertainty: exact prior Poisson/lognormal moments; no parameter uncertainty.

The estimates above are actual finite-sample results, not the fixture's generating values. This local execution does not establish multi-node scale, a global optimum or general model adequacy.

Direct Scala execution passed the same model and declared targets on this artifact and fixture. Observed fitted parameters and objective values match the Python run; see the [frontend parity receipt](../../qualification/arm64-frontend-parity.json). This is a same-host qualification, not the separately requested Compose cluster or worker-container-loss acceptance.

## Common mistakes

- Plugging only the latent mode into exp and omitting its variance correction.
- Claiming that Gaussian-reference parity makes this Poisson Laplace integral exact.
- Treating exposure as a group likelihood weight rather than part of each count mean.

See [the gallery](../EXAMPLES.md), [preparation](../PREPARATION.md), and [custom-model
contracts](../CUSTOM-MODELS.md) for the full execution and scope boundaries. A local run is not a
cluster-scale or global-optimum guarantee.