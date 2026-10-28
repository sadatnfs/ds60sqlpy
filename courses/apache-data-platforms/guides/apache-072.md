# apache-072: Hooks, notifications and integration

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-071`, `apache-069`.

## Metadata ingestion needs a delivery and identity contract

An Atlas hook observes supported application operations and publishes metadata
notifications. Atlas then interprets those notifications and updates its graph.
An explicit REST ingestion client takes a different path: it constructs and
submits metadata directly. Both can be useful, but manual API lineage does not
prove that a Hive hook observed an actual SQL execution.

Compatibility is specific to the hook, application, protocol, Atlas release and
dependencies. Atlas 2.5.0 carries older hook dependencies in its released build.
The course's Hive 4.2 route therefore does not automatically inherit a verified
Atlas hook. The prepared base governance workshop uses explicit REST ingestion
and names that provenance accurately.

Delivery can be delayed, repeated or interrupted. A producer needs stable asset
identity, a defined update policy and reconciliation for unknown outcomes.
A timeout after a server commit does not tell the client whether the mutation
was absent. Retrying with a new random identity can create a duplicate process
or dataset even when the first request succeeded.

## Worked case A: explicit API ingestion with provenance

Generate the owned type/entity payload with plan and retain its source digest.
Apply it only to the separately prepared fixture server. Read back each stable
qualified name and record the actual GUIDs and process edges. Describe the result
as explicit API registration from this source, including which data-state or
execution receipt the process represents.

The payload's lineage can express an intended or observed transformation, so the
producer must state which one it is. A design-time pipeline dependency differs
from a process that actually ran against a selected snapshot. Include status,
run identity and evidence references in a richer schema when the application
requires operational provenance.

A hook-based extension should observe a real supported application action and
then compare the emitted notification and Atlas readback. Merely installing a
hook jar or configuring a Kafka topic is insufficient. Verify what operations
are covered, how failures are surfaced and whether the producer blocks, retries
or drops notifications under load.

## Worked case B: retry the same logical asset

Submit the same owned dataset identities again after saving the first GUID set.
The expected result is the same logical assets, with compatible updated metadata,
not a new dataset for every attempt. Compare GUIDs and the relevant edge set
before and after. A count alone can hide a duplicate that replaced another
missing expected object in the query result.

For a process run, decide whether retries represent the same logical run or
separate attempts. A stable run key can reconcile an unknown response, while
attempt metadata can preserve diagnostics without duplicating the business
operation. There is no universally correct identity policy independent of the
workflow's semantics.

Out-of-order notifications can also overwrite newer descriptions or status if
there is no version rule. A reliable ingestion design compares event sequence,
source revision or another explicit ordering contract. Do not assume that later
HTTP arrival implies a later business fact. Keep rejected stale updates and
reconciliation decisions available for investigation.

## Diagnosis and interview discussion

Follow application operation, notification publication, transport delivery,
Atlas consumption, identity matching and graph readback separately. Determine
which stage is missing before replaying messages. Preserve the original payload
and unknown-outcome state rather than declaring a failed caller response proof
that the server performed no mutation.

**Interview discussion: does at-least-once notification delivery guarantee a clean
catalog?** No. Stable identities, compatible update semantics and reconciliation
are still required to handle duplicates and ordering. These cases distinguish
explicit API provenance from real hook instrumentation and show why delivery and
asset identity must be designed together.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Atlas apache-072 prepared command notebook

Copy the owned Atlas project and read PREPARATION.md. Default local server
execution is omitted until a supported native Java 8 graph/index stack exists.

```bash
bash run.sh prepare
bash run.sh plan
```

These actions validate a portable native Docker client and print original
payloads without contacting a server. For an explicitly prepared owned fixture
server with untracked credentials, deliberate apply and read-only check are:

```bash
bash run.sh apply
bash run.sh check
```

Repeat only deliberate apply operations when studying delivery/idempotency. For persistence readback use check alone. Record source payload/revision, logical run key, actual GUIDs and notification provenance separately.

Prepared payloads are not actual Atlas observations. Never place credentials or
Authorization headers in notebooks, source, command arguments or receipts.

## Primary references

- [Atlas REST types/entities/lineage API](https://atlas.apache.org/api/v2/index.html)
- [Pinned type system documentation](https://github.com/apache/atlas/blob/release-2.5.0/docs/src/documents/TypeSystem.md)
- [Pinned authorization model](https://github.com/apache/atlas/blob/release-2.5.0/docs/src/documents/Security/AuthorizationModel.md)
- [Pinned installation and backing services](https://github.com/apache/atlas/blob/release-2.5.0/docs/src/documents/Setup/InstallationInstruction.md)
- [Pinned dependency/JVM contract](https://github.com/apache/atlas/blob/release-2.5.0/pom.xml)
