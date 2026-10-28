# Owned data-product project design

This project is being implemented. It is not yet a qualified runnable fixture.
It complements the existing ML engineering service and the separate inference
service by exercising the data delivery, analytical publication and recovery
boundaries over actual local HTTP and persistent files.

## Product and state contract

A request supplies a complete synthetic delivery snapshot with a unique batch
identity, a monotone source generation, an expected row count and bounded typed
records. The business grain is one delivery. Route identities and positive
package-count rules are validated before publication. An accepted raw HTTP
request is distinct from an accepted analytical product.

The service records the canonical request identity and raw snapshot in SQLite.
Reusing the same batch identity with identical content is a replay; conflicting
content or an occupied source generation is rejected. The ordinary API does not
replace a previously received snapshot. A corrected producer sends a new full
snapshot with a new identity/generation.

A controlled publisher reads an identified snapshot, performs real Polars quality
checks and DuckDB aggregation, writes an immutable Parquet product plus manifest,
and activates a small pointer after validation. Invalid candidates retain bounded
reasons and never replace the previously accepted product. Consumers resolve one
pointer and verify the manifest/content before reading actual Parquet output.

The basic fixture has deliveries A/B/C with package counts 2/3/1 and route IDs
10/10/20. Its independent product oracle is route 10: two deliveries/five packages;
route 20: one delivery/one package. A later valid complete snapshot changes A to
four packages, producing seven packages on route 10 and one on route 20. Separate
bad snapshots exercise unknown route, duplicate business identity, missing values
and conflicting request identities.

## Explicit execution boundaries

All long-lived computation uses the already prepared data-engineering image.
The project does not build or download packages at runtime. First launch resolves
an existing image to an immutable ID and verifies Linux plus the native engine
architecture. Local qualification is ARM64 only. Unsupported images are refused
before launch, with portable chapter examples or a separately owned remote-native
host as the documented alternatives. There is no automatic emulation.

The host needs Docker and Bash, including WSL 2 on Windows. Source is copied to an
owned working directory before use. Docker-only tool commands handle ingestion,
publication and queries, so ordinary learners do not need host Python libraries.
The host release checker uses only Python's standard library and Docker CLI.

An API service publishes only to 127.0.0.1. It uses a reviewed local ingress
network plus an internal project network for its tool client. No engine socket,
ambient cloud credentials or external service is supplied. The service code does
not contact external URLs. This is a trusted local learning fixture, not an
internet-facing multi-tenant deployment.

## Files and permissions

Generated local state belongs under .workshop/, which the shared source packager
already excludes. It contains private ownership/authentication files, the raw
SQLite store and the published version collection. Secrets are generated locally,
read from a file by the client and never printed or placed in command arguments.

The API receives a writable raw-store directory but only read-only publication
and private-identity mounts. The controlled publisher receives the state it needs
to write. Directory mounts preserve visibility of atomic pointer replacement;
individual pointer-file bind mounts would retain the wrong inode after rename.
The source and container root filesystem remain read-only, with bounded resources
and no extra capabilities.

## Lifecycle and recovery

The launcher supports explicit start, stop, resume, status, logs and down, with
same-project ownership checks before mutation. Normal resume reuses prepared
images/state and never builds or pulls. Down retains .workshop/. Missing prepared
images produce a clear diagnostic rather than an implicit rebuild or architecture
fallback. An explicit image-update path may be added only with state-contract
validation and preservation of the prior selection.

Publication has separate prepared, pointer-activated and observed-completion
phases. An actual controlled process exit before the pointer leaves the old
product active. A process exit after a valid pointer replacement can leave an
incomplete audit observation; recovery reconciles the accepted pointer and
completes that observation without repeating ingestion or rewriting immutable
files. Operator rollback is explicit and records its reason. Out-of-order
ordinary publication must not silently downgrade the accepted generation.

The project assumes one controlled publication writer, enforced by a local file
lock. It does not claim a distributed transaction across HTTP, SQLite, files and
another service. Its raw acceptance transaction and publication pointer have
different authority boundaries, which the chapter and diagnostic output will
name directly.

## Required qualification

- Actual HTTP acceptance, exact replay and conflicting-identity rejection.
- Bounded input, malformed JSON/type/row-count rejection and no partial raw writes.
- Real analytical transformation and the independent route-level oracle.
- Invalid candidate rejection with unchanged accepted pointer and consumer result.
- Real failure injection before/after pointer activation and state reconciliation.
- Controlled rollback, stale-generation protection and content-corruption rejection.
- Stop/resume and full container replacement with unchanged durable receipts/data.
- Missing-image/native-platform refusal and ownership-scoped cleanup.
- Source packaging excludes .workshop/ but includes every maintained source fixture.

All checks use an explicitly disposable project. Cleanup removes only verified
owned resources; ambiguous ownership retains resources and evidence for review.
The test report distinguishes actual execution from syntax or policy checks.
