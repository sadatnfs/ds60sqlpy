# Scala DataFrames and prepared C++/TMB likelihoods

This optional project connects a Scala Spark DataFrame to the same registered
C++ models used by the Python/R companion. Scala supplies explicit projections,
partition scheduling, bounded loss/gradient aggregation and a small driver
optimizer. TMB computes derivatives inside fresh R processes. The adapter does
not add an automatic-differentiation tape to Spark or rewrite a custom model in
Scala.

Read [the prepared-model registry guide](../REGISTERING-MODELS.md) first. The
Scala adapter consumes the [same versioned JSON CLI](../CLI-CONTRACT.md) and does
not maintain a second model schema, native-artifact loader or ABI verifier.
The declared environment is Spark 4.0.1, Scala 2.13, JDK 21, Python 3.12 and the
parent project's pinned R/TMB stack. Native model preparation remains explicit.

## Prepare and run

Prepare the parent Spark/TMB project through its [README](../README.md). Its
image must contain the current `spark_tmb.cli` module and matching registered
model receipts. A previous image from before this adapter existed needs an
explicit project rebuild. Do not bypass a source/registry mismatch.

From the repository root:

```bash
courses/advanced-spark-modeling/projects/spark-tmb/workshop build

docker run --rm --init --pull never --network none \
  --hostname ds60-scala-tmb --add-host ds60-scala-tmb:127.0.0.1 \
  --user 65534:65534 --memory 3g --cpus 2 --pids-limit 512 \
  --read-only --tmpfs /tmp:rw,exec,nosuid,size=1073741824 \
  --env 'JAVA_TOOL_OPTIONS=-Duser.home=/tmp -Divy.home=/tmp/ivy -XX:ActiveProcessorCount=2' \
  --entrypoint python ds60-spark-tmb:4.0.1-tmb1.9.25 \
  /opt/spark-tmb/scala/run.py
```

This command uses an existing prepared image and never pulls or installs a
package. Scala compilation uses the compiler and dependency jars already in
`/opt/spark/jars`. Compiled classes, the JAR, Spark scratch and temporary JSON
files live in disposable `/tmp`. No learner volume or Docker socket is mounted.
Add `--compile-only` after `run.py` to check compilation without executing the
DataFrame example. Compilation alone is not numerical or process acceptance.

Preparation may download pinned dependencies, as the parent project documents.
Execution after preparation is offline. All platforms run Linux containers;
Windows uses WSL 2. Native ARM64 evidence does not establish native AMD64,
remote-cluster or GPU behavior.

## Use the DataFrame adapter

The two original Scala files live in
[src/main/scala/ds60/spark/tmb](src/main/scala/ds60/spark/tmb/TMBDataFrame.scala). The example uses
this public adapter surface:

```scala
val objective = DataFrameObjective.prepare(
  frame,
  observationId = "event_id",
  model = "normal_mean",
  fieldColumns = Map("y" -> "measurement"),
  batchSize = 256
)
try {
  val evaluated = objective.evaluate(Vector(0.5, math.log(1.5)))
  val fitted = DriverOptimizer.fit(
    objective.evaluate,
    Vector(0.0, math.log(2.0))
  )
  require(fitted.converged)
  println(fitted.parameters)
} finally objective.close()
```

The snippet assumes a prepared image and a DataFrame containing the two named
columns. The full [Example.scala](src/main/scala/ds60/spark/tmb/Example.scala)
constructs deterministic data, executes the adapter and checks independent
mathematical oracles. It is the complete runnable reference.

`fieldColumns` maps **registered model field names** to **DataFrame column
names**. The `describe` CLI response supplies the authoritative model fields and
fixed-parameter order. In the normal model, parameters are `mu` and `log_sigma`.
The projection rejects strings, booleans, arrays and decimals as numerical model
inputs rather than silently casting them. Callers can explicitly transform and
validate such inputs before this boundary. Integer values stay integers in JSON;
Python's common registry validator enforces any declared R integer restrictions.

