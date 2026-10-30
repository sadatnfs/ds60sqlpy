# A shared group intercept plus AR(1) dependence

This model combines persistent between-group variation with within-group AR(1) dependence. It uses
an exact Gaussian marginal calculation and requires each complete series to stay intact.

## Likelihood and parameterization

\[
Y_t=\beta+u+z_t,\quad u\sim N(0,\tau^2),\quad z_t=\phi z_{t-1}+\epsilon_t,\quad \Sigma_{ij}=\tau^2+\frac{\sigma^2}{1-\phi^2}\phi^{|i-j|}.
\]

The native implementation uses the AR precision and a rank-one update. The independent reference
constructs the dense covariance and conditions a joint Gaussian directly. These different
calculations must agree on the marginal likelihood, derivatives and future moments.

## The actual fixture

The shared gallery fixture contains 200 observations across 10 complete groups. Its native fit
fields are `time, y`. Row identity is `row_id`, group identity is `series`, and within-group order
is `time`. The fixed-seed generator writes 12 significant digits of canonical precision. These are
public synthetic observations, not a production dataset.

| Stored parameter | Generating value | Optimization start |
| --- | ---: | ---: |
| `beta` | 0.4 | 0.3 |
| `atanh_phi` | 0.6183813 | 0.3095196 |
| `log_sigma` | -1.049822 | -0.6931472 |
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
    "gaussian_ar1_random_intercept"
]
runtime = PreparedRuntime.from_manifest("/opt/spark-tmbad/artifact.json")
api = SparkTMBad(runtime)
training = frame(spark, recipe["training_rows"], list(recipe["training_rows"][0]), ordered=True)
spec = ModelSpec(
    "gaussian_ar1_random_intercept",
    {"time": "time", "y": "y"},
    id_columns=["row_id"],
    group_columns=["series"],
    order_columns=["time"],
)
fitted = api.fit_shared(
    training.repartition(2),
    spec,
    options={
        **recipe["fit_options"],
        "initial_parameters": [0.3, 0.309519604203, -0.69314718056, -0.69314718056],
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
        {"row_id": 1000, "series": "s0", "time": 20},
        {"row_id": 1001, "series": "s0", "time": 21},
        {"row_id": 1002, "series": "s0", "time": 22},
    ],
    ["row_id", "series", "time"],
    ordered=True,
)
predicted = fitted.predict(
    requested,
    history=history,
    options={
        "target": "conditional_history",
        "columns": {"time": "time"},
        "output_prefix": "prediction_",
        "order_columns": ["time"],
        "history_columns": {"time": "time", "y": "y"},
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

If the posterior group effect has mean m_u and variance v_u, the h-step mean is beta+phi to the
h*(last-beta)+(1-phi to the h)*m_u. Variance is (1-phi to the h) squared*v_u plus the propagated
innovation variance. Adding the full group effect twice would double-count information already
present in the last observation.

## A fixed-parameter calculation

At phi=0 this model reduces to the ordinary Gaussian random-intercept model. With beta=2,
sigma=tau=1 and history [4,4], a future observation again has mean 10/3 and variance 4/3. At nonzero
phi, the last observation and posterior group effect both contribute.

This calculation explains the target at stated parameters. It is distinct from the actual estimated
values recorded by a gallery execution.

## Concrete Python and Scala runs

```sh
spark-submit --master 'local[2]' --jars /opt/spark-tmbad/spark-tmbad.jar \
  python/examples/gallery/gaussian_ar1_random_intercept.py \
  --manifest /opt/spark-tmbad/artifact.json --output /owned/results/gaussian_ar1_random_intercept

spark-submit --master 'local[2]' \
  --class io.ds60.spark.tmbad.examples.ModelGallery \
  /opt/spark-tmbad/spark-tmbad.jar /opt/spark-tmbad/artifact.json \
  python/examples/gallery/fixtures.json gaussian_ar1_random_intercept
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
| `beta` | 0.2561743 | 0.2561743 |
| `atanh_phi` | 0.6530797 | phi = 0.57373955 |
| `log_sigma` | -1.0385195 | sigma = 0.35397836 |
| `log_tau` | -0.92109393 | tau = 0.39808333 |

The fit converged with projected gradient norm 7.3733742e-07; raw gradient norm 7.3733742e-07. It
used 11 iterations and 36 objective calls, including 0 reviewed numerical candidate rejections.
Observed objective value: 87.214521. Active bound indices: `[]`.

### Observed prediction: `conditional_history`

| `row_id` | `series` | `time` | `mean` | `variance` | `sd` |
| --- | --- | --- | --- | --- | --- |
| 1000 | s0 | 20 | 0.78310111 | 0.12993396 | 0.36046353 |
| 1001 | s0 | 21 | 0.69381688 | 0.17802182 | 0.42192633 |
| 1002 | s0 | 22 | 0.64259098 | 0.19690159 | 0.44373594 |

These returned values passed the independent target formula check at the fitted parameters.
Uncertainty: posterior latent uncertainty and propagated innovations; pointwise variance excludes
parameter uncertainty.

### Observed prediction: `stationary_new_series`

| `row_id` | `series` | `time` | `mean` | `variance` | `sd` |
| --- | --- | --- | --- | --- | --- |
| 2000 | unseen | 20 | 0.2561743 | 0.34525685 | 0.58758561 |
| 2001 | unseen | 21 | 0.2561743 | 0.34525685 | 0.58758561 |
| 2002 | unseen | 22 | 0.2561743 | 0.34525685 | 0.58758561 |

These returned values passed the independent target formula check at the fitted parameters.
Uncertainty: prior shared latent plus stationary AR1 variance; future steps are correlated.

### Observed forecast: `conditional_history`

| `row_id` | `series` | `time` | `mean` | `variance` | `sd` |
| --- | --- | --- | --- | --- | --- |
| 1000 | s0 | 20 | 0.78310111 | 0.12993396 | 0.36046353 |
| 1001 | s0 | 21 | 0.69381688 | 0.17802182 | 0.42192633 |
| 1002 | s0 | 22 | 0.64259098 | 0.19690159 | 0.44373594 |

These returned values passed the independent target formula check at the fitted parameters.
Uncertainty: posterior latent uncertainty and propagated innovations; pointwise variance excludes
parameter uncertainty.

### Observed forecast: `stationary_new_series`

| `row_id` | `series` | `time` | `mean` | `variance` | `sd` |
| --- | --- | --- | --- | --- | --- |
| 2000 | unseen | 20 | 0.2561743 | 0.34525685 | 0.58758561 |
| 2001 | unseen | 21 | 0.2561743 | 0.34525685 | 0.58758561 |
| 2002 | unseen | 22 | 0.2561743 | 0.34525685 | 0.58758561 |

These returned values passed the independent target formula check at the fitted parameters.
Uncertainty: prior shared latent plus stationary AR1 variance; future steps are correlated.

The estimates above are actual finite-sample results, not the fixture's generating values. This
local execution does not establish multi-node scale, a global optimum or general model adequacy.

## Common mistakes

- Adding m_u directly to an AR forecast whose last observation already includes the same group effect.
- Interpreting sigma as a separate measurement-error scale; it is the AR innovation scale here.
- Splitting a group into time chunks and summing independent marginal likelihoods.

See [the gallery](../EXAMPLES.md), [preparation](../PREPARATION.md), and [custom-model
contracts](../CUSTOM-MODELS.md) for the full execution and scope boundaries. A local run is not a
cluster-scale or global-optimum guarantee.