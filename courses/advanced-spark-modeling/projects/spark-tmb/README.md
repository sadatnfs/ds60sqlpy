# Spark and prepared TMB models

This is the optional R/TMB teaching reference. The primary reusable modeling API
is [ds60-spark-likelihood](../../../../packages/spark-likelihood/README.md), which
uses Spark and PyTorch without R. This reference installs only that package's
pure core wheel to reuse validated contracts and driver optimization. Its
likelihoods remain native R/TMB operations; core-wheel import needs neither Torch
nor a classroom/server source path.

This optional companion project evaluates compiled C++/TMB likelihoods inside real Spark Python tasks. It also provides the reusable `spark_tmb` package for registered custom models. The driver receives ordinary numeric values, gradients and provenance. R objectives, automatic-differentiation tapes, DLL handles and external pointers remain inside the R process that created them.

The numerical examples use Spark `local[2]` in one Linux container. They exercise actual task serialization, Python workers, fresh R processes, compiled C++ models and aggregation. They do not establish remote-cluster performance, distributed automatic differentiation through Spark SQL, or validity for an arbitrary coupled latent model.

## Prepare the optional environment

Use a terminal at the repository root. macOS and Linux use their normal terminal; Windows uses WSL 2 with a working Linux Docker engine. Preparation requires network access to the pinned Python and R packages. Runs are offline after the image is built. The classroom starter image does not imply that this optional project is installed.

First prepare the ordinary R, Spark and Java worker images using the classroom's documented build flow. Their default local tags in this project's Dockerfile are `1.0.0`; if your prepared images use another version, set `DS60_SPARK_BASE`, `DS60_JAVA_BASE` and the R base argument accordingly. The default compiler base for this optional project is the local tag `ds60-tmb-local:dev-1.9.25`, which contains R 4.6.1 and TMB 1.9.25. To prepare it from your ordinary R image:

```bash
docker build --pull=false --progress=plain \
  --target dependencies \
  --build-arg R_BASE_IMAGE=ds60sqlpy-worker-r-statistics:1.0.0 \
  -f courses/tmb-modeling/projects/tmb-local/Dockerfile \
  -t ds60-tmb-local:dev-1.9.25 \
  courses/tmb-modeling/projects/tmb-local
```

Then prepare and run this project:

```bash
courses/advanced-spark-modeling/projects/spark-tmb/workshop build
courses/advanced-spark-modeling/projects/spark-tmb/workshop check
```

For different already prepared local image tags:

```bash
DS60_TMB_BASE=ds60-tmb-local:dev-1.9.25 \
  DS60_SPARK_BASE=ds60sqlpy-worker-spark-local-python:1.1.0 \
  DS60_JAVA_BASE=ds60sqlpy-worker-java21:1.1.0 \
  courses/advanced-spark-modeling/projects/spark-tmb/workshop build
```

The build combines native Java 21, Spark 4.0.1 and Python 3.12 with the exact R/TMB environment. It installs hash-pinned Python packages and builds/installs the reusable pure wheel offline with prepared setuptools. It checks the shared R library, compiles the original TMB examples, runs their R acceptance and performs a real pandas/rpy2/TMB regression fit. It then compiles the project-owned four-model registry and records source, library, registry and ABI identities. SciPy 1.15.3 supplies the shared Python driver optimizer; fitting never installs it. Build failure stops preparation. Do not copy `.so` files from another architecture or R/TMB environment.

Run one case without rebuilding:

```bash
courses/advanced-spark-modeling/projects/spark-tmb/workshop run group-laplace
courses/advanced-spark-modeling/projects/spark-tmb/workshop run registered-models
```

The launcher uses no network, a read-only filesystem, an ephemeral writable `/tmp`, two CPUs and 4 GiB of memory. It does not attach learner volumes or the Docker socket. Logs remain in `.workshop/spark-tmb/` even though the disposable container is removed. The process uses the image's fixed unprivileged UID 65534, with Java's home explicitly `/tmp`. Host UID mappings are unnecessary because the container writes no host-mounted output; the host terminal saves its logs. The image must already exist; `run` and `check` neither build nor pull it.

## What each case establishes

| Case | Calculation | Independent check |
| --- | --- | --- |
| `partition-normal` | One shared Normal NLL and gradient across two partition layouts | Scalar Normal log density and analytic score |
| `group-laplace` | Sum of complete independent group marginal NLLs | Exact Gaussian rank-one covariance integral and score |
| `global-normal-fit` | Shared mean and scale fitted using three distributed score evaluations | Full-data sample mean and maximum-likelihood variance |
| `rpy2-frame` | pandas conversion into embedded R, compiled regression fit, detached output | Least squares and preserved row order |
| `failure-contracts` | Python request-domain failures | Unknown model, bad values, duplicate rows, singleton legacy call and dimension rejection |
| `registered-models` | Reusable package, artifact validation, real Spark global evaluation and independent unit fits | Finite differences, Gaussian marginal oracle and separate closed-form group means |
| `prediction-models` | Typed vector parameters and declared native prediction reports | Normal/regression value, gradient and OLS oracles; no-response and undeclared-target refusals |
| `dataframe-ml` | Optional R-backed DataFrame projection, shared fitting, ML stages and Pipeline persistence | Eighteen named checks including response-free transform, artifact identity, grouping, order and cache ownership |
| `scala-dataframe` | Compiled Scala/JVM adapter using the same fixed Python/R API | Partition/gradient oracles, driver fit, lifecycle and exact envelope/registry identity refusals |

