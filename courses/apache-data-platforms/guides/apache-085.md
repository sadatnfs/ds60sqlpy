# apache-085: Sharing a versioned data product

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-080`, `apache-081`, `apache-084`.

## Key terms

- **Data product:** A shared dataset with a defined meaning, schema, identity, freshness, retention and access contract.
- **Consumer contract:** The provider's promises about schema, versions and compatibility that a recipient can rely on.
- **Consumer receipt:** The recipient's record of table identity, version, schema, row identity and releases, with no bearer tokens or signed URLs.
- **Revocation scope:** The set of capabilities that revoking a recipient actually removes, as opposed to data or URLs it already holds.

## A shared product needs a consumer contract

A versioned data product specifies the meaning and shape of data, who can access
it, how a consumer selects state, and what happens when the provider changes or
revokes it. Delta Sharing can supply a protocol for access, while Delta table
metadata supplies committed storage state. Product semantics still need explicit
schema, identity, freshness, retention and compatibility rules.

The prepared sharing route uses a separately prepared actual reference server
and supported table store. The portable client implements a narrow basic-Parquet
protocol path and rejects advanced features outside its capability. No local
server acceptance or advanced native ARM support is inferred from source files.
This capstone can be completed on a compatible owned native host when those
components are qualified.

A useful consumer receipt contains table identity, version, schema, row identity,
client/server release and sanitized access observations. It must not contain
bearer tokens or signed file URLs. A temporary capability is not a durable public
provenance link, and storing it can expose authority rather than improve
reproducibility.

## Worked case A: publish the bounded version 0 product

Create an actual Delta table containing the three known orders and retain its
version 0 log, schema and file identity. Configure one owned share/schema/table pointing
to that data and start the actual prepared reference server. List the expected
names, request version 0, inspect protocol/metadata and read the signed Parquet
files through the compatible client.

Require exact IDs 1/2/3 and amounts 4/9/7plus regional totals11and9. The contract
should state UTC/time units where relevant, nullability, money units and whether
IDs are unique business events or current entities. A schema that merely says
amount INT leaves important interpretation unstated.

Prepare a later version separately and require that a pinned version 0 consumer
remains reproducible while a current consumer can deliberately adopt the new
state. Record the history retention promise and what happens if an old version
expires. A durable product name cannot guarantee unlimited historical availability
without a corresponding storage/maintenance policy.

## Worked case B: validate recipient denial and its limits

Use the valid fixture profile for a bounded read, then require 401 or 403 with an
invalid or revoked fixture recipient credential. Distinguish that from a missing
file, unsupported protocol or unavailable server. Those failures do not prove
authorization worked and require different operational responses.

Measure what happens to an already issued URL under the provider's actual signing
policy. It may remain valid until its expiration even after new control requests
are denied. Downloaded bytes can persist beyond both token and URL lifetimes.
The consumer contract must state this boundary rather than promising instant
universal revocation.

A schema or feature upgrade can also break an authorized consumer. Negotiate the
supported reader intersection before enabling new Delta features or response
formats. The portable route's explicit rejection is part of correctness: ignoring
a deletion vector and returning removed rows would violate the product even
though authentication and Parquet decoding succeeded.

## Diagnosis and interview discussion

Separate business meaning, committed table state, protocol capability, recipient
policy, signed storage access and downstream retention. Keep the first failed
stage and selected version in a sanitized dossier. Do not refresh to current
state or regenerate source data during a readback that claims to reproduce an
older accepted product.

**Interview discussion: what can a provider promise when sharing a versioned
product?** A clearly scoped schema/state/access/retention contract supported by
actual compatible reads and denial tests. These cases publish one finite version
and then measure recipient/revocation boundaries without confusing protocol
access with control over every downloaded copy.

## Worked examples

### The consumer contract for version 0

```json
{
  "share": "ds60_fixture",
  "schema": "tutorial",
  "table": "orders",
  "version": 0
}
```

This fixture-contract.json is what a consumer can rely on: a named table at a fixed version with columns id, region and amount. The client checks the exact rows against an oracle after reading. Publishing a new version is a separate, announced change; consumers that pinned 0 keep their results until they choose to move.

### Bound the data a recipient will download

```python
import pyarrow as pa
import pyarrow.parquet as pq

sink = pa.BufferOutputStream()
pq.write_table(pa.table({"id": [1, 2, 3], "region": ["east", "west", "east"]}), sink)
metadata = pq.ParquetFile(pa.BufferReader(sink.getvalue())).metadata
print(metadata.num_rows, metadata.num_columns, metadata.num_row_groups)
```

```text
3 2 1
```

The Delta Sharing client reads each file footer and rejects files with too many rows, columns, row groups or metadata bytes before it materializes anything. Here the footer reports three rows, two columns and one row group. Checking footers first protects the recipient from a provider that publishes a much larger file than the contract promised.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Integration apache-085 complete worked notebook

Prepare the real reference server and supported table store. Read the fixed version with exact rows, reject invalid recipient credentials and measure revocation/issued-URL limits without saving capabilities.

## Receipt fields and independent oracle

- Source revision/hashes and exact declared input IDs, values, schema and time units.
- Actual native platform, package/image identities and owned resource namespace.
- Selected table snapshot/version, source positions or process/lineage identity as appropriate.
- Positive result against an independent oracle and a typed negative observation.
- Read-only retained-state comparison after the selected lifecycle transition.
- Cleanup/evidence-storage result and any separate prepared or unavailable feature.

For the common three-order fixture, require IDs 1/2/3 with amounts 4/9/7, total 20,
east 11 and west 9. A later fourth west order of 2 changes the current total to 22 and west
to 11 while an earlier pinned snapshot remains unchanged. Do not use this simple
oracle to claim correctness for a different pipeline without defining its
deduplication, correction and visibility semantics.

Read the selected project README and qualification ledger before commands. The
classroom does not execute Docker commands in this Markdown pad. Prepared
configuration, unit policy fixtures, successful compilation and actual service
acceptance remain different observations. Never include credentials or signed URLs.

## Concrete source inspection

From the copied integration directory, with sibling project copies when selected:

```bash
cat ../delta-sharing/fixture-contract.json
cat ../delta-sharing/PREPARATION.md
```

These inspections do not start or qualify a service. Execute only the chosen
project's complete documented owned route and retain its actual receipt.

## Primary references

- [Iceberg reliability and table state](https://iceberg.apache.org/docs/latest/reliability/)
- [Arrow data format](https://arrow.apache.org/docs/format/Columnar.html)
- [Flink stateful stream processing](https://nightlies.apache.org/flink/flink-docs-release-2.3/docs/concepts/stateful-stream-processing/)
- [Kafka delivery/transaction design](https://kafka.apache.org/44/design/design/)
- [Atlas API and metadata boundaries](https://atlas.apache.org/api/v2/index.html)
- [Delta Sharing protocol](https://github.com/delta-io/delta-sharing/blob/v1.4.1/PROTOCOL.md)
