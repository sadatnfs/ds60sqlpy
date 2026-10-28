# apache-076: Metadata, file URLs and read paths

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-075`.

## Control responses and data bytes travel different paths

A sharing client first asks the service for table metadata and eligible files.
The service can return signed URLs granting temporary reads of those data files.
The client then retrieves bytes from storage and decodes them with a compatible
reader. A successful metadata response does not prove that the recipient can
reach the object store or interpret every advertised feature.

This split is useful for distributing large data without routing all bytes
through the sharing control service. It also introduces separate failure and
security boundaries. Service credentials, URL authorization, network egress,
file availability and file-format compatibility must each be considered. A
control endpoint returning200 is therefore weaker evidence than a completed
row-level read.

The prepared portable client implements actual basic unpartitioned Parquet responses with
minReaderVersion1. It requires verified HTTPS, rejects redirects, restricts data
hosts to an explicit allowlist and keeps bearer credentials off object requests.
It limits response size, number of files, aggregate bytes and materialized rows.
These are tutorial safeguards, not a full general-purpose sharing implementation.

## Worked case A: read the exact bounded table

The reference server returns protocol, metadata and file actions for the fixed
version. The client checks the protocol before fetching files, confirms the
version response, reads the permitted URLs and decodes Parquet with PyArrow.
It projects id, region and amount and compares exact ordered rows with the
independent three-order oracle.

A total amount of20 and count of3 provide useful cross-checks, but neither
uniquely identifies the source rows. Retain the exact logical IDs and values.
The evidence can record file count, data bytes and selected table version without
storing signed URLs. Those URLs are transient capabilities, not durable public
provenance identifiers.

The service can expose different response formats or advanced table features.
The portable route must reject an unsupported protocol, deletion-vector or
Delta-format response rather than reading only familiar Parquet files and
silently ignoring visibility rules. A reader returning plausible extra rows is
more dangerous than an explicit unsupported-feature failure.

## Worked case B: metadata succeeds while a file is unavailable

Use a separately copied owned fixture to make one referenced file unavailable
without altering the original accepted table. A control request may still return
its metadata or file action, while the object request fails. Preserve the bounded
HTTP/transport failure without printing its signed URL or bearer credential.
This is a data-plane failure, not evidence that the profile could not authenticate.

Expired URLs produce another timing boundary. A client may need a supported
refresh/requery operation tied to the same table state. Blindly retrying an old
URL forever cannot restore an expired capability. Blindly switching to the latest
table can also break reproducibility if the original request was version-pinned.
Keep refresh and snapshot policy connected.

A URL host allowlist prevents the tutorial from following arbitrary advertised
locations without an explicit expectation. It does not by itself validate every
network security property of a production recipient. A broader client needs
careful redirect, address resolution, proxy and credential-forwarding policy,
with tests for each supported storage provider.

## Diagnosis and interview discussion

Record whether failure occurred during authorization, metadata parsing, protocol
validation, file retrieval or Parquet decoding. Keep selected version and schema
with the business result. Do not bypass TLS or forward service credentials to
storage in response to an access failure; identify the actual protected boundary.

**Interview discussion: why can list and metadata requests pass while reading the
table fails?** The later object-store and format paths have separate availability,
authorization and compatibility requirements. The two cases require exact rows
for success and preserve the distinct missing-file failure when only the control
path remains healthy.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Delta Sharing apache-076 prepared command notebook

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

Check separates metadata from file retrieval, never forwards recipient Authorization to storage, and withholds signed URLs. Use a separately copied owned table for the missing-file negative experiment.

The classroom Markdown pad does not start a service. Source configuration and
unit policy fixtures are not actual reference-server receipts. Keep credentials
and signed URL query strings out of all published source and evidence.

## Primary references

- [Delta Sharing protocol](https://github.com/delta-io/delta-sharing/blob/v1.4.1/PROTOCOL.md)
- [Reference server and client examples](https://github.com/delta-io/delta-sharing/blob/v1.4.1/README.md)
- [Reference server configuration](https://github.com/delta-io/delta-sharing/blob/v1.4.1/server/src/universal/conf/delta-sharing-server.yaml.template)
- [Actual cloud signing implementation](https://github.com/delta-io/delta-sharing/blob/v1.4.1/server/src/main/scala/io/delta/sharing/server/common/CloudFileSigner.scala)
- [Current Python package dependencies](https://pypi.org/project/delta-sharing/1.4.2/)
