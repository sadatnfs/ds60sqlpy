# A prepared custom quadratic likelihood

This model is the original extension in native/models/custom_models.hpp. It demonstrates how a
prepared custom C++ objective participates in the same Python and Scala DataFrame APIs as the
built-in models.

## Likelihood and parameterization

\[
m_i=\beta_0+\beta_2x_i^2,\qquad y_i\sim N(m_i,\sigma^2),\qquad \sigma=e^s.
\]

The callback squares the supplied x inside the native objective and prediction hook. Curvature is
unconstrained, so both upward and downward parabolas are possible. The model validates the numerical
domain of x separately during fitting and prediction.

## The actual fixture

The shared gallery fixture contains 128 observations. Its native fit fields are `x, y`. Row identity
is `row_id`. The fixed-seed generator writes 12 significant digits of canonical precision. These are
public synthetic observations, not a production dataset.

| Stored parameter | Generating value | Optimization start |
| --- | ---: | ---: |
| `intercept` | 1 | 0.5 |
| `curvature` | 0.7 | 0.3 |
| `log_sigma` | -1.203973 | -0.5108256 |

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
    "quadratic_gaussian"
]
runtime = PreparedRuntime.from_manifest("/opt/spark-tmbad/artifact.json")
api = SparkTMBad(runtime)
training = frame(spark, recipe["training_rows"], list(recipe["training_rows"][0]), ordered=False)
spec = ModelSpec(
    "quadratic_gaussian",
    {"x": "x", "y": "y"},
    id_columns=["row_id"],
    group_columns=[],
    order_columns=[],
)
fitted = api.fit_shared(
    training.repartition(2),
    spec,
    options={**recipe["fit_options"], "initial_parameters": [0.5, 0.3, -0.510825623766]},
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

The future target evaluates the prepared quadratic mean at the supplied x. It does not extrapolate a
time process, and it does not estimate uncertainty about the curve's coefficients. See the
custom-authoring guide for the actual weighted objective callback.

## A fixed-parameter calculation

At intercept=1, curvature=0.5 and sigma=0.25, x=-2 and x=2 both have mean 3 and variance 0.0625. At
x=0 the mean is 1. This symmetry is a useful independent target check.

This calculation explains the target at stated parameters. It is distinct from the actual estimated
values recorded by a gallery execution.

## Concrete Python and Scala runs

```sh
spark-submit --master 'local[2]' --jars /opt/spark-tmbad/spark-tmbad.jar \
  python/examples/gallery/quadratic_gaussian.py \
  --manifest /opt/spark-tmbad/artifact.json --output /owned/results/quadratic_gaussian

spark-submit --master 'local[2]' \
  --class io.ds60.spark.tmbad.examples.ModelGallery \
  /opt/spark-tmbad/spark-tmbad.jar /opt/spark-tmbad/artifact.json \
  python/examples/gallery/fixtures.json quadratic_gaussian
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
| `intercept` | 0.99422807 | 0.99422807 |
| `curvature` | 0.69896809 | 0.69896809 |
| `log_sigma` | -1.293388 | sigma = 0.27433973 |

The fit converged with projected gradient norm 1.2672431e-06; raw gradient norm 1.2672431e-06. It used 14 iterations and 39 objective calls, including 0 reviewed numerical candidate rejections. Observed objective value: 16.070463. Active bound indices: `[]`.

### Observed prediction: `response`

| `row_id` | `x` | `mean` | `variance` | `sd` |
| --- | --- | --- | --- | --- |
| 1000 | -0.5 | 1.1689701 | 0.075262288 | 0.27433973 |
| 1001 | 1 | 1.6931962 | 0.075262288 | 0.27433973 |

These returned values passed the independent target formula check at the fitted parameters. Uncertainty: Gaussian observation variance; parameter uncertainty excluded.

### Observed forecast: `response`

| `row_id` | `x` | `mean` | `variance` | `sd` |
| --- | --- | --- | --- | --- |
| 1000 | -0.5 | 1.1689701 | 0.075262288 | 0.27433973 |
| 1001 | 1 | 1.6931962 | 0.075262288 | 0.27433973 |

These returned values passed the independent target formula check at the fitted parameters. Uncertainty: Gaussian observation variance; parameter uncertainty excluded.

The estimates above are actual finite-sample results, not the fixture's generating values. This local execution does not establish multi-node scale, a global optimum or general model adequacy.

Direct Scala execution passed the same model and declared targets on this artifact and fixture. Observed fitted parameters and objective values match the Python run; see the [frontend parity receipt](../../qualification/arm64-frontend-parity.json). This is a same-host qualification, not the separately requested Compose cluster or worker-container-loss acceptance.

## Common mistakes

- Supplying x squared as native field x, which would square it a second time.
- Changing the C++ objective without rebuilding the worker and source-bound manifest.
- Treating a prepared custom model as permission to compile arbitrary source inside a Spark task.

See [the gallery](../EXAMPLES.md), [preparation](../PREPARATION.md), and [custom-model
contracts](../CUSTOM-MODELS.md) for the full execution and scope boundaries. A local run is not a
cluster-scale or global-optimum guarantee.