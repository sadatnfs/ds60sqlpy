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

## Worked case A: publish the bounded version 0product

Create an actual Delta table containing the three known orders and retain its
version 0log/schema/file identity. Configure one owned share/schema/table pointing
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

Use the valid fixture profile for a bounded read, then require401/403 with an
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
