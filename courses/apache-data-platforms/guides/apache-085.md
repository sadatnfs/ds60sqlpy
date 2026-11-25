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

Require exact IDs 1/2/3 and amounts 4/9/7 plus regional totals 11 and 9. The contract
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

The classroom does not execute these service commands. See the [workshop rules](../STUDY-GUIDE.md#workshop-notebooks).

# Integration apache-085 complete worked notebook

Prepare the real reference server and supported table store. Read the fixed version with exact rows, reject invalid recipient credentials and measure revocation/issued-URL limits without saving capabilities.

## What this sharing receipt must hold

- The share, schema, table and version requested, matching `fixture-contract.json`.
- The Delta table version, protocol and metadata responses the server returned.
- The data file identities read through signed URLs, recorded without query strings.
- Rows 1/2/3 with amounts 4/9/7, and regional totals 11 and 9.
- The status code for an invalid or revoked fixture recipient, with its error body.
- The observed lifetime of a URL issued before revocation, with the signing policy.

Status codes carry the oracle for this route. A 200 with exact rows for the valid
recipient and a 401 or 403 for the revoked one together show authorization at
the server. A 404 or connection error for the revoked recipient shows nothing
about authorization. An old signed URL that still returns bytes after revocation
is the expected boundary, not a failure, as long as its expiry is recorded. The
[shared receipt rules](../STUDY-GUIDE.md#evidence-receipts) cover naming and storage.

## Concrete source inspection

From the copied integration directory, with sibling project copies when selected:

```bash
cat ../delta-sharing/fixture-contract.json
cat ../delta-sharing/PREPARATION.md
```

The contract names share `ds60_fixture`, schema `tutorial`, table `orders` and
version 0, so a version 0 request with any other name is a different product.
`PREPARATION.md` explains why no local 1.4.1 server acceptance exists: the release
ships source archives without a prebuilt server, so the server must be built from
the pinned tag before any revocation test is meaningful.

## Primary references

- [Delta Sharing protocol at v1.4.1](https://github.com/delta-io/delta-sharing/blob/v1.4.1/PROTOCOL.md)
- [Reference server signed URL generation](https://github.com/delta-io/delta-sharing/blob/v1.4.1/server/src/main/scala/io/delta/sharing/server/common/CloudFileSigner.scala)
- [Reference server share configuration](https://github.com/delta-io/delta-sharing/blob/v1.4.1/server/src/universal/conf/delta-sharing-server.yaml.template)
