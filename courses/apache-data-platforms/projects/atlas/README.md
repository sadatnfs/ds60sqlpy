# Atlas 2.5.0 actual REST workshop with a separately prepared server

Default local Atlas server execution is omitted. The pinned upstream POM targets
Java 8 and explicitly warns that Java 9+ has not been tested; the classroom's
Java 17/21 images are not evidence of a supported Atlas server. No official ready
pinned Atlas image was verified. Use a separately owned compatible native host
via [PREPARATION.md](PREPARATION.md), or keep this unit as a fully explained
prepared route. No AMD64 emulation or simulated Atlas service is provided.

The Docker-contained Python client uses the actual Atlas v2 REST API. After
preparing the ordinary data-platforms-python profile, copy this directory to
`work/apache-atlas`, then:

```bash
bash run.sh prepare
bash run.sh plan
```

Plan creates a random owned namespace and prints complete type/entity payloads,
without contacting any server. Prepare validates the native portable client only.
The payload contains custom DataSet/Process subtypes, three datasets, one process,
two lineage edges and one classification. A third dataset intentionally has no
recorded process edge. This is payload preparation, not server execution.

For an explicitly owned fixture server, create an untracked `.workshop/atlas.env` with
DS60_ATLAS_ENDPOINT, DS60_ATLAS_USERNAME and DS60_ATLAS_PASSWORD. Use verified
HTTPS for remote hosts; explicit local fixture HTTP is allowed only for localhost,
127.0.0.1 or host.docker.internal. Keep credentials out of notebooks, commands,
receipts and version control. The launcher passes the environment file directly
to Docker. It does not print it. Keep `.workshop/owner` with this project.

```bash
bash run.sh apply
bash run.sh check
```

Apply writes only namespace-owned types/entities using stable qualified names.
Existing incompatible types are rejected. Check is read-only: exact active asset
identities, two expected lineage edges, absent unrecorded edge, classification,
and actual401/403 for invalid fixture credentials. It does not claim Hive hooks,
search-index recovery, data-engine enforcement or a complete lineage graph.
No requests have been run against an external server as part of source authoring.

There is no automatic remote destroy or server lifecycle action. The server owner
must retain source, actual image/platform, graph/index backup and read-only
before/after GUID/edge evidence. Remove only this random namespace's entities
after reviewing their full identities, and retain needed receipts first.

All generated ownership, lock and credential state stays under `.workshop/`,
which the existing starter/Docker/source policy excludes. Only the fixed public
client file is mounted; the strict private environment cannot replace the owner.
The whole working directory is not a container source mount.
