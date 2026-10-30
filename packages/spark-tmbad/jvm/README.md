# Scala and Java Spark adapter

This directory contains the original Scala 2.13 adapter for Spark 4.0.1. It calls
an explicitly prepared native C++ worker from Spark tasks. The numerical path
uses neither Python nor R on executors. A Python application can use the same
adapter through the package's Py4J facade.

The adapter and native worker are a separately prepared package. They are not
implicitly present in ordinary classroom Spark images. See the parent
[protocol](../docs/PROTOCOL.md) and [build documentation](../README.md) before use.

## Preparation and loading

Compile with a prepared Spark 4.0.1 distribution and JDK 17 or 21:

```sh
python jvm/build.py --spark-home /opt/spark --output /prepared/spark-tmbad.jar
```

This is an offline compilation step. The receipt binds every main Scala source,
the build script, the prepared compiler classpath and the resulting JAR. The
parent package's assembly command binds that JAR to a source-bound native worker.
Supply the assembled JAR using `spark-submit --jars` or an equivalent configured
Spark classpath before creating the session. Both the declared file and the
actually loaded adapter JAR must match the artifact manifest. An arbitrary
class directory cannot satisfy prepared-JAR acceptance.

The artifact manifest contains absolute paths valid on the driver. The adapter
checks the native file's digest and distributes an immutable copy with Spark's
file-distribution API. Each task checks the artifact again, makes a private
executable copy and verifies the native registry handshake. Do not put a Python
interpreter, Rscript command, shell command or compiler flag in the worker path.
A trusted custom model is registered and compiled during preparation, never by
evaluating source supplied in a DataFrame.

## A complete normal-model fit

The following fragment assumes an existing Spark session and a prepared artifact
JSON string. Its four observations are deliberately small so the exact MLE is
known: mean 4 and variance 5.

```scala
import io.ds60.spark.tmbad.PythonBridge
import java.nio.file.{Files, Path}

val artifact = Files.readString(Path.of("/prepared/artifact.json"))
val observations = spark.sql("""
  SELECT * FROM VALUES (0L,1D),(1L,3D),(2L,5D),(3L,7D)
  AS observations(id,y)
""").repartition(3)
val specification = """{
  "model_id":"normal", "columns":{"y":"y"},
  "id_columns":["id"], "group_columns":[], "order_columns":[],
  "weight_column":null
}"""
val fitting = """{
  "initial_parameters":[3.0,0.8], "gradient_tolerance":0.00001,
  "function_tolerance":0, "batch_rows":2
}"""
val modelJson = PythonBridge.fitShared(observations, specification, artifact, fitting)
val future = spark.sql("SELECT * FROM VALUES (10L),(11L) AS future(id)")
val prediction = PythonBridge.predict(future, modelJson, artifact,
  """{"target":"response","columns":{}}""")
prediction.show()
```

The target DataFrame has no response column. The `response` target is declared by
the normal model and returns `tmbad_mean` and `tmbad_sd` alongside the requested
identity columns. The fitted JSON records convergence, score norms, counts,
weights, optimization trace and exact prepared artifact identity. It contains no
training rows. A stopped, unconverged fit is still useful diagnostic output, but
prediction rejects it unless `allow_unconverged:true` is explicitly requested for
diagnostic work. This flag does not make the fit scientifically accepted.

## Three different fitting operations

For a row model, `fitShared` sums each observation's negative log likelihood and
score over partitions. A short partition contributes fewer rows, rather than
getting the same weight as a long partition. A model declared as a complete unit
is grouped and sorted before evaluation; one complete series or latent group is
sent to the native callback. A model with latent dependence across groups cannot
be made separable by repartitioning it.

`fitGroups` estimates a separate parameter vector for every declared group and
returns a DataFrame of model JSON documents and diagnostics. It does not estimate
one common global parameter vector. Keep this model DataFrame distributed, for
example in Parquet, and pass it to `predictGroups` or `forecastGroups`. Only one
bounded model document is read on the driver to establish the common schema;
observations and the complete collection of fitted models are never collected
by the adapter.

A row weight multiplies one row contribution. A complete-unit weight must be
constant within the unit and multiplies its marginal likelihood once. A
`weighted_mean` divides the global sum by global row or unit weight mass. The L2
penalty is added once after this reduction. An optional penalty changes the
estimand and should be recorded when comparing models.

## Conditional predictions and forecasts

Use `predictConditional(history, targets, modelJson, artifact, options)` when a
model's target requires observed history, such as an existing random-intercept
group. Map `history_columns` to the declared fit fields and `columns` to the
prediction target fields. The caller supplies this history explicitly; shared
model JSON does not retain an unbounded collection of group posterior states.

Use `forecast(history, future, modelJson, artifact, options)` for a declared
forecast target, with `history_columns` and `future_columns`. AR1 targets require
complete integer time order with cadence 1. Conditional future time starts one
step after the last historical observation. Multi-step means and variances use
the native target's declared conditioning and uncertainty, not repeated calls
that silently reset the history. Future rows must be nonempty. Empty history is
accepted only for a target that declares `needs_history:false`.

Future-only groups survive the grouping operation. A missing required history or
missing independent fitted model produces a clear failure instead of dropping
rows. IDs are retained; global DataFrame output order is not promised. Sort by
IDs when displaying small results, and use joins when aligning large results.

## Resource and failure boundaries

The initial implementation deliberately has explicit bounds:

