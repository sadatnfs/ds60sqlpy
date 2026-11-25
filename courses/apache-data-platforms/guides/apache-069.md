# apache-069: Types, entities and metadata identity

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-008`, `apache-063`.

## Key terms

- **Entity type:** An Atlas type definition that declares the attributes and relationships its instances can carry, often inheriting from DataSet or Process.
- **Entity:** One instance of an entity type representing an asset or process, stored with a server-assigned GUID.
- **GUID:** The globally unique identifier Atlas assigns to a stored entity instance.
- **qualifiedName:** The unique attribute a producer sets so that retries can locate the same logical asset without knowing its GUID.
- **Relationship type:** A typed definition of how two entity types connect, such as a process to its input and output datasets.

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
one owned classification. The payload carries `typeVersion` 1.0 and a deliberate
set of supertypes. Inspect it before submitting it to a real server. `bash run.sh
plan` prints exactly what this function returns, with no server involved:

From [`projects/atlas/client.py`](../projects/atlas/client.py):

```python
def payloads():
    types = {
        "entityDefs": [
            {"name": DATASET, "superTypes": ["DataSet"], "typeVersion": "1.0", "attributeDefs": []},
            {"name": PROCESS, "superTypes": ["Process"], "typeVersion": "1.0", "attributeDefs": []},
        ],
        "classificationDefs": [
            {"name": LABEL, "superTypes": [], "typeVersion": "1.0", "attributeDefs": []}
        ],
    }
    entities = []
    for number, key in enumerate(["raw", "curated", "unrecorded"], 1):
        entity = {
            "guid": str(-number),
            "typeName": DATASET,
            "attributes": {
                "qualifiedName": NAMES[key],
                "name": key,
                "description": "Synthetic owned Atlas tutorial asset",
            },
        }
        if key == "curated":
            entity["classifications"] = [{"typeName": LABEL}]
        entities.append(entity)
    entities.append(
        {
            "guid": "-4",
            "typeName": PROCESS,
            "attributes": {
                "qualifiedName": NAMES["transform"],
                "name": "transform",
                "inputs": [{"guid": "-1", "typeName": DATASET}],
                "outputs": [{"guid": "-2", "typeName": DATASET}],
            },
        }
    )
    return {"types": types, "entities": {"entities": entities}}
```

Negative `guid` values such as `"-1"` are placeholders that let one request refer
to entities it is creating; the server replaces them with real GUIDs. Existing
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

This case needs a separately prepared Atlas server, which the repository does not
provide; the GUID comparison below is what to record on such a server, not a result
reproduced here. Repeat the same intended asset ingestion using its stable qualified name. Read
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

The classroom does not execute these service commands. See the [workshop rules](../STUDY-GUIDE.md#workshop-notebooks).

# Atlas apache-069 prepared command notebook

`plan` prints the definitions and entities from `client.py` without any network call: an owned DataSet subtype, a Process subtype and a classification, plus raw, curated and unrecorded datasets. Copy the Atlas project and read PREPARATION.md first, since no local server is provided.

```bash
bash run.sh prepare
bash run.sh plan
```

Only a separately prepared Atlas 2.5.0 server with fixture credentials can receive these payloads. `apply` creates any missing types and posts the entities in bulk, and `check` reads them back by qualified name:

```bash
bash run.sh apply
bash run.sh check
```

Inspect the dataset/process/classification types and stable owned qualified names. After an actual apply/check, compare GUIDs before repeating apply to observe the chosen idempotent asset contract.

A printed plan is a prepared payload, not an Atlas observation. Your receipt should hold the GUID for each qualified name after the first apply and again after the second.

## Primary references

- [Atlas REST types/entities/lineage API](https://atlas.apache.org/api/v2/index.html)
- [Pinned type system documentation](https://github.com/apache/atlas/blob/release-2.5.0/docs/src/documents/TypeSystem.md)
- [Pinned authorization model](https://github.com/apache/atlas/blob/release-2.5.0/docs/src/documents/Security/AuthorizationModel.md)
- [Pinned installation and backing services](https://github.com/apache/atlas/blob/release-2.5.0/docs/src/documents/Setup/InstallationInstruction.md)
- [Pinned dependency/JVM contract](https://github.com/apache/atlas/blob/release-2.5.0/pom.xml)
