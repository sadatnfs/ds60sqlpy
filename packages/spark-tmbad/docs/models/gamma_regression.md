# Gamma regression for positive continuous responses

Use this model for strictly positive continuous measurements with a log-linear mean. Its variance
grows quadratically with that mean at fixed shape.

## Likelihood and parameterization

\[
\mu_i=e^{\beta_0+\beta_1x_i},\quad k=e^r,\quad Y_i\sim\operatorname{Gamma}(\text{shape}=k,\text{scale}=\mu_i/k),\quad L_i=\log\Gamma(k)-k\log k+k\log\mu_i-(k-1)\log y_i+ky_i/\mu_i.
\]

Fitting requires x and y>0, while future targets require x alone. The scale parameter of the Gamma
distribution is mu/shape; it is not an additional fitted residual sigma. The log-Gamma approximation
has separate scalar and complete-model oracle checks.

## The actual fixture

The shared gallery fixture contains 128 observations. Its native fit fields are `x, y`. Row identity
is `row_id`. The fixed-seed generator writes 12 significant digits of canonical precision. These are
public synthetic observations, not a production dataset.

| Stored parameter | Generating value | Optimization start |
| --- | ---: | ---: |
| `intercept` | 0.3 | 0 |
| `slope` | 0.5 | 0.2 |
| `log_shape` | 1.386294 | 0.6931472 |

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
    "gamma_regression"
]
runtime = PreparedRuntime.from_manifest("/opt/spark-tmbad/artifact.json")
api = SparkTMBad(runtime)
training = frame(spark, recipe["training_rows"], list(recipe["training_rows"][0]), ordered=False)
spec = ModelSpec(
    "gamma_regression",
    {"x": "x", "y": "y"},
    id_columns=["row_id"],
    group_columns=[],
    order_columns=[],
)
fitted = api.fit_shared(
    training.repartition(2),
    spec,
    options={**recipe["fit_options"], "initial_parameters": [0.0, 0.2, 0.69314718056]},
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
history = training.limit(0)
requested = frame(
    spark, [{"row_id": 1000, "x": -0.5}, {"row_id": 1001, "x": 1.0}], ["row_id", "x"], ordered=False
)
predicted = fitted.predict(
    requested, options={"target": "response", "columns": {"x": "x"}, "output_prefix": "prediction_"}
)
predicted.orderBy("row_id").show()
```

The requested rows contain no future `y`. A history-dependent target receives its historical
response in a separate DataFrame. Native field names and Spark column names are mapped explicitly
instead of inferred from their spelling.

## Forecast the declared target

```python
future = frame(
    spark, [{"row_id": 1000, "x": -0.5}, {"row_id": 1001, "x": 1.0}], ["row_id", "x"], ordered=False
)
forecasts = fitted.forecast(
    history,
    future,
    options={
        "target": "response",
        "history_columns": {"x": "x", "y": "y"},
        "future_columns": {"x": "x"},
        "output_prefix": "forecast_",
    },
)
forecasts.orderBy("row_id").show()
```

Predictions are positive means with Gamma observation variances. A normalized density can exceed
one, so an individual continuous-data negative log likelihood can be negative. That is not by itself
a numerical failure.

## A fixed-parameter calculation

At mean 6 and shape 3, variance is 12 and standard deviation is sqrt(12). Doubling the mean to 12
with shape fixed makes variance 48. This differs from both a Poisson count and NB2 count model.

This calculation explains the target at stated parameters. It is distinct from the actual estimated
values recorded by a gallery execution.

## Concrete Python and Scala runs

```sh
spark-submit --master 'local[2]' --jars /opt/spark-tmbad/spark-tmbad.jar \
  python/examples/gallery/gamma_regression.py \
  --manifest /opt/spark-tmbad/artifact.json --output /owned/results/gamma_regression

spark-submit --master 'local[2]' \
  --class io.ds60.spark.tmbad.examples.ModelGallery \
  /opt/spark-tmbad/spark-tmbad.jar /opt/spark-tmbad/artifact.json \
  python/examples/gallery/fixtures.json gamma_regression
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
| `intercept` | 0.29108802 | 0.29108802 |
| `slope` | 0.44167394 | 0.44167394 |
| `log_shape` | 1.2672674 | shape = 3.5511353 |

The fit converged with projected gradient norm 1.9714068e-07; raw gradient norm 1.9714068e-07. It
used 11 iterations and 47 objective calls, including 0 reviewed numerical candidate rejections.
Observed objective value: 126.96341. Active bound indices: `[]`.

### Observed prediction: `response`

| `row_id` | `x` | `mean` | `variance` | `sd` |
| --- | --- | --- | --- | --- |
| 1000 | -0.5 | 1.0727775 | 0.32407988 | 0.56928014 |
| 1001 | 1 | 2.0808198 | 1.2192752 | 1.1042079 |

These returned values passed the independent target formula check at the fitted parameters.
Uncertainty: Gamma observation variance mu^2/shape; no parameter uncertainty.

### Observed forecast: `response`

| `row_id` | `x` | `mean` | `variance` | `sd` |
| --- | --- | --- | --- | --- |
| 1000 | -0.5 | 1.0727775 | 0.32407988 | 0.56928014 |
| 1001 | 1 | 2.0808198 | 1.2192752 | 1.1042079 |

These returned values passed the independent target formula check at the fitted parameters.
Uncertainty: Gamma observation variance mu^2/shape; no parameter uncertainty.

The estimates above are actual finite-sample results, not the fixture's generating values. This
local execution does not establish multi-node scale, a global optimum or general model adequacy.

## Common mistakes

- Passing zero or negative responses without a different observation model.
- Confusing Gamma scale mu/shape with shape or with a Gaussian standard deviation.
- Rejecting a finite negative density-based loss solely because it is negative.

See [the gallery](../EXAMPLES.md), [preparation](../PREPARATION.md), and [custom-model
contracts](../CUSTOM-MODELS.md) for the full execution and scope boundaries. A local run is not a
cluster-scale or global-optimum guarantee.