The Normal driver fit uses model-specific exact conditional updates derived from the AD score. It is not a general-purpose nonlinear optimizer. The reusable `SparkTMBObjective.evaluate` result can instead be passed to the repository's optional driver optimizer when its dependencies and model assumptions are appropriate.

The fixed examples and reusable package now share the same prepared registry runtime and source/library/ABI checks. The fixed workshop request adapter retains its two-observation teaching minimum; the registered companion permits one or more observations per complete unit. An independent fit with insufficient variation can still fail because the statistical MLE does not exist. The full check also verifies installed-wheel identity without classroom/Torch imports, executes real process cleanup failure/timeout tests and direct R integer-boundary rejection tests, and refuses inexact integer measurements before conversion.

## Shared estimation versus independent fitting

For one shared parameter vector, `SparkTMBObjective.evaluate(theta)` sums likelihood values and gradients evaluated at exactly that same vector. Parameter digests and a materialized unit ledger detect stale results, repeated or missing partitions and changed data. The root reduction adds no hidden regularizer.

`fit_independent_units(initial)` instead estimates a separate parameter vector for each complete independent unit. Those estimates are returned separately. Averaging them is not a substitute for maximizing the shared likelihood. For a random-intercept model, the declared latent vector is integrated within each complete unit. Two units that share latent covariance cannot be independently integrated and then combined with this interface.

The package checks identifiers and numeric membership. It cannot discover whether the scientific author mislabeled two correlated groups as independent. That assumption must be reviewed before execution. A technically successful result on the wrong factorization is still the wrong model.

## Extending the companion

Read [REGISTERING-MODELS.md](REGISTERING-MODELS.md) before adding a model. The supported surface is intentionally bounded: finite numeric observation vectors of equal length, declared scalar or fixed-size vector parameter blocks, and an optional random vector indexed by complete groups. Parameter matrices, data-inferred parameter dimensions, cross-unit latent covariance, arbitrary R expressions, runtime compiler options and source uploads are unsupported. Extend those contracts and their tests deliberately if a future model needs them.

The Normal-mean and random-intercept templates mirror original TMB curriculum models. The Normal-location and linear-regression templates add explicit native prediction-only branches. They use the TMB API under its own package license; no external application or historical forecasting repository source was copied here. The PyTorch likelihood course supplies complementary local mathematical investigations.

Primary references: [Spark partition evaluation](https://spark.apache.org/docs/4.0.1/api/python/reference/api/pyspark.RDD.mapPartitionsWithIndex.html), [TMB model construction](https://kaskr.github.io/adcomp/Introduction.html), and [scoped pandas/rpy2 conversion](https://rpy2.github.io/doc/latest/html/pandas.html). The TMB overview page identifies an older documentation build; the installed package and compiler acceptance, not that page's header, determine this project's exact 1.9.25 behavior.

## DataFrames, ML pipelines and JVM callers

Read [DATAFRAME-ML.md](DATAFRAME-ML.md) for `DataFrameObjective`, `TMBEstimator` and `TMBModel`, including explicit field-to-column mappings, complete-group ownership, response-free transform and source-bound JSON/Pipeline save/load. The model registry declares each prediction target and required inputs. `normal_location` predicts a conditional mean for an explicit row count without a response; `linear_regression` predicts from the declared feature vector. The original `normal_mean` and `random_intercept` models deliberately have no prediction contract and refuse generic transform.

The [Scala/JVM companion](scala/README.md) uses the same [versioned JSON CLI](CLI-CONTRACT.md). Its initial DataFrame adapter supports independent-row models only and rejects latent/group models rather than splitting them incorrectly. Native code remains behind a validated R/TMB process boundary in this implementation; a direct JVM-to-standalone-C++ backend is a separate capability and is not implied by these tests.

A shared fit repeatedly evaluates one common parameter vector across units. Independent fits return separate parameter vectors. The latter use bounded `nlminb` with relative tolerance `1e-10` and require both optimizer status zero and maximum absolute score below `1e-4`. A stricter `1e-12` relative setting produced a diagnosed singular-convergence status at an otherwise accurate regression estimate; the retained control/start comparison justified the `1e-10` choice without weakening the score threshold or rewriting failed statuses. Results retain the raw optimizer message and controls.
