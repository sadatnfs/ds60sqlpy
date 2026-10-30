# Native Spark/TMBad package

The human authorized implementation on 2026-10-29, including custom likelihood
and random-effects fitting, prediction and forecasting through Scala and Python
entrypoints. This supersedes the earlier research-only restriction.

This package is tracked and independently versioned. Coordinate its releases
with the root agent, preserving checkpoints and unrelated working changes.
Classroom 1.1.0 was built from its earlier immutable source and does not include
this package. Export that exact release tree when reproducing its source payload.
No new clones/worktrees. Do not publish the package or native artifacts
incidentally; package implementation does not authorize PyPI publication.

Use the current session's explicit ownership assignments rather than historical
agent names. Root owns versioning, shared generation, build scheduling and
release coordination. Coordinate interface changes across native/, jvm/ and
python/ before changing another owner's files. Keep integration/ self-contained
for an independently copied package directory.

Use the fixed process-worker protocol. At most one serial TMBad process is live per task attempt, containing its mutable
recording context. Independent fitting uses a fresh, successfully terminated
session for each accepted objective evaluation. Do not add JNI or runtime compilation.
No Python or R executes per row on Spark executors. Python is a driver facade.
Never collect observations or all per-group fitted models onto the driver.

Separate row-additive shared fits, complete-unit marginal fits and independent
fits. A Laplace approximation requires a qualified inner mode, positive curvature
and correct outer derivatives; it is not exact integration in general. Reject
unsupported global coupling rather than silently splitting a joint likelihood.
Prediction and forecasting must be explicitly declared by the model, including
conditioning and uncertainty scope. Preserve row identifiers; promise no global
DataFrame order. Treat data snapshot immutability as an explicit contract.

Original code is MIT. The separate native TMBad dependency retains GPL-2 terms,
notices and corresponding source archives. Do not copy Apache-licensed code into
this package and relabel it. No external package/registry publication is authorized
by merely implementing the package. Do not claim legal compatibility from a
process boundary alone.

Use native ARM64 locally, existing prepared images and one compiler/build at a
time. Ask root for the resource slot. Never contact Docker Hub locally or emulate
AMD64. Preserve every learner volume and unrelated resource. Retain numerical,
compiler, actual Spark and failure evidence separately. Use parallel agents and
no em dashes.

Maintained preparation source lives in `tooling/`. Do not rename it to `build/`:
the classroom source packager correctly excludes generated build directories.
Verify these tools remain present in the next portable source archive.
