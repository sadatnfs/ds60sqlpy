# A nonlinear saturating-growth likelihood

This example fits a nonlinear mean curve with Gaussian observation noise. The curve rises from a
baseline toward a finite asymptote, using positive amplitude and rate parameters.

## Likelihood and parameterization

\[
m(t)=b+A(1-e^{-rt}),\quad A=e^a,\quad r=e^q,\quad \sigma=e^s,\quad Y(t)\sim N(m(t),\sigma^2),\quad t\ge0.
\]

The implementation uses expm1 for the small-time expression and AD for all parameter-dependent
terms. The fixture covers early and later times, which helps distinguish amplitude from rate. This
increasing curve is different from the TMB course's positive-amplitude exponential-decay template.

## The actual fixture

The shared gallery fixture contains 128 observations. Its native fit fields are `time, y`. Row
identity is `row_id`. The fixed-seed generator writes 12 significant digits of canonical precision.
These are public synthetic observations, not a production dataset.

| Stored parameter | Generating value | Optimization start |
| --- | ---: | ---: |
| `baseline` | 0.4 | 0.2 |
| `log_amplitude` | 0.9162907 | 0.6931472 |
| `log_rate` | -0.597837 | -0.9162907 |
| `log_sigma` | -1.609438 | -0.9162907 |

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
    "saturating_growth"
]
runtime = PreparedRuntime.from_manifest("/opt/spark-tmbad/artifact.json")
api = SparkTMBad(runtime)
training = frame(spark, recipe["training_rows"], list(recipe["training_rows"][0]), ordered=False)
spec = ModelSpec(
    "saturating_growth",
    {"time": "time", "y": "y"},
    id_columns=["row_id"],
    group_columns=[],
    order_columns=[],
)
fitted = api.fit_shared(
    training.repartition(2),
    spec,
    options={
        **recipe["fit_options"],
        "initial_parameters": [0.2, 0.69314718056, -0.916290731874, -0.916290731874],
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
history = training.limit(0)
requested = frame(
    spark,
    [{"row_id": 1000, "time": 8.0}, {"row_id": 1001, "time": 10.0}],
    ["row_id", "time"],
    ordered=False,
)
predicted = fitted.predict(
    requested,
    options={"target": "response", "columns": {"time": "time"}, "output_prefix": "prediction_"},
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
    [{"row_id": 1000, "time": 8.0}, {"row_id": 1001, "time": 10.0}],
    ["row_id", "time"],
    ordered=False,
)
forecasts = fitted.forecast(
    history,
    future,
    options={
        "target": "response",
        "history_columns": {"time": "time", "y": "y"},
        "future_columns": {"time": "time"},
        "output_prefix": "forecast_",
    },
)
forecasts.orderBy("row_id").show()
```

The forecast hook evaluates the same mean curve at supplied nonnegative future times, with empty
conditioning history. It does not include autocorrelated residuals or parameter-estimation
uncertainty. Extrapolation remains a model assumption even when numerical checks pass.

## A fixed-parameter calculation

With baseline 1, amplitude 4 and rate 0.5, the mean is 1 at time 0, about 3.52848 at time 2, and
tends to 5. If sigma=0.2, observation variance remains 0.04 at each supplied time.

This calculation explains the target at stated parameters. It is distinct from the actual estimated
values recorded by a gallery execution.

## Concrete Python and Scala runs

```sh
spark-submit --master 'local[2]' --jars /opt/spark-tmbad/spark-tmbad.jar \
  python/examples/gallery/saturating_growth.py \
  --manifest /opt/spark-tmbad/artifact.json --output /owned/results/saturating_growth

spark-submit --master 'local[2]' \
  --class io.ds60.spark.tmbad.examples.ModelGallery \
  /opt/spark-tmbad/spark-tmbad.jar /opt/spark-tmbad/artifact.json \
  python/examples/gallery/fixtures.json saturating_growth
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
| `baseline` | 0.41811528 | 0.41811528 |
| `log_amplitude` | 0.91683607 | amplitude = 2.5013637 |
| `log_rate` | -0.57286565 | rate = 0.56390716 |
| `log_sigma` | -1.7069772 | sigma = 0.18141334 |

The fit converged with projected gradient norm 2.3423736e-06; raw gradient norm 2.3423736e-06. It used 19 iterations and 66 objective calls, including 0 reviewed numerical candidate rejections. Observed objective value: -36.868949. Active bound indices: `[]`.

### Observed prediction: `response`

| `row_id` | `time` | `mean` | `variance` | `sd` |
| --- | --- | --- | --- | --- |
| 1000 | 8 | 2.8920024 | 0.0329108 | 0.18141334 |
| 1001 | 10 | 2.9105837 | 0.0329108 | 0.18141334 |

These returned values passed the independent target formula check at the fitted parameters. Uncertainty: independent Gaussian observation variance around the growth curve; no parameter uncertainty.

### Observed forecast: `response`

| `row_id` | `time` | `mean` | `variance` | `sd` |
| --- | --- | --- | --- | --- |
| 1000 | 8 | 2.8920024 | 0.0329108 | 0.18141334 |
| 1001 | 10 | 2.9105837 | 0.0329108 | 0.18141334 |

These returned values passed the independent target formula check at the fitted parameters. Uncertainty: independent Gaussian observation variance around the growth curve; no parameter uncertainty.

The estimates above are actual finite-sample results, not the fixture's generating values. This local execution does not establish multi-node scale, a global optimum or general model adequacy.

Direct Scala execution passed the same model and declared targets on this artifact and fixture. Observed fitted parameters and objective values match the Python run; see the [frontend parity receipt](../../qualification/arm64-frontend-parity.json). This is a same-host qualification, not the separately requested Compose cluster or worker-container-loss acceptance.

## Common mistakes

- Supplying a negative amplitude by putting it inside a logarithm; the prepared family requires positive amplitude.
- Trying to identify amplitude and rate from only a very short initial segment of the curve.
- Treating this increasing saturation curve as the unchanged decreasing R/TMB template.

See [the gallery](../EXAMPLES.md), [preparation](../PREPARATION.md), and [custom-model
contracts](../CUSTOM-MODELS.md) for the full execution and scope boundaries. A local run is not a
cluster-scale or global-optimum guarantee.