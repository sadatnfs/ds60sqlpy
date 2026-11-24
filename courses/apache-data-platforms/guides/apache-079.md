# apache-079: History, changes and compatible readers

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-078`, `apache-075`.

## Key terms

- **Capability negotiation:** Agreeing which protocol and table features both client and server support, which version numbers alone do not establish.
- **Change data feed:** A Delta feature that exposes row-level inserts, updates and deletes between versions, with operation and commit metadata.
- **Deletion vector:** A Delta table feature that marks deleted rows without rewriting Parquet files, which a basic Parquet reader cannot interpret.
- **Delta format response:** A newer sharing response mode that returns Delta log actions for advanced table features, excluded by the course's portable client.

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

Current official Python 1.4.2 uses a native sharing wrapper without an inspected
Linux ARM64 wheel. The course's portable protocol client therefore supports only
basic Parquet with `minReaderVersion` 1 and explicitly excludes Delta-format, deletion
vectors and CDF. This is an intentional supported subset, not an emulated
advanced reader or a claim that protocol evolution is unnecessary.

**Execution boundary.** Case A needs a native reference server, a table writer and
an advanced client, none of which the repository provides. Case B's guard is part
of the portable client's source, the same protocol check shown in apache-076, but
it is exercised only when a server returns an unsupported protocol.

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

## Worked examples

### Reject unknown reader features before reading data

```python
import json

lines = [
    '{"protocol": {"minReaderVersion": 3, "readerFeatures": ["deletionVectors"]}}',
    '{"metaData": {"id": "fixture"}}',
]
protocol = [json.loads(line)["protocol"] for line in lines if "protocol" in line][0]
supported = protocol["minReaderVersion"] == 1 and not protocol.get("readerFeatures")
print("read data" if supported else "stop: unsupported protocol")
```

```text
stop: unsupported protocol
```

The lines imitate a query response from a table that uses deletion vectors. A reader that ignored the protocol line would download the Parquet files and return rows that the table logically deleted, which is a silent correctness bug rather than an error. The project client applies the same rule and raises before any file URL is fetched.

### Ask for history only when the table shares it

```yaml
tables:
  - name: orders
    location: "s3a://owned-fixture-bucket/orders"
    id: "81e0b600-1380-4b9a-a4db-000000000001"
    historyShared: true
```

From server-config.example.yaml, historyShared true lets recipients request older versions and change data feed ranges. Without it, a query with a version or timestamp is refused even if the client supports it. Capability is the intersection of three things: the server version, the table settings and the client implementation, so check each one before blaming the others.

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