Observation IDs must be globally unique, nonnull strings or integers. Each
partition records count and an order-independent content digest. Later
evaluations must match that materialized ledger. The adapter persists its own
derived RDD and releases only that RDD when closed. It does not unpersist the
caller's cached DataFrame. Persisted Spark data can still be recomputed from
lineage, so provide an immutable input snapshot.

## Follow one objective evaluation

1. The driver obtains the prepared model description through `describe`.
   The initial adapter admits `independent_rows` models with no random vector.
2. Spark processes each partition as bounded batches. A batch is a transport
   unit, not a new statistical model or a separately optimized coefficient.
3. The Scala task launches the fixed Python CLI and sends a bounded JSON
   `evaluate` request. The Python boundary reuses the actual model registry,
   source/library receipts, numeric checks and R protocol.
4. R creates process-local native model state and computes the full batch loss
   and gradient through TMB. It returns detached numerical values.
5. Scala checks response identity, parameter order/digest, row count and the
   expected source/library/ABI identity. Compensated accumulators merge batch
   and partition sums. Only one bounded summary per partition reaches the driver.
6. The driver optimizer proposes a new shared vector and requests another
   complete evaluation. It never averages independently fitted coefficients.

The objective is a **sum**, with no hidden mean normalization or regularizer.
A registered model must contribute additive observation terms. Putting a global
prior or penalty inside every batch would count it repeatedly and change the
objective. Add such terms once at the driver in a reviewed extension.

There are at most 64 partitions and 64 fixed parameters in this adapter. Each
batch is limited by the common CLI's model payload bound, currently 4,096 rows,
and serialized requests/responses are bounded to one megabyte. The unique-ID
check uses a distributed key reduction; it can shuffle IDs, but does not collect
observation data on the driver. All `.collect()` calls in the adapter return
bounded ledgers or summaries.

## Optimization and independent cases

The example includes a transparent inverse-BFGS driver with an Armijo line
search, iteration/evaluation limits, a curvature safeguard and an explicit
convergence result. It is an unconstrained, low-dimensional teaching optimizer.
Use domain-safe coordinates, such as log scale, and inspect the final gradient.
A returned parameter vector is not automatically converged, identified or a
global optimum. Failed/nonfinite model evaluations stop instead of being
silently replaced with an unrelated objective value.

A positive-definite quadratic with a known optimum checks the optimizer without
Spark or TMB. The real DataFrame case fits a normal model with mean two and
maximum-likelihood variance 1.25. It compares fixed-parameter loss and both
scores with an independently written formula, then compares the fitted result
with the closed form. Unequal partition layouts, multiple batch sizes, empty
partitions, preserved caller cache and invalid projections are separate cases.

The implementation starts Python and R for each batch. JSON serialization,
process startup, repeated tape construction and Spark action scheduling can
dominate small likelihood calculations. It intentionally makes ownership and
validation explicit. It is not a speed claim or an efficient universal serving
system. A future persistent evaluator needs its own process-lifetime, cache-key,
retry and failure contract, with measurements before replacing this reference.

## Add another registered model

Add trusted C++ source and a registry entry through the parent project's
registration workflow, define independent numerical oracles, then rebuild the
prepared image. The Scala side requests the new description and supplies a
matching explicit `fieldColumns` map plus fixed parameters in the reported order.
It does not need another copied C++ template or a separate Scala registry.

The first adapter deliberately rejects `complete_groups` random-effect models.
Splitting a latent group across arbitrary row batches changes its marginal
likelihood. Use the parent complete-unit API, or design a future Scala grouped
adapter that preserves each complete independent unit and its memory bound.
Cross-unit latent covariance still requires a different mathematical algorithm.

## Evidence

Consult [QUALIFICATION.md](QUALIFICATION.md) for actual compiled/runtime evidence.
Source checks, a compiler pass, an executed small local DataFrame and a real
remote-cluster deployment are different results. An ordinary Scala classroom
pad does not automatically contain this multi-file project or the R/TMB bridge.
