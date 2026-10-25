# Scala and Apache Spark: correct data and recoverable products

> **Study in the unified classroom:** run `./classroom` from the repository
> root, then choose **Scala and Apache Spark: correct data and recoverable products** on `/classroom`. Python, SQL and all other
> subjects share this home and workspace. Each subject has its own theme;
> prerequisites guide your choices and you set the pace. The
> [one-command setup](../../docs/one-command-classroom.md) prepares the Docker runtimes and preserves saved
> work.


This course builds from Scala language reasoning or a tested Python bridge into paired Scala/PySpark batch and finite-streaming work. The [authored manifest](lessons.json) is the file inventory consumed by the classroom. The [full design route](../../docs/expansion/plans/scala-spark.json) describes the 42-lesson progression. All 42 lessons are authored; [validation](../../docs/validation.md) defines runtime qualification, and CI artifacts record actual checks for a specific revision and platform.

## Start with a language route

Begin with [spark-001](guides/spark-001.md). A new Scala learner follows the language foundations from [spark-002](guides/spark-002.md) through [spark-010](guides/spark-010.md), learning immutable collections, explicit absence, domain states, validation ledgers, independent oracles, closure serialization and laziness. A learner already comfortable with the existing Python testing lesson can use the [PySpark bridge, spark-011](guides/spark-011.md). Both routes meet at the [session and explicit-schema lesson, spark-012](guides/spark-012.md), then the preserved [NULL-aware row pilot, spark-013](guides/spark-013.md) and [reconciled revenue capstone, spark-014](guides/spark-014.md).

The framework's prerequisite graph currently expresses AND conditions, so spark-012 retains the common structural prerequisite spark-001 and explains its actual readiness gate in the guide: demonstrate `spark-010` competence or complete the `spark-011` branch. An authored file or a reading marker does not certify that readiness.

## Run through the prepared classroom

Use the [Docker classroom workflow](../../docs/docker-classroom.md) and explicitly prepare the profile needed for the selected source. Language foundations use scala-jvm. Paired engine lessons use spark-local-scala or spark-local-python. Reading lessons need no runtime. The [execution baseline](execution-baseline.md) targets the prepared Spark 4.0.1, Scala binary 2.13 and JDK 17 family, with exact patch versions read from actual runs.

Scala programs stage as Main.scala with object Main; Python programs stage as main.py with a main guard. Default Spark programs create an owned local[2] session, use loopback driver binding, disable the UI, keep UTC time semantics explicit and stop the session in finally. No lesson opens a remote cluster, downloads data or installs a dependency. pandas/Arrow and external connectors remain separately labeled optional capabilities until provisioned and tested.

## Learn from evidence

Each new lesson supplies a substantial guide, two worked examples, six distinct progressive tasks, exact result and boundary checks, hints, a learner source, separate runnable references and explained solutions. Shared concepts have paired language implementations where appropriate. Follow explanation, prediction, attempt, one hint, inspected evidence and retrieval. Keep official solutions separate until an attempt or an explicit request.

A successful process exit is one observation. The references additionally check row identity, multiplicity, NULL state, types, values, ordering and negative cases. Physical plans, local partition behavior, measured runtime and production acceptance are separate evidence. A small local example never establishes cluster-scale speed or an unconditional exactly-once guarantee.

File and streaming demonstrations own fresh scratch roots inside their job directory. They bound inputs, await query completion, stop owned queries and remove only their own resources. Existing checkpoints, unrelated services and saved learner work are never silently reset. Use source-bound test results and CI artifacts for the exact revision and platform to establish runtime qualification, rather than inferring it from source presence.

## Continue through batch and streaming systems

Lessons [015](guides/spark-015.md) through [020](guides/spark-020.md) develop grain, joins, nested records, timestamps, windows and partition reasoning. Lessons [021](guides/spark-021.md) through [029](guides/spark-029.md) connect actual plans and metrics to shuffle, broadcast, skew, Parquet, UDF boundaries, cache lifecycle, a reconciled batch capstone and staged publication. The [deployment architecture review](guides/spark-030.md) makes the boundary between local execution and a real cluster explicit.

The finite-streaming sequence begins with [source and progress accounting](guides/spark-031.md), then covers [watermarks](guides/spark-032.md), [identity-aware deduplication](guides/spark-033.md), [bounded joins](guides/spark-034.md), [checkpoint recovery](guides/spark-035.md) and [foreachBatch publication failure and replay](guides/spark-036.md). It continues through [scenario tests](guides/spark-037.md), [observability](guides/spark-038.md) and [partition evidence](guides/spark-039.md). The [JDBC architecture chapter](guides/spark-040.md) is a reading review with literal counterexamples, not a live connector exercise. [Compatibility and rollback](guides/spark-041.md) and the [replay-safe streaming capstone](guides/spark-042.md) close the route.

## Continue into GPU data processing

The [CUDA course](../cuda/README.md) adds Python GPU dataframes and a substantial
RAPIDS Accelerator for Apache Spark sequence. Its [Spark lab](../cuda/spark/README.md)
separates CPU compatibility checks from real GPU plans, semantic parity and
end-to-end measurements. The ordinary Scala/PySpark workers here remain CPU
runtimes. A GPU-capable package or a rewritten plan alone does not establish
that an entire pipeline ran faster or preserved SQL behavior.
