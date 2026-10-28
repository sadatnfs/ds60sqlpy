## An analytical serving system has distinct roles

Pinot serves analytical queries from segments, which are column-oriented units
containing data and indexes. A controller manages table configuration, segment
metadata and assignment. A server stores or consumes segments and evaluates query
work. A broker accepts a query, determines relevant servers and combines their
responses. ZooKeeper supplies coordination state through the cluster-management
layer. These roles can share a small machine for instruction while retaining
different responsibilities and failure behavior.

A data file is not yet a served segment. Offline ingestion reads a supported
input format, applies schema and transformation rules, builds a segment and
uploads it through the configured controller path. The controller records and
assigns that segment, and servers must make it available before a broker query
can return its rows. A successful upload response alone does not establish that
all expected rows are queryable.

The [owned Pinot project](../../projects/pinot/README.md) uses three synthetic
orders and separate actual role containers. Its preparation pins the official
1.5.1 image digest with native AMD64 and ARM64 descriptors. Source preparation,
image availability and actual native acceptance remain separate in the project's
qualification ledger. No classroom Markdown pad starts these services.

## Worked case A: load one bounded offline segment

The input has IDs 1, 2 and 3, regions east/west/east, and amounts 4, 9 and 7.
The schema distinguishes dimensions, metrics and an epoch-millisecond time field.
The table requests one replica and appropriate indexes. Explicit initialization
creates only an absent owned table, builds the real segment with the released
standalone ingestion runner, and pushes it to the actual controller.

The independent oracle expects the exact three identities and values. A count
of three is weaker: duplicated ID 1 and missing ID 3 could preserve that count.
An amount sum is also insufficient because different missing/duplicated values
can cancel. The checker therefore requests ordered primitive columns and compares
complete rows before accepting the aggregate east 11 and west 9.

Initialization and readback are separate operations. If initialization was
interrupted after creating an empty table, the next check reports that state.
It does not delete the table or replay ingestion to manufacture a successful
lifecycle result. Inspect controller metadata, segment state and ingestion output
before deciding whether an explicit recovery action is safe.

## Worked case B: a broker query crosses the serving topology

The client sends SQL to broker:8099, not directly to a data file. The broker
routes work to the assigned serving instance and combines the result. The project
also reads controller segment and instance metadata so the result can be tied
to the actual serving topology. A query against an unknown column must return
an explicit exception rather than being mistaken for an empty successful result.

All role addresses belong to the project's private Docker network. Host
localhost and container localhost have different meanings, as established in
the networking foundations. A broker advertising an unreachable address can
accept an initial request yet fail a later data exchange. Record both listener
and advertised identities while diagnosing connection failures.

One broker and one server provide no high availability. All containers also
share the same Docker engine and disk. The project teaches role boundaries and
retained state without claiming rack-level replication, production latency or
fault tolerance. Increasing a replica count requires actual placement and query
availability checks, not merely a new integer in a JSON file.

The pinned server release eagerly evaluates a default address-discovery call
that tries to find a public UDP route, even when an explicit server hostname is
present. An internal Docker network has no such route, and the first owned run
failed with Network is unreachable before loading any data. The workshop pins
hostname-based instance addressing while retaining the explicit service DNS name.
This configuration keeps startup inside the private network; enabling external
egress is not required merely to discover the server's own address.

## Diagnosis and interview discussion

Follow input file, ingestion output, controller metadata, assignment, server
availability and broker exceptions in that order. Missing rows can originate at
any of those boundaries. Preserve the original source fixture and segment identity
when investigating; resetting volumes discards the evidence needed to distinguish
ingestion loss from a routing failure.

**Interview discussion: why can segment upload succeed while a query is incomplete?**
Upload, assignment and server readiness are separate stages. A complete diagnosis
compares expected source identities with segment state and actual broker results.
The two cases establish a reproducible segment contract and explain the serving
path that must be healthy before the contract can be observed.
