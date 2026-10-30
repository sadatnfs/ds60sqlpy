# Poisson counts with exposure

Use this likelihood for independent event counts observed over different positive exposures. An
exposure is part of the mean model, not a likelihood weight.

## Likelihood and parameterization

\[
\mu_i=e_i\exp(\beta_0+\beta_1x_i),\qquad L=\sum_i\left[\mu_i-y_i\log\mu_i+\log\Gamma(y_i+1)\right].
\]

Fitting requires x, exposure and nonnegative integer y. Prediction requires x and exposure only. The
factorial normalization is retained. The exposure must use the same scientific units in training and
future data.

## The actual fixture

The shared gallery fixture contains 128 observations. Its native fit fields are `x, exposure, y`.
Row identity is `row_id`. The fixed-seed generator writes 12 significant digits of canonical
precision. These are public synthetic observations, not a production dataset.

| Stored parameter | Generating value | Optimization start |
| --- | ---: | ---: |
| `intercept` | 0.2 | 0 |
| `slope` | 0.6 | 0.3 |

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
    "poisson_exposure"
]
runtime = PreparedRuntime.from_manifest("/opt/spark-tmbad/artifact.json")
api = SparkTMBad(runtime)
training = frame(spark, recipe["training_rows"], list(recipe["training_rows"][0]), ordered=False)
spec = ModelSpec(
    "poisson_exposure",
    {"x": "x", "exposure": "exposure", "y": "y"},
    id_columns=["row_id"],
    group_columns=[],
    order_columns=[],
)
fitted = api.fit_shared(
    training.repartition(2),
    spec,
    options={**recipe["fit_options"], "initial_parameters": [0.0, 0.3]},
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
    spark,
    [{"exposure": 1.0, "row_id": 1000, "x": -0.5}, {"exposure": 1.5, "row_id": 1001, "x": 1.0}],
    ["exposure", "row_id", "x"],
    ordered=False,
)
predicted = fitted.predict(
    requested,
    options={
        "target": "response",
        "columns": {"x": "x", "exposure": "exposure"},
        "output_prefix": "prediction_",
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
    [{"exposure": 1.0, "row_id": 1000, "x": -0.5}, {"exposure": 1.5, "row_id": 1001, "x": 1.0}],
    ["exposure", "row_id", "x"],
    ordered=False,
)
forecasts = fitted.forecast(
    history,
    future,
    options={
        "target": "response",
        "history_columns": {"x": "x", "exposure": "exposure", "y": "y"},
        "future_columns": {"x": "x", "exposure": "exposure"},
        "output_prefix": "forecast_",
    },
)
forecasts.orderBy("row_id").show()
```

The response target returns expected count, Poisson observation variance and its square root. It
assumes conditional equidispersion. The forecast hook accepts supplied future x and exposure with
empty history.

## A fixed-parameter calculation

At intercept=log(2), slope=0.5 and x=0, exposure 3 gives expected count 6 and variance 6. Doubling
exposure to 6 gives expected count 12. These quantities are counts, not rates.

This calculation explains the target at stated parameters. It is distinct from the actual estimated
values recorded by a gallery execution.

## Concrete Python and Scala runs

```sh
spark-submit --master 'local[2]' --jars /opt/spark-tmbad/spark-tmbad.jar \
  python/examples/gallery/poisson_exposure.py \
  --manifest /opt/spark-tmbad/artifact.json --output /owned/results/poisson_exposure

spark-submit --master 'local[2]' \
  --class io.ds60.spark.tmbad.examples.ModelGallery \
  /opt/spark-tmbad/spark-tmbad.jar /opt/spark-tmbad/artifact.json \
  python/examples/gallery/fixtures.json poisson_exposure
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
| `intercept` | 0.045831657 | 0.045831657 |
| `slope` | 0.6887699 | 0.6887699 |

The fit converged with projected gradient norm 5.3760556e-07; raw gradient norm 5.3760556e-07. It used 7 iterations and 21 objective calls, including 0 reviewed numerical candidate rejections. Observed objective value: 191.16398. Active bound indices: `[]`.

### Observed prediction: `response`

| `row_id` | `x` | `exposure` | `mean` | `variance` | `sd` |
| --- | --- | --- | --- | --- | --- |
| 1000 | -0.5 | 1 | 0.74189074 | 0.74189074 | 0.8613308 |
| 1001 | 1 | 1.5 | 3.1269768 | 3.1269768 | 1.768326 |

These returned values passed the independent target formula check at the fitted parameters. Uncertainty: Poisson observation variance; parameter uncertainty excluded.

### Observed forecast: `response`

| `row_id` | `x` | `exposure` | `mean` | `variance` | `sd` |
| --- | --- | --- | --- | --- | --- |
| 1000 | -0.5 | 1 | 0.74189074 | 0.74189074 | 0.8613308 |
| 1001 | 1 | 1.5 | 3.1269768 | 3.1269768 | 1.768326 |

These returned values passed the independent target formula check at the fitted parameters. Uncertainty: Poisson observation variance; parameter uncertainty excluded.

The estimates above are actual finite-sample results, not the fixture's generating values. This local execution does not establish multi-node scale, a global optimum or general model adequacy.

Direct Scala execution passed the same model and declared targets on this artifact and fixture. Observed fitted parameters and objective values match the Python run; see the [frontend parity receipt](../../qualification/arm64-frontend-parity.json). This is a same-host qualification, not the separately requested Compose cluster or worker-container-loss acceptance.

## Common mistakes

- Passing a rate as y while also providing exposure, thereby changing the likelihood.
- Using exposure as weight_column and omitting its offset contribution to the mean.
- Expecting the Poisson likelihood to estimate overdispersion; use NB2 or an appropriate random-effect model when that is the model you need.

See [the gallery](../EXAMPLES.md), [preparation](../PREPARATION.md), and [custom-model
contracts](../CUSTOM-MODELS.md) for the full execution and scope boundaries. A local run is not a
cluster-scale or global-optimum guarantee.