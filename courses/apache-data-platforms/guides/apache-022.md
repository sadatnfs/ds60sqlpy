# apache-022: Cluster configuration and shared data paths

Tutorial mode. Stage: intermediate. Direct prerequisites: `apache-021`, `apache-003`.

## A path names bytes only within a filesystem contract

A client can inspect a Parquet schema while registering a table, but executor
processes later need to read the actual data. A path that exists in the client
is not automatically available in an executor. The same string can name different
bytes in different containers, machines or mount namespaces. File visibility must
therefore be part of deployment design rather than an assumption hidden inside
query construction.

The workshop places its immutable fixture under one explicit shared state path.
All native service processes and the independent client see that path. They run
on one Docker host, so this is shared local storage, not object storage or a
distributed filesystem. The project refuses to replace an existing fixture whose
checksum differs from its recorded identity, preserving unexpected state for
inspection instead of silently repairing it.

Remote object storage solves a different visibility problem: each executor can
request an object through a common URI and credentials. It introduces endpoint,
authorization, consistency, version and network dependencies. A file URI does not
become remote simply because it appears in a distributed query plan, and an object
URI does not guarantee the same version is selected on every read.

## Worked case A: one immutable shared Parquet fixture

Run paths after a successful workshop check. The client verifies the source bytes,
registers the shared location and executes a bounded count and aggregate through
Ballista. It records the exact path as project-relative context and the actual
logical source digest. The independent result must still match the 200-order
fixture rather than merely showing that a file can be opened.

Permissions matter as much as naming. A process can resolve a path and still lack
read access to a parent directory or file. The initializer creates data with the
service user's ownership, and service processes run without root privileges.
The source project is mounted read-only, while generated data and receipts live
in a distinct owned volume. This prevents an analytical query from needing write
access to maintained source files.

The same mount should appear consistently to every participating process. Mapping
one host directory to /data in one container and /warehouse in another does not
make a literal /data query portable without an explicit location mapping. Keep
logical table names separate from physical storage configuration when the system
provides a compatible catalog or provider abstraction.

## Worked case B: remove a registered file before execution

The negative path check creates a disposable copy of the tiny fixture, registers
it so planning can inspect its schema, then removes that copy before the action
executes. The resulting actual scan returns an empty listing on this prepared release.
The application rejects that missing population through its independent row-identity
oracle. A successful engine action is therefore not accepted as correct data.
The checker records this observed boundary and confirms
that the canonical fixture remains unchanged afterward.

This is an actual plan-versus-execution visibility experiment inside one container
namespace. It is not a lost remote filesystem experiment. The mechanism still
illustrates the critical contract: successful registration does not guarantee later
file availability, and a missing listing can become an empty result rather than
a thrown engine exception.
A multi-host deployment must additionally test each executor's mount or object
access independently.

A missing-file error should not trigger automatic source recreation during a
query. Doing so could replace an intentionally removed or corrupted dataset with
a new version, making a failed job appear successful against different data.
Reconciliation should compare expected identity, retained metadata and storage
state, then make any replacement an explicit authorized operation.

## Mistakes, diagnosis and interview discussion

Check the path from the process that reads it, using that process's user and
namespace. Distinguish file absence, permission failure, corrupted format and
changed contents. Keep temporary negative fixtures separate from canonical data,
and delete only their exact project-owned paths. Never point a failure experiment
at learner files or shared storage.

**Interview discussion: why can table registration succeed while a later query loses
its expected rows?** Planning may inspect metadata in the client before a later
executor scan, and the file can disappear or be invisible at that later boundary.
The two cases demonstrate both the valid shared-file contract and a real source-removal
condition detected after planning, with explicit limits on the single-host topology's conclusions.

The [complete Ballista workshop](../projects/ballista/README.md) provides the maintained files, preparation, lifecycle and exact qualification boundaries for these cases.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Data visibility and delayed failure

From the copied, prepared Ballista workshop:

```bash
bash run.sh start
bash run.sh paths
```

The positive read must match the canonical fixture. The negative case registers a
separate disposable Parquet copy, removes only that copy, and detects the actual empty result with an independent row-identity oracle while preserving the canonical source checksum.

```bash
bash run.sh check
bash run.sh evidence
```

A single-host shared mount is not a multi-host filesystem qualification. Inspect
the complete client source before adapting the paths to another storage system.

## Primary references

- [Ballista deployment](https://datafusion.apache.org/ballista/user-guide/deployment/index.html)
- [DataFusion Parquet input](https://datafusion.apache.org/python/user-guide/io/parquet.html)
