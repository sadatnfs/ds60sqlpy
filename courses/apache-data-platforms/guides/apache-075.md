# apache-075: An open sharing protocol

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-008`, `apache-039`, `apache-073`.

## Key terms

- **Delta Sharing:** An open protocol from the Delta Lake project under the Linux Foundation, not the Apache Software Foundation, through which a recipient discovers and reads shared tables.
- **Share:** The top-level object a provider grants to a recipient, containing schemas that contain shared tables.
- **Recipient:** The party granted access to shares, identified by the credentials in its profile file.
- **Profile file:** A JSON file holding the sharing server endpoint, a bearer token and the profile format version.
- **Reference server:** The Scala and JVM server implementation intended for development and interoperability testing, not a production deployment.

## Sharing a table is a protocol interaction

Delta Sharing defines an open protocol through which a recipient discovers and
reads shared tables. It belongs to the Delta Lake/Linux Foundation ecosystem,
not the Apache Software Foundation. A Delta table is a storage/transaction format;
a Delta Sharing service authorizes and describes recipient access to table data.
The two concepts are related without being interchangeable.

The reference implementation is a Scala/JVM server intended for development and
interoperability testing. Its public interface and the recipient's data path
must be secured for the chosen deployment. A production-grade authentication,
proxy, storage and operational design is not established by starting the example
server. Keep the scope of a local or prepared-native workshop explicit.

The [sharing project](../projects/delta-sharing/README.md) provides an actual
bounded protocol client and a separate reference-server preparation runbook.
The selected 1.4.1 release did not expose a matching prebuilt package or image tag
at inspection. Current official Python 1.4.2 also requires a native wrapper lacking
an inspected Linux ARM64 wheel. The portable basic-Parquet client avoids emulation
and rejects features it does not implement.

**Execution boundary.** No Delta Sharing reference server is included. `bash run.sh
prepare` and `bash run.sh plan` validate the recipient client without contacting a
server; the listings and the 401 or 403 below require a separately prepared
reference server. Its share, schema and table come from a configuration like the
project's example:

From [`projects/delta-sharing/server-config.example.yaml`](../projects/delta-sharing/server-config.example.yaml):

```yaml
version: 1
host: "0.0.0.0"
port: 8080
endpoint: "/delta-sharing"
preSignedUrlTimeoutSeconds: 60
stalenessAcceptable: false
evaluatePredicateHints: false
shares:
  - name: ds60_fixture
    schemas:
      - name: tutorial
        tables:
          - name: orders
            location: "s3a://owned-fixture-bucket/orders"
            id: "81e0b600-1380-4b9a-a4db-000000000001"
            historyShared: true
```

The client walks that hierarchy with three bounded listing requests before it asks
for table metadata:

From [`projects/delta-sharing/client.py`](../projects/delta-sharing/client.py):

```python fragment
code, _, body = control("/shares?maxResults=100")
if share not in {row["name"] for row in json.loads(body).get("items", [])}:
    raise ValueError("Expected owned share absent from bounded listing")
_, _, body = control("/shares/" + urllib.parse.quote(share, safe="") + "/schemas?maxResults=100")
if schema not in {row["name"] for row in json.loads(body).get("items", [])}:
    raise ValueError("Expected owned schema absent")
_, _, body = control(path.rsplit("/", 1)[0] + "?maxResults=100")
if table not in {row["name"] for row in json.loads(body).get("items", [])}:
    raise ValueError("Expected owned table absent")
```

## Worked case A: discover one explicitly owned table

Prepare an actual reference server and a synthetic table under an owned share,
schema and table name. The recipient profile identifies the service endpoint
and credential. List shares, schemas and tables through the actual protocol,
and require the specific owned names from the fixture contract. A successful
list of some public demonstration table is not evidence that this provider's
configuration works.

The prepared fixture-contract.json names ds60_fixture.tutorial.orders at version 0.
Its expected business rows are IDs 1/2/3 with regions east/west/east and amounts 4/9/7.
Discovery establishes the control-plane naming path. It does not yet establish
metadata compatibility, signed data-file access or row-level correctness. Those
are later stages with independent observations.

List APIs can paginate. The bounded client searches a deliberately small owned
namespace with a stated page limit and fails if the expected object is absent.
A general inventory client must follow continuation semantics rather than
calling one page complete. Record the limit and selected names with the result.

## Worked case B: reject an invalid recipient

Issue a separate list request with an intentionally invalid fixture credential
and require 401 or 403. A server outage, missing table or TLS failure does not
satisfy this authentication/authorization negative case. Keep the valid and
invalid observations separate so an unavailable service cannot masquerade as a
successful access-control test.

The recipient bearer credential belongs only to the sharing control endpoint.
It should not be copied into requests to the object-store URLs returned by the
server. Those URLs have their own authorization mechanism. The portable client
uses separate unauthenticated data requests and never emits tokens or signed
query strings in its result.

An endpoint can discover a table while denying a later query according to its
actual access rules. Conversely, previously issued URLs or downloaded bytes can
outlive a rejected new list request. Therefore a narrow invalid-recipient result
must not be expanded into a claim of immediate universal data revocation.

## Diagnosis and interview discussion

Trace profile parsing, service origin, credential acceptance, share/schema/table
identity, metadata response and data retrieval independently. Use verified TLS
and reject credential-bearing redirects. Preserve sanitized status and logical
identities, while leaving secrets and signed URLs out of notebooks and evidence.

**Interview discussion: is Delta Sharing simply a Delta file reader?** No. It
adds discovery and recipient access through a service protocol, with a separate
data-retrieval path. These cases establish a specific discovery contract and an
actual rejected-recipient boundary before any claim about reading table rows.

## Complete worked source

The classroom does not execute these service commands. See the [workshop rules](../STUDY-GUIDE.md#workshop-notebooks).

# Delta Sharing apache-075 prepared command notebook

Copy the Delta Sharing project, a Delta Lake and Linux Foundation tool rather than an Apache one, and read PREPARATION.md. `prepare` only confirms the native client image, and the first `plan` creates the owned namespace and prints the expected rows with `server_contacted` false:

```bash
bash run.sh prepare
bash run.sh plan
```

The check needs a reference server you prepared yourself and a recipient profile kept under the untracked `.workshop/` directory:

```bash
bash run.sh check
```

The actual check lists the exact owned share/schema/table and requires an invalid-recipient 401 or 403 before accepting its bounded row read.

The pad never starts a server. Keep the bearer token and any signed URL query string out of the receipt; record the listed share, schema and table names and the 401 or 403 code instead.

## Primary references

- [Delta Sharing protocol](https://github.com/delta-io/delta-sharing/blob/v1.4.1/PROTOCOL.md)
- [Reference server and client examples](https://github.com/delta-io/delta-sharing/blob/v1.4.1/README.md)
- [Reference server configuration](https://github.com/delta-io/delta-sharing/blob/v1.4.1/server/src/universal/conf/delta-sharing-server.yaml.template)
- [Actual cloud signing implementation](https://github.com/delta-io/delta-sharing/blob/v1.4.1/server/src/main/scala/io/delta/sharing/server/common/CloudFileSigner.scala)
- [Current Python package dependencies](https://pypi.org/project/delta-sharing/1.4.2/)
