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
401/403condition. Then test a newly issued valid credential separately. Do not
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
