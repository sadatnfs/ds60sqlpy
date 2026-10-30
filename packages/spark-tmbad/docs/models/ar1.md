# A directly observed Gaussian AR(1) series

This model fits complete, ordered and independently replicated Gaussian AR(1) series. The observed
value itself is the AR state; there is no separate measurement-noise component.

## Likelihood and parameterization

\[
Y_t-\mu=\phi(Y_{t-1}-\mu)+\epsilon_t,\quad \phi=\tanh(a),\quad \epsilon_t\sim N(0,\sigma^2),\quad Y_0\sim N(\mu,\sigma^2/(1-\phi^2)).
\]

The likelihood includes the stationary initial density. Fit fields are time,y, with consecutive
integer time indices. Prediction uses an explicit lag field for one conditional step; forecasting
uses complete history and future time indices to propagate several innovations.

## The actual fixture

The shared gallery fixture contains 200 observations across 10 complete groups. Its native fit
fields are `time, y`. Row identity is `row_id`, group identity is `series`, and within-group order
is `time`. The fixed-seed generator writes 12 significant digits of canonical precision. These are
public synthetic observations, not a production dataset.

| Stored parameter | Generating value | Optimization start |
| --- | ---: | ---: |
| `mu` | 0.4 | 0.3 |
| `atanh_phi` | 0.6183813 | 0.3095196 |
| `log_sigma` | -1.049822 | -0.6931472 |

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

recipe = json.loads(Path("python/examples/gallery/fixtures.json").read_text())["cases"]["ar1"]
runtime = PreparedRuntime.from_manifest("/opt/spark-tmbad/artifact.json")
api = SparkTMBad(runtime)
training = frame(spark, recipe["training_rows"], list(recipe["training_rows"][0]), ordered=True)
spec = ModelSpec(
    "ar1",
    {"time": "time", "y": "y"},
    id_columns=["row_id"],
    group_columns=["series"],
    order_columns=["time"],
)
fitted = api.fit_shared(
    training.repartition(2),
    spec,
    options={**recipe["fit_options"], "initial_parameters": [0.3, 0.309519604203, -0.69314718056]},
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
    [{"lag": 1.11391067769, "row_id": 3000, "series": "s0"}],
    ["lag", "row_id", "series"],
    ordered=True,
)
predicted = fitted.predict(
    requested,
    options={"target": "response", "columns": {"lag": "lag"}, "output_prefix": "prediction_"},
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
        {"row_id": 1000, "series": "s0", "time": 20},
        {"row_id": 1001, "series": "s0", "time": 21},
        {"row_id": 1002, "series": "s0", "time": 22},
    ],
    ["row_id", "series", "time"],
    ordered=True,
)
forecasts = fitted.forecast(
    history,
    future,
    options={
        "target": "conditional_history",
        "history_columns": {"time": "time", "y": "y"},
        "future_columns": {"time": "time"},
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
        {"row_id": 2000, "series": "unseen", "time": 20},
        {"row_id": 2001, "series": "unseen", "time": 21},
        {"row_id": 2002, "series": "unseen", "time": 22},
    ],
    ["row_id", "series", "time"],
    ordered=True,
)
new_group = fitted.forecast(
    training.limit(0),
    unseen,
    options={
        "target": "stationary_new_series",
        "history_columns": {"time": "time", "y": "y"},
        "future_columns": {"time": "time"},
        "output_prefix": "new_group_",
    },
)
new_group.orderBy("row_id").show()
```

A conditional h-step mean is mu+phi to the h*(last-mu), with variance sigma squared times the sum of
phi to the 2j. A stationary new-series target instead has mean mu and variance sigma squared/(1-phi
squared) at each point. Future rows are correlated even though the table reports pointwise
variances.

## A fixed-parameter calculation

At mu=2, phi=-0.5, sigma=0.7 and last observation 4, the next three means are 1, 2.5 and 1.75. Their
variances are 0.49, 0.6125 and 0.643125. The alternating means are a real consequence of negative
autocorrelation.

This calculation explains the target at stated parameters. It is distinct from the actual estimated
values recorded by a gallery execution.

## Concrete Python and Scala runs

```sh
spark-submit --master 'local[2]' --jars /opt/spark-tmbad/spark-tmbad.jar \
  python/examples/gallery/ar1.py \
  --manifest /opt/spark-tmbad/artifact.json --output /owned/results/ar1

spark-submit --master 'local[2]' \
  --class io.ds60.spark.tmbad.examples.ModelGallery \
  /opt/spark-tmbad/spark-tmbad.jar /opt/spark-tmbad/artifact.json \
  python/examples/gallery/fixtures.json ar1
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
| `mu` | 0.39765228 | 0.39765228 |
| `atanh_phi` | 0.60243963 | phi = 0.53878328 |
| `log_sigma` | -1.0949781 | sigma = 0.33454692 |

The fit converged with projected gradient norm 3.1891975e-06; raw gradient norm 3.1891975e-06. It
used 10 iterations and 34 objective calls, including 0 reviewed numerical candidate rejections.
Observed objective value: 66.506551. Active bound indices: `[]`.

### Observed prediction: `response`

| `row_id` | `series` | `lag` | `mean` | `variance` | `sd` |
| --- | --- | --- | --- | --- | --- |
| 3000 | s0 | 1.1139107 | 0.78356032 | 0.11192164 | 0.33454692 |

These returned values passed the independent target formula check at the fitted parameters.
Uncertainty: one innovation variance; parameter uncertainty excluded.

### Observed forecast: `conditional_history`

| `row_id` | `series` | `time` | `mean` | `variance` | `sd` |
| --- | --- | --- | --- | --- | --- |
| 1000 | s0 | 20 | 0.78356032 | 0.11192164 | 0.33454692 |
| 1001 | s0 | 21 | 0.60557308 | 0.14441108 | 0.38001458 |
| 1002 | s0 | 22 | 0.50967653 | 0.15384236 | 0.39222743 |

These returned values passed the independent target formula check at the fitted parameters.
Uncertainty: propagated future innovations; pointwise variance, not simultaneous intervals.

### Observed forecast: `stationary_new_series`

| `row_id` | `series` | `time` | `mean` | `variance` | `sd` |
| --- | --- | --- | --- | --- | --- |
| 2000 | unseen | 20 | 0.39765228 | 0.15769995 | 0.39711453 |
| 2001 | unseen | 21 | 0.39765228 | 0.15769995 | 0.39711453 |
| 2002 | unseen | 22 | 0.39765228 | 0.15769995 | 0.39711453 |

These returned values passed the independent target formula check at the fitted parameters.
Uncertainty: stationary marginal variance; future steps are correlated.

The estimates above are actual finite-sample results, not the fixture's generating values. This
local execution does not establish multi-node scale, a global optimum or general model adequacy.

## Common mistakes

- Using storage order as time or allowing missing time steps without a different cadence model.
- Supplying future y to a forecast target that requires only time.
- Equating this directly observed AR model with the course's latent AR process plus separate measurement noise.

See [the gallery](../EXAMPLES.md), [preparation](../PREPARATION.md), and [custom-model
contracts](../CUSTOM-MODELS.md) for the full execution and scope boundaries. A local run is not a
cluster-scale or global-optimum guarantee.