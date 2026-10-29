# Advanced Spark qualification boundaries

The [source-bound public receipt](qualification-public.json) records actual
native ARM64 Linux execution on 2026-10-29. Twelve PySpark programs and nine
Scala programs passed in Spark 4.0.1. Scala sources were compiled with the
prepared Scala 2.13 compiler and Java 17. The separate Catalyst project compiled
and executed both expression paths, null/type/arity cases and its actual
analyzed-to-optimized two-node-to-one-node rewrite.

These checks used one disposable local[2] container, two CPU cores, 3 GiB RAM,
no network, read-only source and temporary scratch. They touched no learner
volumes. The retained runtime image ID identifies the prepared environment;
the source hashes identify the newly authored programs evaluated within it.
An older runtime tag does not claim these new lessons were in that old release.

The focused host suite passed 29 tests covering independent mathematical
identities, generated publication and runtime admission boundaries. All 38 guides
rendered through the actual repository Markdown renderer; 205 explicit formulas
passed the offline math converter. This is renderer evidence, not browser
interaction or fresh Docker-install acceptance.

The ordinary numerical examples intentionally use tiny deterministic data.
They do not prove production cluster speed, GPU operation, arbitrary-model
identifiability or statistical calibration. Retry delivery is a modeled
counterexample rather than an injected Spark executor failure. Native AMD64
qualification remains a separate target.

The combined [Spark/Torch project](projects/spark-torch/README.md) and
[Spark/TMB project](projects/spark-tmb/README.md) require their own preparation
and receipts. Reading a chapter or storing a project command does not establish
that its runtime has been executed. Their full documentation and shared browser
admission are coordinated separately from this public-program receipt.
