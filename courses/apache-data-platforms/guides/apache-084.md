# apache-084: Catalog and governance integration

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-068`, `apache-074`.

## Key terms

- **Qualified identity:** A name that includes environment, catalog, namespace, table and, where needed, snapshot, so lineage cannot connect the wrong asset.
- **Catalog entry:** A Hive Metastore or Iceberg catalog record that lets readers locate and interpret a table. It is not a governance policy.
- **Recorded governance:** Atlas entities, classifications and lineage that describe assets. They are not table commits and do not enforce access.
- **Manual registration:** Submitting catalog assets to Atlas through its API, which must state its source and scope rather than claim instrumented lineage.

## Catalog metadata and governance metadata describe different contracts

Hive Metastore or an Iceberg catalog helps a reader locate and interpret tables
and their committed state. Atlas records searchable asset, classification and
lineage metadata. An integration can connect them through explicit identities,
but neither service automatically supplies every responsibility of the other.
A catalog entry is not a complete governance policy, and an Atlas entity is not
a table commit.

A shared identity scheme should include environment, catalog, namespace, table
and where appropriate version or snapshot. Similar display names are insufficient.
Two orders tables in different catalogs can have different owners, schemas and
retention rules. Qualified metadata identity prevents a lineage edge from
accidentally connecting the wrong asset.

The course offers an actual Hive/Metastore prepared route and an explicitly
separate Atlas REST/native-server alternative. No automatic Hive 4.2/Atlas 2.5 hook
compatibility is inferred. Manual registration must describe its actual source
and scope rather than claiming complete instrumented runtime lineage.

## Worked case A: register a selected table state and process

Read a real owned table's schema, location and selected Iceberg snapshot or
external-table metadata through its supported catalog client. Construct the
Atlas dataset identity from those observed fields. Register a process whose
input and output refer to the intended source/result identities and retain the
source execution receipt separately.

Read Atlas back by qualified name and require the actual GUIDs and expected
directed edges. Compare that with the catalog's table identity and selected
state. A successful metadata write is weaker than this cross-system readback,
and a successful lineage response does not prove that the process actually
executed unless its referenced execution evidence supports that claim.

Schema changes and table replacements require an identity policy. A new snapshot
of the same table may be a version attribute or a separate modeled asset under
the chosen design. Dropping and recreating a name can create a new physical/logical
object. Preserve enough source identity to distinguish these situations rather
than updating a display label and assuming continuity.

## Worked case B: compare a label with actual denied access

Attach an owned review/sensitivity classification to the selected Atlas dataset.
Read it back and search the intended namespace under a deadline. That establishes
metadata state. Next, through a separately prepared policy-aware data engine,
issue an allowed read and an intended denied read for two valid fixture principals.
Record the actual enforcement point and policy revision.

If both data requests succeed, report that the classification did not establish
the intended denial. If Atlas itself rejects a metadata request, do not call that
a denied table query. The system must demonstrate how identity and classification
reach the relevant authorizer before a governance intention becomes an access
claim.

Access can also occur outside the governed engine through direct storage
credentials or previously shared copies. The policy scope must name those paths
and any exclusions. A catalog/lineage integration cannot erase downloaded data
or automatically remove permissions held through an unrelated system.

## Diagnosis and interview discussion

Trace catalog identity, table state, Atlas qualified name/GUID, process provenance,
classification origin and actual engine policy. Keep metadata freshness separate
from data freshness and enforcement. A stale search index and an outdated
consumer snapshot can look similar to a user while requiring different repairs.

**Interview discussion: what is the minimum evidence for a governed table
integration?** Correct cross-system identity and provenance plus actual protected
operations at the stated enforcement boundary. These cases connect observed
catalog state to recorded lineage and then test governance effects separately
instead of treating a metadata label as a universal control.

## Worked examples

### Pin the table snapshot in the lineage record

```json
{
  "typeName": "ds60_<owner>_dataset",
  "attributes": {
    "qualifiedName": "ds60://<owner>/curated",
    "name": "curated",
    "description": "demo.orders snapshot <snapshot-id>"
  }
}
```

Iceberg already records which snapshot is current, and Atlas records who produced what. Writing the snapshot ID into the Atlas description, or into a custom attribute, lets a reviewer connect a lineage edge to the exact table state that existed. Without it, lineage says the process wrote curated but not which version, and a later overwrite makes the record ambiguous.

### Read the snapshot from the table catalog

```python fragment
table = catalog.load_table("demo.orders")
snapshot = table.current_snapshot()
print(snapshot.snapshot_id, snapshot.summary.operation)
```

This PyIceberg fragment reads the current snapshot ID and its operation, such as append, from the same catalog that batch_snapshot.py uses. Compare it with the ID stored in Atlas: a mismatch means the table moved after lineage was registered. Catalog metadata says what the table is; governance metadata says what someone decided about it, and both need to name the same state.

## Complete worked source

The classroom does not execute these service commands. See the [workshop rules](../STUDY-GUIDE.md#workshop-notebooks).

# Integration apache-084 complete worked notebook

Read real catalog metadata, register explicitly sourced Atlas identities/lineage, then test the actual protected data operation separately. Metadata classification alone is not enforcement.

## What this governance receipt must hold

- The catalog, database and table names exactly as the Metastore client returned them.
- The table location, schema and selected snapshot or external table properties.
- The Atlas qualified names built from those fields, and the GUIDs Atlas assigned.
- The lineage edges read back from Atlas, with direction, input and output.
- The classification name, who attached it and when it was read back.
- Two engine requests under two fixture principals, with the enforcement point named.

The governance oracle has two halves that must not be merged. The metadata half
passes when the qualified name read back from Atlas matches the observed catalog
identity and the lineage edge points from source to result. The access half
passes only when the allowed principal reads the three orders and the denied
principal receives a typed refusal from the data engine itself. The
[shared receipt rules](../STUDY-GUIDE.md#evidence-receipts) cover naming and storage.

## Concrete source inspection

From the copied integration directory, with sibling project copies when selected:

```bash
cat ../hive/MetadataProbe.java
cat ../atlas/README.md
cat ../atlas/client.py
```

`MetadataProbe.java` checks `ds60.orders` as an `EXTERNAL_TABLE` at
`file:/warehouse/orders` with partition key `day`. Those observed fields, not a
display name, are the source for the Atlas qualified name. In `client.py`, the
`plan` action prints prepared payloads without contacting a server. A printed payload is
the request you intend to send, not an entity that Atlas accepted, so record it
separately from any server response.

## Primary references

- [Hive Metastore administration](https://hive.apache.org/docs/latest/admin/adminmanual-metastore-administration/)
- [Hive and Iceberg catalog integration](https://iceberg.apache.org/docs/latest/hive/)
- [Atlas REST entities and lineage](https://atlas.apache.org/api/v2/index.html)
- [Atlas 2.5.0 authorization model](https://github.com/apache/atlas/blob/release-2.5.0/docs/src/documents/Security/AuthorizationModel.md)
