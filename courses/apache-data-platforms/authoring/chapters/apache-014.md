## Interchange is a contract between independently owned processes

Arrow describes typed columnar memory and related interchange protocols. It is
not itself a database, transaction manager or durable catalog. The C Data
Interface exposes arrays across an in-process language boundary with explicit
ownership and release callbacks. Arrow IPC serializes batches for a file or stream.
Flight transfers Arrow data through RPC. They solve related problems at different
boundaries and should not all be described as the same zero-copy mechanism.

A reference-counted buffer can be shared inside one process without copying its
values, but crossing a process or network boundary can require serialization,
framing, transport buffers and allocations. A compatible representation can reduce
conversion cost without eliminating every copy. Claims about copy counts require
measurements at the specific boundary, not just the presence of an Arrow type.

The project supplies two real paths. The first exchanges IPC between the prepared
Python Arrow23 and Rust Arrow60 libraries. The second sends batches from an actual
Flight service to an independent client. Dependency preparation happens before
the workshop; the checks need no host Python, Rust compiler, Cargo resolution or
network package download.

## Worked case A: Python to Rust and back

The ipc-check command creates a three-row stream with an int64 identifier, UTF8
region and nullable int64 amount. The second amount is null. Python writes the
IPC stream to a temporary file, the prepared Rust compiler builds the bridge
against its installed Arrow library, and the Rust program reads and rewrites the
stream. Python then checks exact schema, values and nulls after the round trip.

Rust downcasts each column to its expected concrete array type and rejects an
unexpected schema or row count. Checking a nullable array through value alone
would be wrong because the null bitmap carries validity separately from the value
buffer. The bridge explicitly checks the missing amount rather than treating its
underlying physical slot as a meaningful integer.

The different library version numbers are deliberate: Arrow IPC interoperability
is a protocol property, not a requirement that Python and Rust package numbers
match. This exact primitive-schema exchange is qualified; it does not prove every
extension type, compression mode or future protocol feature interoperates. Keep a
fixture for the types a real application uses and qualify both directions.

## Worked case B: a real Flight request and rejected tickets

The check command discovers the fixed events descriptor, obtains a ticket and
reads batches from the separate server. The server's dataset is immutable and
owned by this project. The client validates three rows, total 11 for east and a
logical source digest. It also sends three invalid tickets, including a path-like
value, and an unknown descriptor; each must be rejected by the actual service.

A Flight ticket is an opaque server-defined selection token. It is not inherently
a filesystem path, SQL statement or user identity. The fixture allowlists one
exact token and does not use caller bytes to choose arbitrary files. That protects
this selection boundary, but does not create authentication. The service remains
local and private because it has no identity or authorization subsystem.

Stopping and resuming reuses the exact server container. Down followed by start
replaces it while retaining the named fixture volume. The qualified lifecycle
readbacks preserve the same source identity and result. They establish persistence
for this local topology, not replication, public endpoint security or service
availability during its single server's interruption.

## Diagnosis and interview discussion

Distinguish schema mismatch, malformed IPC, lifetime misuse, network failure and
application-level ticket rejection. A C Data Interface consumer must obey release
ownership even if its visible values look correct. A Flight client must bound
message size, rows, bytes and deadlines even when the server is on a local network.
Use the provided fixed fixture before attempting a larger integration.

**Interview discussion: when is zero copy a defensible statement?** Name the
specific buffer, process boundary, ownership contract and conversion being avoided.
The IPC bridge and Flight service demonstrate real interoperability and transfer;
neither test measures or claims that all transport and allocation costs vanish.
That precision prevents a useful format from becoming an unsupported performance
or database guarantee.
