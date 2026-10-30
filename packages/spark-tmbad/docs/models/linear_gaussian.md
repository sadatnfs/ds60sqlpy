# Gaussian regression with one covariate

Use this model when an independent continuous response has a linear conditional mean in one supplied
covariate. Spark combines row likelihoods to estimate one intercept, slope and residual scale.

## Likelihood and parameterization

\[
m_i=\beta_0+\beta_1x_i,\quad \sigma=e^s,\quad L=\sum_i\left[s+\tfrac12\log(2\pi)+\frac{(y_i-m_i)^2}{2\sigma^2}\right].
\]

The native field order is x,y for fitting and x alone for prediction. The intercept is a model
parameter; a separate all-ones DataFrame column is unnecessary. A future covariate may have a
different Spark column name when it is explicitly mapped to native field x.

## The actual fixture

The shared gallery fixture contains 128 observations. Its native fit fields are `x, y`. Row identity
is `row_id`. The fixed-seed generator writes 12 significant digits of canonical precision. These are
public synthetic observations, not a production dataset.

| Stored parameter | Generating value | Optimization start |
| --- | ---: | ---: |
| `beta0` | 0.6 | 0.3 |
| `beta1` | 1.2 | 0.5 |
| `log_sigma` | -0.9162907 | -0.2231436 |

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
    "linear_gaussian"
]
runtime = PreparedRuntime.from_manifest("/opt/spark-tmbad/artifact.json")
api = SparkTMBad(runtime)
training = frame(spark, recipe["training_rows"], list(recipe["training_rows"][0]), ordered=False)
spec = ModelSpec(
    "linear_gaussian",
    {"x": "x", "y": "y"},
    id_columns=["row_id"],
    group_columns=[],
    order_columns=[],
)
fitted = api.fit_shared(
    training.repartition(2),
    spec,
    options={**recipe["fit_options"], "initial_parameters": [0.3, 0.5, -0.223143551314]},
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

A future-covariate forecast is the same conditional observation distribution evaluated at supplied
future x. It does not predict x itself, and it does not include parameter-estimation uncertainty.

## A fixed-parameter calculation

At beta0=1, beta1=2 and sigma=0.5, x=1 gives mean 3 and x=2 gives mean 5. Both observations have
variance 0.25. Changing x changes the conditional mean while the residual variance stays fixed.

This calculation explains the target at stated parameters. It is distinct from the actual estimated
values recorded by a gallery execution.

## Concrete Python and Scala runs

```sh
spark-submit --master 'local[2]' --jars /opt/spark-tmbad/spark-tmbad.jar \
  python/examples/gallery/linear_gaussian.py \
  --manifest /opt/spark-tmbad/artifact.json --output /owned/results/linear_gaussian

spark-submit --master 'local[2]' \
  --class io.ds60.spark.tmbad.examples.ModelGallery \
  /opt/spark-tmbad/spark-tmbad.jar /opt/spark-tmbad/artifact.json \
  python/examples/gallery/fixtures.json linear_gaussian
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
| `beta0` | 0.47607012 | 0.47607012 |
| `beta1` | 1.1894867 | 1.1894867 |
| `log_sigma` | -0.82514666 | sigma = 0.43817073 |

The fit converged with projected gradient norm 4.2844956e-06; raw gradient norm 4.2844956e-06. It used 13 iterations and 37 objective calls, including 0 reviewed numerical candidate rejections. Observed objective value: 76.005361. Active bound indices: `[]`.

### Observed prediction: `response`

| `row_id` | `x` | `mean` | `variance` | `sd` |
| --- | --- | --- | --- | --- |
| 1000 | -0.5 | -0.11867325 | 0.19199359 | 0.43817073 |
| 1001 | 1 | 1.6655568 | 0.19199359 | 0.43817073 |

These returned values passed the independent target formula check at the fitted parameters. Uncertainty: observation only; parameter uncertainty excluded.

### Observed forecast: `response`

| `row_id` | `x` | `mean` | `variance` | `sd` |
| --- | --- | --- | --- | --- |
| 1000 | -0.5 | -0.11867325 | 0.19199359 | 0.43817073 |
| 1001 | 1 | 1.6655568 | 0.19199359 | 0.43817073 |

These returned values passed the independent target formula check at the fitted parameters. Uncertainty: observation only; parameter uncertainty excluded.

The estimates above are actual finite-sample results, not the fixture's generating values. This local execution does not establish multi-node scale, a global optimum or general model adequacy.

Direct Scala execution passed the same model and declared targets on this artifact and fixture. Observed fitted parameters and objective values match the Python run; see the [frontend parity receipt](../../qualification/arm64-frontend-parity.json). This is a same-host qualification, not the separately requested Compose cluster or worker-container-loss acceptance.

## Common mistakes

- Interpreting the residual variance as uncertainty in the estimated regression line.
- Assuming the package constructs a multi-column design matrix or interaction terms automatically.
- Changing a future feature's meaning or units while retaining the same field mapping.

See [the gallery](../EXAMPLES.md), [preparation](../PREPARATION.md), and [custom-model
contracts](../CUSTOM-MODELS.md) for the full execution and scope boundaries. A local run is not a
cluster-scale or global-optimum guarantee.