# apache-078: Recipients and credential boundaries

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-077`, `apache-075`.

## Key terms

- **Bearer token:** A credential in the profile file that grants access to anyone who holds it, so it must never appear in notebooks, receipts or screenshots.
- **Credential rotation:** Issuing a new token to a recipient and retiring the old one, with any overlap period stated explicitly.
- **Revocation:** Withdrawing a recipient's access to new control requests. It does not recall already issued URLs or data already downloaded.
- **Credential boundary:** The scope a credential covers, separating control requests, issued file URLs, cached metadata and downloaded copies.

## A recipient profile carries authority

A sharing profile combines an endpoint with credentials and versioned profile
metadata. It is not an ordinary public connection example. Publishing it in a
notebook, source archive or screenshot can grant unintended access. Signed data
URLs also carry temporary authority and should be treated separately from harmless
table names and version identifiers.

The prepared workshop stores the fixture profile in an untracked regular file
with a bounded size and supported credential version. The Docker client receives
only its read-only project mount and explicit environment file. It prints logical
results and sanitized failures without emitting bearer tokens or signed query
strings. No credential is required for the offline plan action.

Credential validity has several scopes: new control requests, already issued
URLs, cached metadata and downloaded copies. Revoking one control credential does
not necessarily revoke every capability or erase data a recipient already owns.
Define the intended revocation boundary before promising an access policy.

**Execution boundary.** Issuing, rotating and revoking recipient credentials happens
on the provider's server, which the repository does not include. The client's part,
reading the profile and sending its bearer token only to the control endpoint, is
in `projects/delta-sharing/client.py`.

## Worked case A: use a fixture-only short-lived profile

On the separately prepared owned server, issue a synthetic recipient credential
with a stated expiration and table scope. Save it outside version control and
run an actual bounded read. Record profile format version, logical recipient
role, authorized table and expiration policy without storing the credential
value. Use verified TLS and an explicit expected data-host allowlist.

The client rejects profiles with unsupported format, empty bearer value,
embedded URL credentials or insecure remote endpoints. A parsing failure is
separate from a server denial. A validly parsed profile can still be expired or
unauthorized, so acceptance requires the actual service response and exact
business-row readback.

Do not include the profile in portable starter archives or generated teaching
source. The source should show field names and explain how the learner supplies
a disposable fixture profile, while keeping actual values local. A copied token
in a command-line argument can also appear in shell history or process listings,
which is why the prepared launcher uses a file.

## Worked case B: invalidate new access and inspect its limits

Rotate or disable the fixture credential through the actual provider mechanism.
Require a new control request using the old credential to fail with the intended
401 or 403 condition. Then test a newly issued valid credential separately. Do not
accept an outage or missing table as proof that revocation worked.

If a previously issued signed URL remains valid until its own expiration, report
that observation explicitly. Its authorization is enforced by the storage
provider under the URL's signing contract. Shorter URL lifetime can reduce that
window but affects retry and long-read behavior. Choose and measure a policy
rather than assuming all capabilities share one clock.

Downloaded bytes have crossed an even stronger boundary. Disabling a profile
cannot remotely erase an offline copy on another system. A governance agreement,
retention process or controlled execution environment can address additional
requirements, but those are separate mechanisms whose actual enforcement must
be stated and tested.

## Diagnosis and interview discussion

Distinguish profile parsing, credential expiry, provider revocation, URL expiry,
storage denial and cached/downloaded data. Keep clocks and units explicit when
comparing expiration observations. Sanitize errors at every layer so a useful
failure report does not become a new credential leak.

**Interview discussion: what exactly does rotating a sharing token revoke?** It
can reject future control requests under that provider's rules; already issued
URLs and downloaded data can have different lifetimes. The two cases establish
a controlled credential path and then measure the specific revocation boundary
instead of claiming universal erasure.

## Worked examples

### Shape of a recipient profile

```json
{
  "shareCredentialsVersion": 1,
  "endpoint": "https://sharing.example.com/delta-sharing",
  "bearerToken": "<fixture-only-token>",
  "expirationTime": "2026-01-02T00:00:00Z"
}
```

Anyone holding this file can read every table in the shares it grants, so treat it like a password: store it untracked, give it a short expiration and never paste it into tickets. The client rejects profiles with an unexpected credentials version, an empty token or extra structure, and it never echoes the token in errors. The endpoint and expiry shown are illustrative.

### What rotation does and does not revoke

```bash
curl -s -o /dev/null -w "%{http_code}\n" \
  -H "Authorization: Bearer $OLD_RECIPIENT_TOKEN" \
  "$SHARING_ENDPOINT/shares?maxResults=1"
```

After rotating the fixture credential, this call with the old token should return 401 or 403, which shows that new control requests are blocked. It does not invalidate presigned file URLs already handed out; those stay valid until preSignedUrlTimeoutSeconds expires, which is 60 in the example config. Files already downloaded cannot be recalled at all, so revocation is a forward-looking control, and short URL lifetimes are what limit the exposure window.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Delta Sharing apache-078 prepared command notebook

Copy the owned Delta Sharing project and follow PREPARATION.md. Delta Sharing
belongs to Delta Lake/Linux Foundation. The offline preparation actions are:

```bash
bash run.sh prepare
bash run.sh plan
```

For a separately prepared actual owned reference server and untracked recipient
profile, the bounded native Docker protocol client runs with:

```bash
bash run.sh check
```

Rotate only fixture credentials via the real provider mechanism, then test old/new control access separately. Previously issued URLs and downloaded copies have different revocation boundaries.

The classroom Markdown pad does not start a service. Source configuration and
unit policy fixtures are not actual reference-server receipts. Keep credentials
and signed URL query strings out of all published source and evidence.

## Primary references

- [Delta Sharing protocol](https://github.com/delta-io/delta-sharing/blob/v1.4.1/PROTOCOL.md)
- [Reference server and client examples](https://github.com/delta-io/delta-sharing/blob/v1.4.1/README.md)
- [Reference server configuration](https://github.com/delta-io/delta-sharing/blob/v1.4.1/server/src/universal/conf/delta-sharing-server.yaml.template)
- [Actual cloud signing implementation](https://github.com/delta-io/delta-sharing/blob/v1.4.1/server/src/main/scala/io/delta/sharing/server/common/CloudFileSigner.scala)
- [Current Python package dependencies](https://pypi.org/project/delta-sharing/1.4.2/)
