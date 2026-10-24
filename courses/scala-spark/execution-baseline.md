# Authored Scala and Spark execution baseline

The authored additions target the prepared worker family: Scala binary 2.13, Apache Spark 4.0.1, JDK 17 and the worker's Python 3.12 environment. Exact Scala/JDK/Python patch versions are read from an actual run receipt, not inferred from a design document. The earlier expansion plan proposed Spark 4.2.0 / Scala 2.13.18 / JDK 21; that proposal is not the runtime tuple used by these references.

Use the classroom's explicit prepared profiles: scala-jvm for language foundations, spark-local-scala or spark-local-python for Spark programs, and reading for architecture worksheets. Scala sources stage as Main.scala with object Main. Python sources stage as main.py with a main guard. Sessions use local[2], loopback driver binding, a disabled UI, two shuffle partitions and UTC where time semantics matter. No default program fetches dependencies, datasets, remote models or a cluster.

The fixed worker provides Spark and its bundled JVM/Python APIs. pandas, PyArrow and third-party connectors are not assumed available. Arrow/pandas UDF comparisons are optional until exact dependency versions and runtime acceptance are recorded. No JDBC, Kafka, cloud storage or external cluster is required by the default examples.

Every file or streaming demonstration creates its own fresh scratch directory under the current job directory. Queries are awaited with a deadline and stopped before their owned SparkSession is stopped. Cleanup removes only the root created by that demonstration; no existing checkpoint, learner directory or unrelated query is reset. Restart experiments preserve the checkpoint within the demonstration until the comparison is complete and use a separate owned namespace for incompatible changes.

Native commands are optional only when Scala 2.13 and a compatible JDK are already prepared. Compile the single learner source into a fresh local output directory, then run Main with the Scala 2.13 runner. The classroom handles that staging automatically and is the primary path. No command in a guide installs a compiler or silently launches a remote service.

A local row oracle, a successful program, an observed logical/physical plan and a cluster-performance claim are different evidence levels. Each lesson names which it demonstrates. Runtime qualification belongs to root-owned worker tests and is recorded separately in the implementation status.
