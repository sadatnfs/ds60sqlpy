# Native qualification boundaries

The corrected actual Apache Pinot 1.5.1 workshop passed Linux ARM64 acceptance
on October 28, 2026. It used the official Apache binary archive with its published
SHA512 on the already prepared native Java 17 base. The locally built image is
not presented as an Apache-published container. Native AMD64 execution remains
a separate hosted-runner gate; no local AMD64 emulation was used.

The actual broker returned exact order identities/values, east 11 and west 9,
and selective ID 3. An unknown column returned its actual field diagnostic.
Controller metadata contained the broker/server roles and one owned offline
segment. Repeated checks were read-only and did not initialize or replay ingestion.

Exact stop/resume retained all four role container identities. Replacement over
retained coordination/controller/server/staging volumes changed every container
identity while preserving image identities, the offline segment/role identity and
all query results. The maintained qualifier confirmed owned container/network/
volume absence after destruction and retention of all pre-existing volumes.

The initial official image pull failed verified TLS before startup. Its failure
was retained; certificate checks were never disabled. The first binary-server
startup then exposed the release's eager public-route address discovery on an
internal network. The corrected project uses the supported hostname mode while
retaining explicit private service DNS. That diagnostic and corrected result are
separate observations, not a rewritten successful history.

This acceptance covers the bounded offline segment path. Kafka ingestion,
hybrid/upsert behavior, indexed-versus-unindexed plan comparisons, multistage
joins, cross-host operation and high availability require their own actual gates.
Their source/configuration routes remain explicitly prepared extensions.
