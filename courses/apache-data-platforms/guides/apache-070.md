# apache-070: Lineage as recorded relationships

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-069`.

## Key terms

- **Lineage:** The graph of datasets and processes that Atlas builds from recorded inputs and outputs. A missing edge does not prove that data never moved.
- **Process entity:** An Atlas entity whose inputs and outputs lists record that a transformation related specific datasets.
- **Lineage granularity:** The level, such as table or column, at which lineage relates assets. Table-level edges do not show which rows or columns contributed.
- **Instrumentation scope:** The operations an integration actually reports. Lineage is complete only for activity within this scope.

## Lineage records a claim about an operation

Atlas lineage connects dataset and process metadata. A process with input and
output references can show that an instrumented transformation related those
assets. The graph is useful for impact analysis, discovery and investigation,
but its completeness depends on what integrations actually reported. A missing
edge does not prove that data never moved between two systems.

Lineage also has a granularity. Table-level lineage can state that an output
used an input table without proving which individual rows or columns contributed.
Column-level relationships require richer instrumentation and semantics. A
manual API process record should therefore be described as explicit recorded
metadata, not automatically generated full execution provenance.

The prepared client uses actual Atlas v2 unique-attribute and lineage endpoints.
Its plan creates raw, curated and unrecorded datasets plus one transform process.
Running plan is payload preparation only. Actual GUIDs and lineage edges exist
only after a separately prepared native server accepts the owned ingestion.
No Python graph simulation is used as evidence of Atlas behavior.

**Execution boundary.** Both cases read lineage that only a running Atlas server can
return. In this repository `bash run.sh plan` shows the process entity whose
`inputs` and `outputs` lists create the two edges; the edge sets below are the
written answer to check on a separately prepared server.

## Worked case A: record an input-process-output path

Submit the two datasets and process with references linking raw to transform and
transform to curated. Read the server-assigned GUIDs through stable qualified
names. Query lineage from curated in BOTH directions at a bounded depth and
require both expected directed relationships. An independent expected edge set
is stronger than accepting any nonempty graph response.

The process should carry enough context to identify the intended transformation:
source revision, logical operation and relevant table state or run identity as
appropriate to the chosen metadata model. Merely naming a process transform does
not reproduce its code, dependencies or inputs. Keep the execution receipt and
metadata graph related by explicit identifiers without pretending one replaces
the other.

A lineage response can include additional ancestors, descendants or authorized
objects. Compare the relevant owned subgraph rather than demanding that an entire
shared server contain only the tutorial's three nodes. Conversely, do not accept
an expected name found in an unrelated branch as proof that the intended edge
was recorded for the selected output.

## Worked case B: an intentionally missing relationship

Create the third owned dataset without connecting it to the transform process.
The prepared checker requires that its GUID does not appear in the expected
lineage path. This negative condition tests a specific recorded graph boundary.
It does not establish the global absence of every possible hidden relationship
or an uninstrumented external copy.

Suppose an analyst knows that another job copied raw data into that third asset.
The correct response is to compare job execution evidence with metadata ingestion
and determine why reporting was missing. Inventing an edge solely from a similar
name or directory location would replace evidence with an assumption. If a manual
correction is appropriate, record its source and owner explicitly.

Lineage depth and authorization filters can also make an edge absent from a
particular response. A bounded query is not necessarily a complete graph traversal.
Check the API's selected direction, depth and permissions before concluding that
ingestion failed. Preserve both the request parameters and the returned relation
identities in the evidence bundle.

## Diagnosis and interview discussion

Trace dataset identity, process identity, input/output references, mutation
response and readback. Distinguish unreported execution, incorrect qualified
names, delayed processing and filtered visibility. Replaying all metadata without
reconciling identities can create duplicates and make the graph harder to trust.

**Interview discussion: can lineage prove that a dataset contains no sensitive
source data?** Only if the relevant transformations, granularity and instrumentation
coverage support that conclusion, which a small recorded path cannot establish.
These cases show a positive process path and a deliberately absent edge while
keeping graph evidence bounded to what was actually reported.

## Worked examples

### A process entity that names its inputs and outputs

```json
{
  "guid": "-4",
  "typeName": "ds60_<owner>_process",
  "attributes": {
    "qualifiedName": "ds60://<owner>/transform",
    "name": "transform",
    "inputs": [{ "guid": "-1", "typeName": "ds60_<owner>_dataset" }],
    "outputs": [{ "guid": "-2", "typeName": "ds60_<owner>_dataset" }]
  }
}
```

This is the shape client.py sends to /api/atlas/v2/entity/bulk, with the owner prefix shown as a placeholder. Negative GUIDs are temporary references within one request; Atlas replaces them with real GUIDs and links the process to the raw and curated datasets. Lineage in Atlas exists only because something submitted this record, so a missing edge means nobody reported the operation, not that it never happened.

### Read lineage around the curated asset

```bash
curl -s -u "$ATLAS_USER:$ATLAS_PASSWORD" \
  "$DS60_ATLAS_ENDPOINT/api/atlas/v2/lineage/<curated-guid>?direction=BOTH&depth=3"
```

The response holds a guidEntityMap and a relations list of fromEntityId and toEntityId pairs. The check route requires the pairs raw to transform and transform to curated, and requires that the unrecorded dataset appears in no pair. That third rule matters: an asset that was really used but never registered stays invisible, so a clean lineage graph can still be incomplete. Use the credentials from your untracked environment, never a literal in shell history.

## Complete worked source

The classroom does not execute these service commands. See the [workshop rules](../STUDY-GUIDE.md#workshop-notebooks).

# Atlas apache-070 prepared command notebook

In the copied Atlas project, `plan` shows the `transform` process with `raw` as its input and `curated` as its output. The `unrecorded` dataset has no process at all, which makes it the negative case for lineage.

```bash
bash run.sh prepare
bash run.sh plan
```

With an owned Atlas server prepared through PREPARATION.md, these actions send the payloads and then ask for lineage around `curated` in both directions to depth 3:

```bash
bash run.sh apply
bash run.sh check
```

Check requires actual raw-to-process and process-to-curated edges and excludes the intentionally unrecorded asset from that path. This is explicit API lineage, not an automatic hook result.

Until those calls run, the edges exist only in a payload. This lineage comes from explicit API entities, so no hook or crawler is being tested.

## Primary references

- [Atlas REST types/entities/lineage API](https://atlas.apache.org/api/v2/index.html)
- [Pinned type system documentation](https://github.com/apache/atlas/blob/release-2.5.0/docs/src/documents/TypeSystem.md)
- [Pinned authorization model](https://github.com/apache/atlas/blob/release-2.5.0/docs/src/documents/Security/AuthorizationModel.md)
- [Pinned installation and backing services](https://github.com/apache/atlas/blob/release-2.5.0/docs/src/documents/Setup/InstallationInstruction.md)
- [Pinned dependency/JVM contract](https://github.com/apache/atlas/blob/release-2.5.0/pom.xml)
