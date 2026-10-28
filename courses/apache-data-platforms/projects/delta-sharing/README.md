# Actual Delta Sharing protocol client and prepared reference-server route

Delta Sharing belongs to Delta Lake/Linux Foundation. This directory provides
a real bounded Parquet-protocol recipient client and a separately prepared
Scala reference-server runbook. No local server or advanced client feature is
claimed qualified. Read [PREPARATION.md](PREPARATION.md) before server work.

Prepare the native ordinary data-platforms-python image, copy this directory
into work/apache-sharing, then run:

```bash
bash run.sh prepare
bash run.sh plan
```

Neither action contacts a sharing server. The portable client uses actual HTTP
protocol operations and PyArrow Parquet decoding, not a mock sharing service.
It is intentionally limited to basic unpartitioned Parquet/minReaderVersion 1; Delta response
format, deletion vectors and CDF are rejected or left to separately supported
clients. Current official Python 1.4.2depends on a Rust wrapper with no inspected
LinuxARM64wheel, so no automatic emulation or incompatible install is attempted.

For an explicitly prepared owned reference server, put the fixture recipient
profile in untracked `.workshop/recipient.share` and set DS60_SHARING_DATA_HOSTS in an
untracked `.workshop/sharing.env` to a comma-separated exact hostname allowlist for the
expected object store. The profile uses shareCredentialsVersion1, endpoint and
bearerToken. Never paste it into a notebook or commit it. Adjust the public
fixture-contract.json only to the actual owned share/schema/table/version.

```bash
bash run.sh check
```

The client lists shares/schemas/tables, fetches metadata, requests the fixed
version, validates supported protocol, then reads at most10 files/8 MB combined
and 1000 rows combined. Parquet footer row/column/group/schema and uncompressed-byte
bounds are checked before materializing data. Nonempty partitionValues are rejected;
this first portable route is explicitly unpartitioned. It requires exact order rows and actual 401/403 for an invalid
recipient. Bearer credentials go only to the control endpoint; object requests
receive no recipient Authorization header. Redirects are rejected before
credential or signed-URL forwarding, verified HTTPS is required, and tokens/URLs
are omitted from output. File hostnames must match the explicit allowlist.

Lifecycle and cleanup belong to the separately owned native server/table store.
Run check alone after restart or replacement, preserving table/version identity.
Do not rewrite source data to make retention pass. Revoking the profile does not
erase downloaded data or necessarily invalidate already issued unexpired file
URLs. Keep those revocation boundaries explicit in the evidence.

All generated ownership, lock and credential state stays under `.workshop/`,
which the existing starter/Docker/source policy excludes. Only fixed public
client/configuration files and the explicit read-only recipient profile are
mounted; the whole working directory is not a container source mount.