- At most 4096 input partitions for shared numerical summaries.
- At most 64 parameters, 256 numerical fields and 8192 rows in a row batch.
- A complete unit or horizon uses its registered bound, at most 256 rows.
- Independent row-model groups contain at most 8192 observations.
- Each buffered group, history or row batch has an 8 MiB conservative retained
  key/data budget in addition to the 4 MiB native JSON frame limit.
- Each task output spool is limited to 128 MiB. Repartition independent output
  work explicitly if that limit is reached; do not split a coupled horizon.
- Native stderr is capped, deadlines are bounded and task cancellation stops and
  reaps the child. No numerical output becomes visible until successful exit.
- Prepared distribution copies are capped at 16 artifacts and 256 MiB per
  SparkContext. Active copies are not evicted. A weak-context cleanup task also
  handles a missed application-end callback and retries failed owned deletions.
  New allocations wait for failed cleanup to recover.

For independent fits, `task_timeout_seconds` covers the owned executor fitting
phase across every group and objective session in that task attempt. Starting a
fresh process does not reset the budget. It does not bound driver-side
preparation, Spark scheduling or preceding upstream query stages. Lexically
owned objective sessions retain cancellation checks and close in `finally`;
closed sessions do not accumulate task-completion listeners.

The driver collects only numerical partition summaries and bounded metadata.
The adapter owns only its derived cache and leaves caller caches alone. The
caller must supply an immutable snapshot across optimization evaluations; counts,
weights and a row-data ledger detect changes in the evaluated snapshot. This is
not a transactional snapshot service for a concurrently changing external table.

The original bounded BFGS optimizer reports projected first-order stationarity,
active bounds, stalling and evaluation limits. Convergence does not establish
identifiability, a global optimum, valid uncertainty or an appropriate model.
An invalid initial evaluation aborts the fit. After a valid initial evaluation,
the line search may reject a candidate only for four reviewed native numerical
codes: `DOMAIN_ERROR`, `INNER_MODE_FAILURE`, `BAD_CURVATURE` and
`NONFINITE_EVALUATION`. Classification requires the exact request/build/model
identity, the native error exit status and EOF. No value or partial sum is
accepted for that candidate. Every shared partition still contributes its full
row/weight/data ledger, and the driver validates complete coverage before
backtracking. `fit.rejected_candidates` records how often this occurred.

Transport, schema, identity, resource, cancellation and AD invariant errors always
abort the fit. They are never caught as numerical trial failures. Independent
fits start and successfully finish a native session for each accepted objective
evaluation, so a later rejected trial cannot invalidate earlier results from a
shared process. This conservative lifecycle adds process-launch overhead. Native
inner-mode score and curvature requirements remain unchanged; choose meaningful
initial parameters and inspect model domains.

## Model gallery and validation

The Scala gallery shares deterministic fixtures with the Python gallery:

```sh
spark-submit --master 'local[2]' \
  --class io.ds60.spark.tmbad.examples.ModelGallery \
  /prepared/spark-tmbad.jar \
  /prepared/artifact.json \
  python/examples/gallery/fixtures.json normal /output/normal-scala.json
```

Replace `normal` with a registered model ID or `all`. The runner fits each model,
requires convergence, and executes every declared prediction and forecast target.
It checks finite output, exact target identity coverage and declared target
semantics. The Python gallery additionally checks independent target formulas.
A script's existence is not an executed qualification; consult retained runtime
receipts for the platform and model cases actually run.

`ContractChecks` validates the strict parser, memory bounds and original solver.
`SparkChecks` exercises real native execution, serial MLE references, weighted
reduction, partition changes, cache ownership, saved group models and response-
free outputs. Compile tests into a separate JAR against the production JAR so
prepared adapter identity stays unchanged. A local two-thread Spark run and a
same-host two-executor run are distinct from a multi-machine deployment.

For the same-host two-executor check, compile the checks separately:

```sh
python jvm/build_checks.py \
  --production-jar /prepared/spark-tmbad.jar \
  --output /prepared/checks.jar

spark-submit --master 'local-cluster[2,1,512]' \
  --driver-memory 768m \
  --conf spark.executor.memory=512m \
  --conf spark.executor.cores=1 \
  --conf spark.cores.max=2 \
  --conf spark.ui.enabled=false \
  --jars /prepared/spark-tmbad.jar \
  --class io.ds60.spark.tmbad.ExecutorChecks \
  /prepared/checks.jar /prepared/artifact.json /tmp/executors.json
```

In an offline, read-only Docker container, use `--hostname localhost`,
`JAVA_TOOL_OPTIONS='-Duser.home=/tmp -XX:ActiveProcessorCount=2'`, an executable
`/tmp`, and an owned writable `/opt/spark/work`. The qualified container supplied
that worker directory as
`--tmpfs /opt/spark/work:rw,exec,nosuid,size=128m,uid=65534,gid=65534,mode=700`.
Its limits were 3 GiB, 2 CPUs and 1024 PIDs. The observed peak was 546 processes
and threads; a 512-PID attempt produced thread-allocation failures and was not
accepted. Pass `--conf spark.executor.memory=512m` explicitly: this exact
local-cluster mode retained the 1 GiB default when only `--executor-memory` was
supplied. These are acceptance-fixture settings, not cluster-sizing advice.

Retain the structured result printed on stdout before removing a container.
Files written into a tmpfs disappear when the container stops. A numerical
`passed` marker alone is insufficient for a clean environment qualification:
check process exit, fatal diagnostics, memory events and PID-limit events too.
