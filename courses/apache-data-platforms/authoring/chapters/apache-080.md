## Service restart, table durability and recipient recovery differ

A sharing deployment has server software, share configuration, recipient policy
and table storage. A reference-server process can be replaced while its config
and table remain. A durable table can also survive while the service is unavailable.
Treat those as different state sets and failure boundaries when writing an
operational runbook.

The prepared native-server route requires an actual compatible Scala/JVM package
and supported object-store signing path. A local file URI is not an interchangeable
replacement for a cloud signer. No source-built server or signed-data path has
been called qualified merely because its configuration template exists.
Preparation, compilation, protocol exchange and lifecycle readback need separate
receipts.

A recipient must distinguish safe read retries from state changes. A repeated
version-pinned request should preserve the intended snapshot, while switching to
current state can legitimately change rows. A timeout can leave the client
uncertain about which bytes were received, even though the read itself did not
mutate the provider's table.

## Worked case A: retain a shared version through replacement

After a real successful bounded read, save server source/package identity,
configuration identity, table ID/version and exact logical row oracle. Stop and
resume the same owned server process or container and repeat only the read.
Then replace the process over retained configuration and table storage and
repeat again. Do not rewrite the table or regenerate the fixture during readback.

Require the same three orders and selected version 0. The server container can
change while table identity remains stable. Conversely, seeing the same rows
under a newly created table ID is a different event that should not count as
retained-state acceptance. Keep logical and process identities in the dossier.

The share configuration may contain bearer/storage credentials, so evidence
should hash or describe its relevant source without exporting secret values.
A sanitized configuration contract can record table names, version policy and
storage identity. Never preserve a complete recipient profile or signed file
URL merely to make a receipt seem reproducible.

## Worked case B: distinguish missing file from unavailable server

On a separately copied owned fixture, make one advertised data file unavailable
and request the fixed version. The control path can still respond while data
retrieval fails. In a second experiment, stop the actual server and observe a
control-path transport failure before any file response. Those are different
failure locations and need different recovery actions.

Bound attempts and retain the first diagnostic. An expired URL may require a
supported refresh, a missing source file may require provider restoration, and
an unavailable service may require process/network recovery. Indefinite retries
cannot repair all three conditions and can obscure a clear operational incident.

A service-level objective should specify latency, availability and freshness for
the intended recipient workload. Tiny local read timings are not a forecast for
large object transfers or many simultaneous recipients. Measure server CPU,
metadata latency, file bytes and storage behavior separately before extrapolating
capacity or cost.

## Diagnosis and interview discussion

State whether an incident caused unavailability, stale state, missing files or
incorrect rows. Record selected snapshot, control response, data retrieval stage,
actual service identity and recovered result. Preserve owned table/configuration
state until the cause is understood and required evidence has been exported.

**Interview discussion: why is a healthy sharing process insufficient to prove
service recovery?** Its configuration or referenced table files can still be
wrong or unavailable. These cases require unchanged versioned data after
replacement and distinguish a failed data plane from a failed control service
without hiding either behind a generic restart flag.
