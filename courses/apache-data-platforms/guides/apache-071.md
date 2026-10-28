# apache-071: Classifications and discovery

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-070`, `apache-069`.

## A classification is metadata with a defined meaning

Atlas classifications label entities and can carry attributes. Examples might
represent a review status, a sensitivity category or a business classification.
The label's meaning, owner and revision process must be defined outside the
string itself. Two teams using the same word with different criteria can produce
a misleading catalog even when every API request is syntactically valid.

Discovery uses type, classification and other indexed metadata to locate assets.
An entity read by GUID and a search result can exercise different backend paths.
Search can lag behind a successful mutation, so a new classification may be
visible in direct entity readback before every discovery query reflects it.
Use bounded polling and retain that timing distinction.

A label is not automatically an access-control rule in every data engine.
An integration must map the classification to a policy, distribute it to an
authorizer and enforce it at the actual data-access boundary. The prepared Atlas
client explicitly reports that data-engine enforcement has not been demonstrated.
No chapter treats a successful label attachment as a denied query.

## Worked case A: attach and discover a review label

Define the owned reviewed classification and attach it to the curated synthetic
dataset. Read the entity directly and require that exact classification type.
Then, on the separately prepared real server, search by the owned dataset type
and classification under a finite deadline. Require the curated GUID in the
matching results and preserve request parameters and server version.

The independent oracle uses a known asset identity, not only a matching display
name. An unqualified search for reviewed could find another experiment's entity
and create a false positive. The saved random owner keeps the tutorial's type
and qualified-name namespace separate from unrelated catalog content.

Search pagination matters even for a simple API. A first page does not establish
that a larger result set is complete. Bound the tutorial to its small namespace,
record the selected limit and use the API's actual continuation behavior when
extending the experiment. A client must not silently discard additional pages
while calling the result an exhaustive inventory.

## Worked case B: remove a label without deleting the asset

Use the real classification removal endpoint for the exact owned GUID/type after
saving the first observation. Read the entity again and require that the label
is absent while its qualified name and GUID remain unchanged. Poll discovery
separately until the old classification search no longer returns that asset,
subject to the selected server's indexing behavior.

Removal changes a metadata statement; it does not automatically delete files,
revoke already downloaded data or prove an access policy changed. If a workflow
requires enforcement, run an actual authorized and denied data request through
the policy-aware engine. Keep that result separate from the catalog mutation so
an eventual-consistency delay cannot be hidden in one combined success flag.

Classification propagation through relationships introduces another policy choice.
A propagated label may have a different origin and lifecycle from a directly
assigned label. Inspect the actual propagation configuration and entity response
before treating all visible classifications as independent owner decisions.
Changes to relationship direction can affect propagation without changing file
contents.

## Diagnosis and interview discussion

Record type identity, assigned versus propagated origin, exact entity GUID,
mutation response, direct readback and discovery timing. Distinguish a failed
label write from search lag and distinguish both from authorization behavior.
Use an owner review with explicit criteria when classifications drive decisions.

**Interview discussion: why can an asset remain readable after being classified
as sensitive?** Classification and enforcement are separate components unless a
tested integration connects them. The two cases attach and remove a metadata
statement while preserving asset identity and requiring independent evidence for
search and actual data-access effects.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Atlas apache-071 prepared command notebook

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

The client reads the attached classification directly. A classification search, removal and bounded index catch-up experiment use the actual release API and need separate evidence; they do not prove data-engine enforcement.

Prepared payloads are not actual Atlas observations. Never place credentials or
Authorization headers in notebooks, source, command arguments or receipts.

## Primary references

- [Atlas REST types/entities/lineage API](https://atlas.apache.org/api/v2/index.html)
- [Pinned type system documentation](https://github.com/apache/atlas/blob/release-2.5.0/docs/src/documents/TypeSystem.md)
- [Pinned authorization model](https://github.com/apache/atlas/blob/release-2.5.0/docs/src/documents/Security/AuthorizationModel.md)
- [Pinned installation and backing services](https://github.com/apache/atlas/blob/release-2.5.0/docs/src/documents/Setup/InstallationInstruction.md)
- [Pinned dependency/JVM contract](https://github.com/apache/atlas/blob/release-2.5.0/pom.xml)
