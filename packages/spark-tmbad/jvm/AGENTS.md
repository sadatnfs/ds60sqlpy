# Spark/TMBad JVM ownership

This is a new, separately qualified package stream. Preserve the active classroom
release and do not edit its catalogs, workflows, image defaults or progress IDs.
The JVM implementation owns only this directory. Native worker and Python facade
owners coordinate through the parent package's PROTOCOL.md. Do not invent wire
fields or silently change declared model semantics.

Use Spark 4.0.1, Scala 2.13 and prepared JDK 17 or compatible JDK 21. Compile with
existing Spark jars offline; do not download dependencies while evaluating a model.
Executors launch the prepared C++ worker directly, without Python or R. Require
exact artifact/manifest/source/ABI and request identity, bounded frames and logs,
successful process exit, deadlines, cancellation and descendant cleanup.

A row-additive shared objective, a complete-unit marginal objective and separate
per-group fitting are different operations. Preserve those distinctions and apply
normalization/penalties once. Never collect raw observations to the driver.
Prediction and forecasting must use declared targets and explicit supplied fields;
a likelihood alone does not define either operation. Shared model JSON must not
hide raw training rows or an unbounded group-posterior collection.

Keep IDs in outputs, enforce within-unit ordering where required, and make no
promise about global DataFrame row order. Record actual scale, native platform,
compiler/runtime versions and numerical oracles. A parsed source or host solver
test is not native worker, Spark or multi-host qualification. No em dashes.
