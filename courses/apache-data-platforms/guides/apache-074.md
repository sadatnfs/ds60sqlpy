# apache-074: Graph, indexes and recovery

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-073`, `apache-069`.

## Graph persistence and search availability are different states

Atlas stores metadata relationships in a graph backend and uses indexes to
support discovery. A direct entity lookup can succeed while a search query is
stale or unavailable. Likewise, a responsive search service does not prove that
all graph mutations were durably recorded. Recovery needs a coordinated plan
for the actual selected backend and index implementation.

The pinned2.5.0 source provides graph/index configuration choices with specific
component versions. The prepared native-server runbook requires recording those
choices, their durable directories and backup procedures. A general Atlas label
is not enough to reconstruct a deployment. Default local server execution remains
omitted rather than claiming unsupported JVM or backend combinations ran here.

A restart preserves state only when the right storage survives. An in-memory
cache, a local graph directory, an external HBase deployment and a search index
have different recovery properties. Containers sharing one engine also share
one physical failure domain. A successful process replacement on that engine
cannot establish independent-host disaster recovery.

## Worked case A: retain entities and lineage through restart

After actual apply/check on the owned server, save the exact entity GUIDs,
qualified names, classifications and expected directed edge set. Stop and resume
the exact server/backing-service processes using that host's reviewed lifecycle.
Run only the read-only client check afterward. Do not reapply payloads during
persistence readback.

Require the same GUIDs and relationships, not merely the same display names.
If the graph was lost and recreated from the source, new GUIDs can expose that
different event even when the visible names look familiar. Preserve source
revision and actual image/platform identities so the result is bound to the
software that performed recovery.

Readiness can require several stages: backing database available, graph readable,
Atlas API authenticated and index catch-up complete. Use a finite deadline for
each meaningful condition and retain first-failure diagnostics. A port accepting
connections is weaker than an authenticated entity read with the expected state.

## Worked case B: distinguish index lag from missing graph data

Query an entity directly by its stable qualified name, then perform an owned
classification/type discovery query. If direct readback contains the entity while
search initially omits it, record that difference and poll discovery under a
bounded deadline. This is evidence of a read-path discrepancy; inspect actual
backend/index state before assigning a cause.

A search rebuild or index-recovery action can be operationally significant and
must follow the selected release's procedure. Do not delete graph or index
storage just to make a small fixture return quickly. Retain a consistent backup
and test recovery on a separate owned target before applying a destructive
maintenance procedure to valuable metadata.

Restore acceptance should compare entity identity, relationship direction,
classification state and discovery results. A successful file copy or database
restore command is only an intermediate event. If graph and index snapshots
represent different times, a restored service can expose inconsistent discovery
until a supported reconciliation completes.

## Diagnosis and interview discussion

Record backend versions, durable storage locations, backup cut, source revision,
entity GUIDs, edge set and search timing. State whether the failure caused lost
metadata, temporary unavailability or stale discovery. Those outcomes imply
different recovery actions and should not be collapsed into a generic restart
success flag.

**Interview discussion: why can an Atlas entity exist but be absent from search?**
Direct graph/entity access and indexed discovery can have different readiness or
consistency states. The first case requires durable identity/lineage survival,
while the second tests search separately and keeps index maintenance distinct
from graph restoration.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Atlas apache-074 prepared command notebook

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

Record actual GUIDs/edges before lifecycle changes on the separately prepared server, then run check without apply. Search/index catch-up and graph/index restore require their own bounded observations.

Prepared payloads are not actual Atlas observations. Never place credentials or
Authorization headers in notebooks, source, command arguments or receipts.

## Primary references

- [Atlas REST types/entities/lineage API](https://atlas.apache.org/api/v2/index.html)
- [Pinned type system documentation](https://github.com/apache/atlas/blob/release-2.5.0/docs/src/documents/TypeSystem.md)
- [Pinned authorization model](https://github.com/apache/atlas/blob/release-2.5.0/docs/src/documents/Security/AuthorizationModel.md)
- [Pinned installation and backing services](https://github.com/apache/atlas/blob/release-2.5.0/docs/src/documents/Setup/InstallationInstruction.md)
- [Pinned dependency/JVM contract](https://github.com/apache/atlas/blob/release-2.5.0/pom.xml)
