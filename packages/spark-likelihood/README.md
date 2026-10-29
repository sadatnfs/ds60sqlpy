# DS60 Spark Likelihood

`ds60-spark-likelihood` is an independent Python package for fitting custom low-dimensional likelihoods with Spark and PyTorch. Spark schedules complete independent contributions, Torch differentiates local CPU float64 calculations, and a driver optimizer receives bounded numerical summaries. There is no R or classroom-server dependency.

Version 0.1.0 is the first package release. The row kernel preserves the separately tested objective, gradient, reduction, weighting, empty-partition and optimizer contracts. A distinct complete-unit protocol preserves joint likelihoods; scalar group losses must never be sent through the row-batching kernel. Cross-group latent covariance and a differentiable Spark SQL plan are different problems and are not implied by this package.

## Install from this checkout

```bash
python -m pip install ./packages/spark-likelihood
```

The core contracts use the Python standard library. Install optional dependencies explicitly before execution, never inside a fit:

```bash
python -m pip install './packages/spark-likelihood[spark,torch,scipy]'
```

The prepared classroom Spark/Torch project supplies the tested CPU Torch, Spark and SciPy environment. A source installation elsewhere also needs a compatible Java runtime for Spark. Choose the appropriate Torch distribution for the machine during environment preparation; installing the package does not promise GPU support. Native qualification records exact versions and architecture separately.

## Additive row likelihoods

```python
from pyspark.sql import SparkSession
from ds60_spark_likelihood.models import normal_mean
from ds60_spark_likelihood.spark_backend import SparkObjective
from ds60_spark_likelihood.optimization import minimize_lbfgsb

spark = SparkSession.builder.master("local[2]").appName("likelihood-example").getOrCreate()
# Each row contains model features, then a scalar target and a nonnegative weight.
rows = spark.sparkContext.parallelize([(1.0, 1.0), (2.0, 1.0), (4.0, 1.0), (7.0, 1.0)], 2)
with SparkObjective(rows, normal_mean()) as objective:
    result = minimize_lbfgsb(objective.evaluate, [0.0, 0.0])
    print(result.parameters, result.gradient_inf_norm, result.converged)
spark.stop()
```

A custom `TorchLoss` supplies one differentiable value per observation. It must be deterministic and independent of batch composition. Observations remain on executors; the driver collects bounded partition summaries. Unequal partitions carry their true weight masses. A global penalty is added once after the declared sum or weighted-mean reduction.

An optimizer success flag is not a proof of identification, correct sampling assumptions or calibrated prediction intervals. Inspect raw and projected gradient norms, bounds, numerical oracles and the scientific unit of independence.

## Development

```bash
python -m pip install -e './packages/spark-likelihood[test,scipy]'
python -m pytest packages/spark-likelihood/tests
python -m pip wheel --no-deps --no-build-isolation ./packages/spark-likelihood --wheel-dir dist
```

Build and test the wheel independently from the parent classroom application. Installed-wheel checks must not rely on a repository `PYTHONPATH` or the old compatibility imports. `ds60sqlpy.spark_likelihood` contains only migration aliases; canonical implementations live here. No PyPI publication is performed by these commands.

## Model and execution contracts

Read [objectives and complete units](docs/objectives.md), [custom model authoring](docs/custom-models.md), [the Gamma-Poisson custom group model](docs/gamma-poisson.md), and [distributed training](docs/distributed-training.md). They distinguish row likelihoods, joint independent groups, shared versus separate parameters, explicit point-prediction targets and large neural-network training. The exact Gaussian random-intercept example runs entirely in Torch; it does not require R or imply support for arbitrary Laplace approximations.

Qualification has separate layers: source tests, installed-wheel import isolation, numerical oracles, actual local Spark tasks and DataFrame/ML persistence. Native architecture and dependency versions belong to the retained execution receipts. Tiny CPU examples do not establish remote-cluster or GPU performance.

```mermaid
flowchart LR
    D[Immutable executor-side data] --> U[Bounded rows or complete units]
    O[Driver optimizer] -->|parameter vector| U
    U --> T[Local Torch differentiation]
    T -->|value, gradient, counts, weight mass| C[Bounded driver reduction]
    C -->|one global penalty| O
```

The driver receives summaries, not the observations. This diagram describes the low-dimensional likelihood path; DDP training has a separate execution and sharding contract.

## DataFrame and ML interfaces

The [DataFrame and ML guide](docs/DATAFRAME-ML.md) documents `DataFrameObjective`, `SparkLikelihoodEstimator` and `SparkLikelihoodModel`. Feature columns, target labels, row weights and unit weights have distinct roles. Complete units preserve their grouping and declared ordering. Saved models use JSON configuration, parameters and full model descriptors; they require trusted registration on load and do not deserialize executable pickles.
