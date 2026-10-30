# A Bernoulli logistic likelihood

Use this model for independent binary outcomes. It estimates a probability through a logistic link
and evaluates the negative log likelihood with stable softplus terms.

## Likelihood and parameterization

\[
\eta_i=\beta_0+\beta_1x_i,\quad p_i=\frac{1}{1+e^{-\eta_i}},\quad L_i=\begin{cases}\operatorname{softplus}(-\eta_i)&y_i=1,\\\operatorname{softplus}(\eta_i)&y_i=0.\end{cases}
\]

The response must be exactly zero or one. This is a Bernoulli model, not a binomial-successes model
with a variable trial count. The declared parameter bounds and score diagnostics remain visible if a
sample is close to separation.

## The actual fixture

The shared gallery fixture contains 160 observations. Its native fit fields are `x, y`. Row identity
is `row_id`. The fixed-seed generator writes 12 significant digits of canonical precision. These are
public synthetic observations, not a production dataset.

| Stored parameter | Generating value | Optimization start |
| --- | ---: | ---: |
| `intercept` | -0.2 | 0 |
| `slope` | 0.9 | 0.3 |

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
    "bernoulli_logistic"
]
runtime = PreparedRuntime.from_manifest("/opt/spark-tmbad/artifact.json")
api = SparkTMBad(runtime)
training = frame(spark, recipe["training_rows"], list(recipe["training_rows"][0]), ordered=False)
spec = ModelSpec(
    "bernoulli_logistic",
    {"x": "x", "y": "y"},
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

The mean column is a probability, not a class decision. The variance is p(1-p) for a new Bernoulli
observation. Choosing a classification threshold or evaluating calibration is a separate analytical
decision.

## A fixed-parameter calculation

At intercept=0 and slope=1, x=0 gives probability 0.5 and variance 0.25. At x=log(3), probability is
0.75 and variance is 0.1875. At an extreme positive logit, stable tail formulas retain a small
positive variance even when the mean rounds to 1.

This calculation explains the target at stated parameters. It is distinct from the actual estimated
values recorded by a gallery execution.

## Concrete Python and Scala runs

```sh
spark-submit --master 'local[2]' --jars /opt/spark-tmbad/spark-tmbad.jar \
  python/examples/gallery/bernoulli_logistic.py \
  --manifest /opt/spark-tmbad/artifact.json --output /owned/results/bernoulli_logistic

spark-submit --master 'local[2]' \
  --class io.ds60.spark.tmbad.examples.ModelGallery \
  /opt/spark-tmbad/spark-tmbad.jar /opt/spark-tmbad/artifact.json \
  python/examples/gallery/fixtures.json bernoulli_logistic
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
| `intercept` | -0.15613691 | -0.15613691 |
| `slope` | 0.85602663 | 0.85602663 |

The fit converged with projected gradient norm 8.6638019e-07; raw gradient norm 8.6638019e-07. It
used 7 iterations and 16 objective calls, including 0 reviewed numerical candidate rejections.
Observed objective value: 101.88093. Active bound indices: `[]`.

### Observed prediction: `response`

| `row_id` | `x` | `mean` | `variance` | `sd` |
| --- | --- | --- | --- | --- |
| 1000 | -0.5 | 0.35797819 | 0.2298298 | 0.47940568 |
| 1001 | 1 | 0.66816332 | 0.2217211 | 0.4708727 |

These returned values passed the independent target formula check at the fitted parameters.
Uncertainty: Bernoulli observation variance; no parameter uncertainty; future rows conditionally
independent.

### Observed forecast: `response`

| `row_id` | `x` | `mean` | `variance` | `sd` |
| --- | --- | --- | --- | --- |
| 1000 | -0.5 | 0.35797819 | 0.2298298 | 0.47940568 |
| 1001 | 1 | 0.66816332 | 0.2217211 | 0.4708727 |

These returned values passed the independent target formula check at the fitted parameters.
Uncertainty: Bernoulli observation variance; no parameter uncertainty; future rows conditionally
independent.

The estimates above are actual finite-sample results, not the fixture's generating values. This
local execution does not establish multi-node scale, a global optimum or general model adequacy.

## Common mistakes

- Passing counts greater than one without a binomial trial-count model.
- Computing a tiny tail variance as mean*(1-mean) after mean has rounded to 1.
- Treating a parameter-bound optimum under separation as evidence of an unconstrained finite MLE.

See [the gallery](../EXAMPLES.md), [preparation](../PREPARATION.md), and [custom-model
contracts](../CUSTOM-MODELS.md) for the full execution and scope boundaries. A local run is not a
cluster-scale or global-optimum guarantee.