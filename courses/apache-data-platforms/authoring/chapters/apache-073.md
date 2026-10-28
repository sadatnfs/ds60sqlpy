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

## Worked case A: permitted and rejected API requests

On the explicitly owned fixture server, perform a permitted metadata read using
the configured test principal. Repeat the read with a deliberately invalid fixture
password and require the actual401 or403 response. This negative check establishes
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
