## A distributed engine adds placement and coordination

DataFusion plans and executes analytical operators inside an embedding application.
Ballista uses DataFusion's execution model across a scheduler and executors. A
client constructs a query, the scheduler organizes stages and tasks, and executors
scan input and produce intermediate or final batches. Those responsibilities
introduce RPC addresses, shared data visibility, serialization compatibility and
failure handling that an embedded query does not need to solve in the same way.

The workshop uses the released Ballista 54.1.0 Python package, which contains real
native Rust scheduler and executor implementations. It runs one scheduler and one
executor as separate native processes on one container host, with an independent client
process. This is actual Ballista planning, scheduling and data transfer. It is
explicitly a single-host teaching topology, not a multi-machine cluster, replica
failover experiment or high-availability installation.

The wheel requires Linux/glibc 2.39 or newer and exactly DataFusion 54. The ordinary
classroom DataFusion 55 profile is intentionally separate. A Python import that
happens to succeed after mixing incompatible packages is not a supported version
contract. Both native AMD64 and ARM64 wheels are prepared explicitly; the launcher
refuses an unsupported architecture before obtaining an image.

## Worked case A: submit to a real scheduler

Copy the complete Ballista workshop into a fresh learner-owned directory, prepare
its image, start it and run check. The fixture contains 200 orders across east
and west regions, with a deterministic amount formula. The client registers the
shared Parquet path, constructs an ordered grouped SQL query, and collects a
bounded result from the actual scheduler/executor path.

The result oracle is calculated independently from the synthetic input records.
It checks region identities, row counts and amount totals. Query success alone
would be weaker evidence: a query could execute against a different file or lose
a group while still returning a plausible table. The project records a source
checksum and selected runtime versions alongside its answer.

The Python context is an entry point, not the location of every operator. A
collect action triggers execution and brings final batches into the client.
It should be used only when the result is intentionally small. The fixture's
aggregate has two rows; this does not imply an arbitrary large SELECT star can
be safely collected into one process.

## Worked case B: compare the embedded and scheduled paths

The same client also creates an ordinary local DataFusion 54 session over the
same file and runs the same SQL. Both outputs must equal the independent oracle.
This compares semantics under controlled source and version choices. It does not
assume that identical SQL plans use identical physical execution or that adding
a scheduler makes a tiny query faster.

The local route avoids scheduling and shuffle coordination, while Ballista can
place partitions across executor capacity. For a small file, coordination can
cost more than the arithmetic it distributes. A useful architecture decision
therefore needs workload size, concurrency, data location and operational burden,
not a rule that distributed is always more advanced or better.

The comparison also exposes the role of serialization. A custom expression or
provider known only to the local process may not have a registered codec on
scheduler and executors. A successful built-in aggregate is not proof that every
Python callback or optional extension can be shipped. Begin with supported typed
operators, then qualify each real extension boundary separately.

## Mistakes, diagnosis and interview discussion

Distinguish failure to construct a plan from failure to submit it, schedule tasks,
read data or collect output. Inspect version information and process readiness
before changing the SQL. The wrapper's default scheduler state is not a promise
that jobs survive scheduler replacement; retained fixture bytes and persisted
query history are separate contracts.

**Interview discussion: what does Ballista add to DataFusion?** It adds distributed
planning and execution coordination around DataFusion operators, including task
placement and data exchange. That creates useful scaling possibilities and new
failure surfaces. The two cases execute a real scheduled query and an embedded
control, preserving an independent correctness oracle while leaving performance
and multi-host claims to their own experiments.

The [complete Ballista workshop](../../projects/ballista/README.md) provides the maintained files, preparation, lifecycle and exact qualification boundaries for these cases.
