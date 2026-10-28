## A language binding is not a universal compatibility promise

Ballista's native implementation and Rust API use DataFusion types and execution
contracts. Its Python package wraps supported behavior and routes selected actions
to a scheduler. A Java or Scala program does not gain the complete Spark API by
connecting to a Ballista endpoint. Language, SQL dialect, wire protocol and release
compatibility are separate questions that must be answered for the chosen path.

The prepared workshop uses the released Python54.1.0 binding and its declared
DataFusion 54 dependency. Its service classes are native Rust implementations exposed
through Python, not Python simulations. The same image supplies scheduler, executors
and client, reducing one source of version mismatch. This does not make arbitrary
Python objects or callbacks serializable across the execution boundary.

A Rust application can embed the corresponding Ballista client crate, but it
needs an explicitly prepared Cargo project and dependency lock. The ordinary
classroom Rust pad contains Arrow primitives, not every Ballista or DataFusion
crate. A complete Rust client source is included as a separately prepared extension,
with its compilation and runtime status stated independently in the workshop ledger.

## Worked case A: SQL and DataFrame expressions through Python

The client executes one grouped SQL query and an equivalent supported DataFrame
expression against the same registered fixture. Both actions must return the same
ordered results and match the independent oracle. Plan construction can remain
lazy until an action such as collect or to_arrow_table requests execution.
Understand which method returns a new plan and which one actually starts work.

The route records client, scheduler and executor versions from the real package.
An import version alone would not prove a remote server matches. In this single-image
workshop the processes share prepared libraries, while a remote deployment must
inspect each service's actual version or build identity. Never compare only the
human-friendly image tag if its contents can change.

A type mismatch or unsupported function should be surfaced as its actual error.
Do not silently fall back to a local engine when distributed execution fails,
because that changes the resource and data-visibility contract. A local control
query can be useful, but its result must be labeled separately from the scheduler's
result, as it is in chapter021.

## Worked case B: read the native Rust client boundary

The included Rust extension creates a Ballista session, registers a Parquet path
and collects a bounded grouped query. The source uses the selected crate's public
API and a prepared dependency graph. It illustrates the native entry point and
ownership types without pretending that the ordinary Rust pad has those crates.
Run its explicit preparation only when the compatible project environment is ready.

A Rust client still relies on matching plan codecs and supported operators at the
remote scheduler and executors. Static compilation does not prove a query completed
on the cluster. Qualification must include an actual connection, exact result
readback and a meaningful failure, just as for Python. The source's presence is
therefore distinct from a successful native client receipt.

For other languages, a supported Arrow Flight SQL or another exposed protocol can
provide a narrower integration when explicitly configured. That does not guarantee
all client methods, catalog functions or extension features. Select the smallest
verified interface needed by the application rather than copying a familiar Spark
example and assuming its semantics transfer unchanged.

## Mistakes, diagnosis and interview discussion

Inspect the released package's API and dependency metadata instead of relying on
a development-branch tutorial. Keep client package version, native server version,
DataFusion version and wire interface together in a compatibility record. Prepare
new dependencies outside lesson execution and never install packages merely when
a learner opens the chapter.

**Interview discussion: why can a client compile or import successfully and still
fail at query execution?** The local API can be valid while a remote codec, operator,
path, authorization rule or server release is incompatible. These cases separate
actual Python execution from the separately prepared Rust extension and explain
which additional observation is required before either becomes a supported
end-to-end language route.

The [complete Ballista workshop](../../projects/ballista/README.md) provides the maintained files, preparation, lifecycle and exact qualification boundaries for these cases.
