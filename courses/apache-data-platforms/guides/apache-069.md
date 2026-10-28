# apache-069: Types, entities and metadata identity

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-008`, `apache-063`.

## A metadata type is different from an asset instance

Atlas provides a type system for describing metadata. An entity type defines
attributes and relationships that its instances can carry. An entity represents
one asset or process and receives a GUID. A classification attaches a label and
possibly attributes to an entity. A relationship connects entities under a
specified relationship type. Keeping these concepts distinct prevents a catalog
from becoming an unstructured collection of arbitrary strings.

The inherited DataSet and Process concepts provide useful starting points for
custom types. A dataset can represent an input table or published data product;
a process can record a transformation between inputs and outputs. Subtyping
should express a stable semantic contract. Creating a new type for every run
usually confuses a type definition with an instance or version identity.

The [Atlas workshop](../projects/atlas/README.md) contains a real REST client
and complete original payloads. Default local server startup is omitted because
no compatible native Atlas 2.5.0/Java 8 stack has been qualified here. Plan produces
payloads without server contact; apply/check require an explicitly prepared
owned native server. This distinction remains visible throughout these chapters.

## Worked case A: define dataset and process contracts

The client derives a unique type prefix from a saved random owner and defines
a dataset subtype of DataSet plus a process subtype of Process. It also defines
one owned classification. The payload carries typeVersion1.0 and a deliberate
set of supertypes. Inspect it before submitting it to a real server. Existing
incompatible definitions are rejected rather than automatically migrated.

Next create raw and curated dataset instances and one transform process. Their
qualified names include the complete random owner and logical role. Atlas GUIDs
identify the stored instances, while qualified names provide a stable lookup
contract for this ingestion source. Both belong in evidence because a name can
be mistyped and a GUID can belong to another environment.

The fixture includes a third unrecorded dataset to make an intentionally absent
lineage relationship observable. That is a real metadata modeling choice, not
a claim that no external process ever touched those data. Atlas can only answer
from the information ingested into its graph and exposed under the caller's
permissions.

## Worked case B: update one asset while retaining its identity

Repeat the same intended asset ingestion using its stable qualified name. Read
back the actual GUID before and after. The expected contract is one updated
asset, not a new independent asset for each delivery attempt. A changed display
name or description should not automatically change the qualified-name identity
when the underlying asset remains the same.

A physical dataset version can require a different identity policy. For example,
a current table, a fixed Iceberg snapshot and an exported file generation are
different objects even when users call all three orders. Decide whether to model
versions as separate entities or explicit version attributes, and document how
lineage points to the selected state. A GUID alone does not encode that business
choice.

Changing an existing type also needs compatibility planning. A required attribute,
cardinality or relationship change can affect existing entities and ingestion
clients. Treat type evolution as a schema migration with validation and rollback
considerations rather than a harmless rename in a JSON template.

## Diagnosis and interview discussion

Inspect type definitions, supertypes, required attributes, qualified names,
server-assigned GUIDs and actual mutation responses. A successful HTTP exchange
is weaker than reading back the intended active entity. Keep source payload and
identity-policy decisions with the observation so future ingestion can reconcile
duplicates without deleting unrelated metadata.

**Interview discussion: why are GUID and qualifiedName both useful?** A GUID
identifies the stored Atlas instance, while a well-designed qualified name helps
an external producer locate the same logical asset across retries. These cases
separate type design, asset identity and versioning instead of using one label
for all three responsibilities.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Atlas apache-069 prepared command notebook

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

Inspect the dataset/process/classification types and stable owned qualified names. After an actual apply/check, compare GUIDs before repeating apply to observe the chosen idempotent asset contract.

Prepared payloads are not actual Atlas observations. Never place credentials or
Authorization headers in notebooks, source, command arguments or receipts.

## Primary references

- [Atlas REST types/entities/lineage API](https://atlas.apache.org/api/v2/index.html)
- [Pinned type system documentation](https://github.com/apache/atlas/blob/release-2.5.0/docs/src/documents/TypeSystem.md)
- [Pinned authorization model](https://github.com/apache/atlas/blob/release-2.5.0/docs/src/documents/Security/AuthorizationModel.md)
- [Pinned installation and backing services](https://github.com/apache/atlas/blob/release-2.5.0/docs/src/documents/Setup/InstallationInstruction.md)
- [Pinned dependency/JVM contract](https://github.com/apache/atlas/blob/release-2.5.0/pom.xml)
