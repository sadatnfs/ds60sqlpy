# apache-080: Operating a bounded sharing service

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-079`, `apache-075`.

## Key terms

- **Share configuration:** The server's declaration of shares, schemas and tables, which must survive a process replacement separately from the table storage.
- **Version-pinned retry:** Repeating a read for the same table version, which is safe because the read does not change the provider's table.
- **Object-store signer:** The server component that creates pre-signed URLs for a supported cloud store. A local file URI is not an interchangeable replacement.
- **Failure diagnosis:** Classifying an outage as service, configuration, storage or network unavailability before choosing a recovery action.

## Service restart, table durability and recipient recovery differ

A sharing deployment has server software, share configuration, recipient policy
and table storage. A reference-server process can be replaced while its config
and table remain. A durable table can also survive while the service is unavailable.
Treat those as different state sets and failure boundaries when writing an
operational runbook.

The prepared native-server route requires an actual compatible Scala/JVM package
and supported object-store signing path. A local file URI is not an interchangeable
replacement for a cloud signer. No source-built server or signed-data path has
been called qualified merely because its configuration template exists.
Preparation, compilation, protocol exchange and lifecycle readback need separate
receipts.

A recipient must distinguish safe read retries from state changes. A repeated
version-pinned request should preserve the intended snapshot, while switching to
current state can legitimately change rows. A timeout can leave the client
uncertain about which bytes were received, even though the read itself did not
mutate the provider's table.

**Execution boundary.** Restart, replacement and outage experiments need a prepared
reference server and its storage, which the repository does not provide. The
records described below are what to collect on that server.

## Worked case A: retain a shared version through replacement

After a real successful bounded read, save server source/package identity,
configuration identity, table ID/version and exact logical row oracle. Stop and
resume the same owned server process or container and repeat only the read.
Then replace the process over retained configuration and table storage and
repeat again. Do not rewrite the table or regenerate the fixture during readback.

Require the same three orders and selected version 0. The server container can
change while table identity remains stable. Conversely, seeing the same rows
under a newly created table ID is a different event that should not count as
retained-state acceptance. Keep logical and process identities in the dossier.

The share configuration may contain bearer/storage credentials, so evidence
should hash or describe its relevant source without exporting secret values.
A sanitized configuration contract can record table names, version policy and
storage identity. Never preserve a complete recipient profile or signed file
URL merely to make a receipt seem reproducible.

## Worked case B: distinguish missing file from unavailable server

On a separately copied owned fixture, make one advertised data file unavailable
and request the fixed version. The control path can still respond while data
retrieval fails. In a second experiment, stop the actual server and observe a
control-path transport failure before any file response. Those are different
failure locations and need different recovery actions.

Bound attempts and retain the first diagnostic. An expired URL may require a
supported refresh, a missing source file may require provider restoration, and
an unavailable service may require process/network recovery. Indefinite retries
cannot repair all three conditions and can obscure a clear operational incident.

A service-level objective should specify latency, availability and freshness for
the intended recipient workload. Tiny local read timings are not a forecast for
large object transfers or many simultaneous recipients. Measure server CPU,
metadata latency, file bytes and storage behavior separately before extrapolating
capacity or cost.

## Diagnosis and interview discussion

State whether an incident caused unavailability, stale state, missing files or
incorrect rows. Record selected snapshot, control response, data retrieval stage,
actual service identity and recovered result. Preserve owned table/configuration
state until the cause is understood and required evidence has been exported.

**Interview discussion: why is a healthy sharing process insufficient to prove
service recovery?** Its configuration or referenced table files can still be
wrong or unavailable. These cases require unchanged versioned data after
replacement and distinguish a failed data plane from a failed control service
without hiding either behind a generic restart flag.

## Worked examples

### Compare the shared table across a server replacement

```bash
cd work/delta-sharing
bash run.sh check
bash run.sh check
```

Run check before and after the reference server is resumed or replaced. Both receipts should report version 0 and the same three rows, because the table lives in object storage and the server only reads it. The server itself holds no table data, so replacing it is cheap; what must survive is the configuration naming shares and table locations, plus the storage the location points to.

### Unavailable server versus missing file

```bash
curl -s -o /dev/null -w "%{http_code}\n" \
  -H "Authorization: Bearer $RECIPIENT_TOKEN" \
  "$SHARING_ENDPOINT/shares?maxResults=1"
```

A connection error or 503 here means the server is down; recipient credentials and the table may both be fine. If this listing succeeds but a later presigned URL returns 404, the server is up but a data file was removed from storage, often by an aggressive VACUUM on the source table. These need different owners: platform operations for the first, the table owner for the second.

## Complete worked source

The classroom does not execute these service commands. See the [workshop rules](../STUDY-GUIDE.md#workshop-notebooks).

# Delta Sharing apache-080 prepared command notebook

Keep the `plan` output from the copied Delta Sharing project as your reference copy of the three expected rows:

```bash
bash run.sh prepare
bash run.sh plan
```

After the owned server resumes or is replaced, run only `check`, and never rewrite the source table first:

```bash
bash run.sh check
```

After actual server resume/replacement, run check alone and compare the same table ID/version/rows. Never rewrite the source table during retention readback. Server outage and missing-file experiments are distinct.

A server outage fails at the control endpoint, while a missing data file fails at storage. Record which call failed and its status so the two are never merged into one result.

## Primary references

- [Delta Sharing protocol](https://github.com/delta-io/delta-sharing/blob/v1.4.1/PROTOCOL.md)
- [Reference server and client examples](https://github.com/delta-io/delta-sharing/blob/v1.4.1/README.md)
- [Reference server configuration](https://github.com/delta-io/delta-sharing/blob/v1.4.1/server/src/universal/conf/delta-sharing-server.yaml.template)
- [Actual cloud signing implementation](https://github.com/delta-io/delta-sharing/blob/v1.4.1/server/src/main/scala/io/delta/sharing/server/common/CloudFileSigner.scala)
- [Current Python package dependencies](https://pypi.org/project/delta-sharing/1.4.2/)
