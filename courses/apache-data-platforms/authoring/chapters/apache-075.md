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

The [sharing project](../../projects/delta-sharing/README.md) provides an actual
bounded protocol client and a separate reference-server preparation runbook.
The selected1.4.1 release did not expose a matching prebuilt package or image tag
at inspection. Current official Python 1.4.2also requires a native wrapper lacking
an inspected LinuxARM64wheel. The portable basic-Parquet client avoids emulation
and rejects features it does not implement.

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
and require401 or403. A server outage, missing table or TLS failure does not
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
