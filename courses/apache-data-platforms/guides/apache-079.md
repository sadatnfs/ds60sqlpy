# apache-079: History, changes and compatible readers

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-078`, `apache-075`.

## Client and server capabilities must intersect

Sharing protocols evolve to expose additional table features, history and change
reading. A client/server pair can interoperate for a primitive Parquet snapshot
while failing on a newer response format or table feature. Version numbers alone
are weaker evidence than actual supported-operation and changed-condition tests.
Record the complete relevant compatibility boundary.

A current-state read answers which records are visible at a selected snapshot.
A change feed answers which changes occurred across a supported range, often
with operation and commit metadata. Repeatedly reading the current table and
subtracting results is not automatically equivalent to a real change feed,
especially when updates, deletes, retention and schema changes occur.

Current official Python 1.4.2uses a native sharing wrapper without an inspected
LinuxARM64wheel. The course's portable protocol client therefore supports only
basic Parquet/minReaderVersion1 and explicitly excludes Delta-format, deletion
vectors and CDF. This is an intentional supported subset, not an emulated
advanced reader or a claim that protocol evolution is unnecessary.

## Worked case A: inspect a supported history or change range

Prepare a compatible native reference server, actual table writer and advanced
recipient client. Record version 0 with three orders, a later update of one amount
and a separate delete of another identity. Enable the actual supported history
or CDF configuration, then request a bounded range whose expected changes are
known independently.

Require exact operation identities and values, including the chosen update
before/after semantics where supported. A final table with two rows cannot prove
which intermediate updates occurred. Retain commit/version metadata and schema
with the change result so downstream consumers can reproduce the selected range.

Retention can remove versions or change data needed by an old consumer. A
checkpoint identifying the last consumed version must be interpreted against
the provider's retained history. If the required starting point is unavailable,
fail explicitly and use a reviewed resnapshot/reconciliation procedure rather
than silently skipping ahead.

## Worked case B: reject an unsupported protocol before data reads

Present the portable client with a real service response advertising an
unsupported minimum reader version or reader feature. It must stop before
fetching files. This demonstrates a client compatibility guard, while an actual
native server exchange remains necessary to qualify the selected advanced path.
A unit fixture exercising the guard is not a reference-server receipt.

Deletion vectors illustrate why explicit rejection matters. A naive client could
read referenced Parquet bytes while ignoring deletion information and return
rows that the table considers removed. The output may look plausible and still
violate snapshot correctness. A clear unsupported-feature error is preferable
to silently weakening visibility semantics.

A released older pure-Python client can be a portable option for a basic protocol
subset, but must keep its own dependency lock and actual acceptance. Do not label
it current or claim that it supports features introduced later. Compatibility
choices should name both the useful supported path and the omitted operations.

## Diagnosis and interview discussion

Collect table protocol/features, server release, client release/native platform,
requested range, returned state metadata and exact result identities. Separate
packaging availability from a successful import and both from an actual protocol
exchange. Native AMD64 qualification must run on native AMD64 hardware.

**Interview discussion: why can a newer table fail with a client that previously
read it correctly?** The table may have enabled a feature outside that client's
supported intersection. These cases require a real bounded advanced-history
experiment and an explicit rejection path that protects the portable reader
from silently returning an invalid snapshot.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Delta Sharing apache-079 prepared command notebook

Copy the owned Delta Sharing project and follow PREPARATION.md. Delta Sharing
belongs to Delta Lake/Linux Foundation. The offline preparation actions are:

```bash
bash run.sh prepare
bash run.sh plan
```

For a separately prepared actual owned reference server and untracked recipient
profile, the bounded native Docker protocol client runs with:

```bash
bash run.sh check
```

The portable client rejects unsupported protocol/features before data reads. Advanced CDF/Delta/deletion-vector behavior is omitted until a supported native client and real server exchange are qualified.

The classroom Markdown pad does not start a service. Source configuration and
unit policy fixtures are not actual reference-server receipts. Keep credentials
and signed URL query strings out of all published source and evidence.

## Primary references

- [Delta Sharing protocol](https://github.com/delta-io/delta-sharing/blob/v1.4.1/PROTOCOL.md)
- [Reference server and client examples](https://github.com/delta-io/delta-sharing/blob/v1.4.1/README.md)
- [Reference server configuration](https://github.com/delta-io/delta-sharing/blob/v1.4.1/server/src/universal/conf/delta-sharing-server.yaml.template)
- [Actual cloud signing implementation](https://github.com/delta-io/delta-sharing/blob/v1.4.1/server/src/main/scala/io/delta/sharing/server/common/CloudFileSigner.scala)
- [Current Python package dependencies](https://pypi.org/project/delta-sharing/1.4.2/)
