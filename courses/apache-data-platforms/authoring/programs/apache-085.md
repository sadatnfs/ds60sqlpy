# Integration apache-085 complete worked notebook

Prepare the real reference server and supported table store. Read the fixed version with exact rows, reject invalid recipient credentials and measure revocation/issued-URL limits without saving capabilities.

## What this sharing receipt must hold

- The share, schema, table and version requested, matching `fixture-contract.json`.
- The Delta table version, protocol and metadata responses the server returned.
- The data file identities read through signed URLs, recorded without query strings.
- Rows 1/2/3 with amounts 4/9/7, and regional totals 11 and 9.
- The status code for an invalid or revoked fixture recipient, with its error body.
- The observed lifetime of a URL issued before revocation, with the signing policy.

Status codes carry the oracle for this route. A 200 with exact rows for the valid
recipient and a 401 or 403 for the revoked one together show authorization at
the server. A 404 or connection error for the revoked recipient shows nothing
about authorization. An old signed URL that still returns bytes after revocation
is the expected boundary, not a failure, as long as its expiry is recorded. The
[shared receipt rules](../../STUDY-GUIDE.md#evidence-receipts) cover naming and storage.

## Concrete source inspection

From the copied integration directory, with sibling project copies when selected:

```bash
cat ../delta-sharing/fixture-contract.json
cat ../delta-sharing/PREPARATION.md
```

The contract names share `ds60_fixture`, schema `tutorial`, table `orders` and
version 0, so a version 0 request with any other name is a different product.
`PREPARATION.md` explains why no local 1.4.1 server acceptance exists: the release
ships source archives without a prebuilt server, so the server must be built from
the pinned tag before any revocation test is meaningful.
