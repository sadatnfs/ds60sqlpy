# Native Spark/TMBad package

The human authorized implementation on 2026-10-29, including custom likelihood
and random-effects fitting, prediction and forecasting through Scala and Python
entrypoints. This supersedes the earlier research-only restriction.

This package is a separate development stream. Keep it untracked and uncommitted
until root coordinates its release. Do not change the active 1.1.0 classroom
release, shared package, catalog or workflow files. No new clones/worktrees.
The local classroom source packager walks untracked packages too: root must
export the exact tracked release tree for 1.1.0 packaging instead of using this
working tree. Do not publish this package or native artifacts incidentally.

Ownership: native/ belongs to phase2_torch_likelihood_book; jvm/ belongs to
phase2_advanced_spark_book; python/, README.md and other docs belong to
native_model_python_api. Root owns docs/PROTOCOL.md, build integration and release
coordination. Coordinate boundary changes before editing another owner's files.

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
