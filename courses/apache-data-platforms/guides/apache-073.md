# apache-073: Authorization and governance workflows

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-072`, `apache-069`.

## Key terms

- **Authentication:** Establishing who the caller is, for example with fixture credentials kept in an untracked environment file.
- **Authorization:** Deciding which metadata operations an authenticated caller may perform. A failed login yields 401, while a permitted login without the needed permission yields 403.
- **Policy decision point:** The component that evaluates a policy and decides whether an operation is allowed.
- **Policy enforcement point:** The component that blocks or permits the protected operation. Permission to classify an asset is not permission to modify its data.
- **Governance workflow:** A recorded process of ownership, classification review and approval decisions, which does not by itself control storage or query access.

## Governance decisions need an enforcement boundary

Atlas authentication identifies a caller, while authorization determines which
metadata operations that caller may perform. A governance workflow can also
record an owner, classification review and approval decision. Those metadata
policies do not automatically control every storage object or query engine that
contains the underlying data.

A complete design names the policy decision point, enforcement point and protected
operation. Reading Atlas entity metadata, selecting table rows and downloading
an already issued file URL are different operations. Permission to classify an
asset should not be treated as permission to modify its data, and a denial from
Atlas should not be reported as a denied Hive query.

The prepared client validates an Atlas origin without embedded credentials or
query parameters and requires verified HTTPS for remote servers. Its fixture
credentials remain in an untracked environment file passed to the Docker client.
They never appear in maintained notebooks, source payloads or receipts. Default
local server execution is omitted until a compatible native stack is prepared.

**Execution boundary.** Both requests in case A go to a prepared Atlas server with
untracked fixture credentials; the repository supplies the client and its 401 or
403 check but no server. Case B is a governance record you can write without a
server.

## Worked case A: permitted and rejected API requests

On the explicitly owned fixture server, perform a permitted metadata read using
the configured test principal. Repeat the read with a deliberately invalid fixture
password and require an actual 401 or 403 response. This negative check establishes
rejection at the Atlas API boundary, not a particular distinction between unknown
identity and insufficient permissions.

A stronger authorization extension uses two valid principals with different
reviewed permissions. Require one allowed read or mutation and one specifically
denied operation against the same owned namespace. Keep their policy definitions
and actual responses without storing credentials. A network failure,404 or
unrelated server error cannot satisfy the intended permission-denial oracle.

Do not enable verbose HTTP traces containing Authorization headers during
troubleshooting. A failed request can be diagnosed with operation class, bounded
status, server-side correlation and sanitized endpoint information. TLS errors
must remain failures; disabling verification would invalidate the credential
protection assumption of the experiment.

## Worked case B: classification review versus actual data access

Record a synthetic owner's decision that the curated asset carries the owned
reviewed classification. Save who is responsible in a neutral fixture role,
what criteria were checked and which data state was reviewed. This creates an
inspectable governance record, but it still does not establish engine enforcement.

For a separately prepared policy integration, issue the same data query under
an allowed consumer and a denied consumer through the actual engine. Record
where the request was rejected and how the catalog classification reached that
enforcer. If both queries succeed, report that observation even if the Atlas
label and policy intention look correct.

Previously downloaded data and cached permissions introduce revocation limits.
Removing a catalog label or disabling one metadata principal cannot erase copies
already held by a recipient. Define the scope and time of revocation and avoid
promising control over bytes outside the tested enforcement boundary.

## Diagnosis and interview discussion

Separate authentication failure, authorization denial, metadata state and data
engine behavior. Keep identity mapping, policy revision, classification origin
and actual protected request in the evidence dossier. An approval record is a
human decision with a scope; a zero exit code is not a substitute for that scope.

**Interview discussion: what evidence proves a governance policy works?** A clear
policy/enforcement mapping plus actual allowed and denied protected operations,
not merely a classification or configuration file. These cases verify a narrow
API credential boundary and then explain the independent test required for a
real data-access claim.

## Worked examples

### An invalid credential must be rejected

```bash
curl -s -o /dev/null -w "%{http_code}\n" -u "invalid:fixture" \
  "$DS60_ATLAS_ENDPOINT/api/atlas/v2/types/typedef/name/ds60_<owner>_dataset"
```

The expected code is 401 or 403; the check route fails if anything else comes back. A 200 here would mean authentication is disabled, which turns every metadata claim in the catalog into something anyone could have written. A redirect to a login page is also suspicious for an API client, which is why client.py refuses redirects before it forwards credentials. Note that this proves only that Atlas guards its own API, nothing about who can query the underlying tables.

### Label review versus data access

```sql
SELECT
  region,
  SUM(amount)
FROM
  ds60.orders
GROUP BY
  region;
```

Imagine the orders table carries a PII classification in Atlas. Whether this query succeeds depends on the engine and its authorizer, for example a Ranger tag policy that reads Atlas classifications, not on Atlas itself. To claim enforcement you need a recorded denial from the engine for a principal that lacks access, alongside a success for one that has it. Without that pair, the classification documents a decision but does not prove it is applied.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Atlas apache-073 prepared command notebook

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

Check requires an actual 401 or 403 for a deliberately invalid fixture credential. A valid-principal authorization comparison and actual denied data-engine query remain independent tests.

Prepared payloads are not actual Atlas observations. Never place credentials or
Authorization headers in notebooks, source, command arguments or receipts.

## Primary references

- [Atlas REST types/entities/lineage API](https://atlas.apache.org/api/v2/index.html)
- [Pinned type system documentation](https://github.com/apache/atlas/blob/release-2.5.0/docs/src/documents/TypeSystem.md)
- [Pinned authorization model](https://github.com/apache/atlas/blob/release-2.5.0/docs/src/documents/Security/AuthorizationModel.md)
- [Pinned installation and backing services](https://github.com/apache/atlas/blob/release-2.5.0/docs/src/documents/Setup/InstallationInstruction.md)
- [Pinned dependency/JVM contract](https://github.com/apache/atlas/blob/release-2.5.0/pom.xml)
