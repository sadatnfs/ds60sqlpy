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

Numerical rejection is narrowly reviewed. Only an evaluation response with the
exact request/build/model binding, EOF and native exit2 can yield one of the four
allowed scientific rejection codes. Initial rejection stays fatal. Validate all
partition/ledger coverage and erase partial sums before a driver DomainFailure.
Never catch a generic SparkException as a numerical trial.

Independent objective sessions use lexical try/finally, no per-session task hook,
and one shared task deadline. Keep cancellation checks and constructor cleanup.
The prepared cache has explicit entry/byte caps, weak context references and
owned cleanup retry; do not evict artifacts used by active tasks. Compile test
classes separately so they cannot replace the prepared production adapter JAR.
Treat qualification.json as retained evidence for its exact source hashes. Update
it only after actual qualification and preserve superseded evidence externally.

Named target extensions preserve legacy post-reduction L2. New Gaussian/L1 terms
share the summed-likelihood target and divide with the likelihood under weighted
mean. Apply each prior once per fitted vector, record optimizer-coordinate measure,
and keep MAP distinct from posterior inference. Exact L1 uses its proximal/KKT
path. Equality-fixed coordinates do not enter BFGS secant updates.

ParameterSet prediction has distinct data-only provenance and never fabricates a
converged fit. Preserve fitted-model admission, declared targets, complete history
and worker/ledger/source guards when sharing prediction code. Schema2 smooth-gradient
fields may be nonzero at an L1 optimum; use its declared KKT metadata. Old
qualification receipts stay immutable and do not qualify changed source.
