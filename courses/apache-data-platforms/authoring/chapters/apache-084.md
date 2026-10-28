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
separate Atlas REST/native-server alternative. No automatic Hive 4.2/Atlas 2.5hook
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
