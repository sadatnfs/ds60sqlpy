# Environments and native qualification scope

The complete 88-unit tutorial route has 24 ordinary Python programs and 64
reading/project notebooks. Those are different execution surfaces. A registered
chapter, prepared image, source parse and actual service run are separate facts.
All local execution acceptance recorded here is Linux ARM64. Native AMD64 is a
separate hosted-runner gate; it was never emulated on this Mac.

## Ordinary actual-library environment

The dedicated data-platforms-python profile prepares Python 3.12 with
PyArrow 23.0.1, DataFusion 55.0.0 and PyIceberg 0.12.0 using Arrow/SQLite extras.
Its complete native worker success/error/timeout/recovery and result-publication
checks passed. Every one of the 24 authored ordinary references also passed in
actual Linux ARM64 with independent row/type/value and negative oracles.

PyIceberg performs catalog/scan work and explicitly materializes Arrow for the
DataFusion examples. No direct DataFusion-Iceberg provider or shared Spark/Hive
catalog connector is inferred from that bridge. The batch capstone additionally
records source/schema/snapshot/result identity, old versus current state, fresh
catalog readback and a wrong logical-catalog rejection.

Ballista has its own compatible Python 54.1/DataFusion 54 environment and glibc 2.39
or newer. It is not merged into DataFusion 55's ordinary worker. The current
Sharing Python 1.4.2 native wrapper did not expose an inspected Linux ARM64 wheel;
its dependency bounds also conflict with unreviewed newest HTTP/filesystem
packages. The portable project therefore uses a real bounded unpartitioned
Parquet protocol client and rejects advanced response formats/features.

## Actual native service paths

| Product/path | Accepted local scope | Explicitly separate scope |
| --- | --- | --- |
| Arrow Flight and Rust IPC | Actual Flight schema/value/null/RPC/invalid-ticket and namespace checks; compiled Rust/Python IPC; exact resume and retained-volume replacement | Different-host deployment and high availability |
| DataFusion 55 | Actual SQL/plans/UDFs/Arrow/Parquet examples in the ordinary profile | A direct Iceberg provider, remote catalog and arbitrary distributed execution |
| Ballista 54.1 | Supported one-container separate scheduler/executor/client processes, one executor with 1/2 task slots, positive/negative and lifecycle evidence | The retained failed three-container advertised-localhost route; cross-host/HA; uncompiled optional Rust client |
| Airflow 3.3.2 | Actual DAG/interval/retry/idempotent-publication/API/browser and retained-state lifecycle | Production executor/HA, unrelated hooks and external infrastructure |
| Kafka 4.4 | Actual checksum-binary broker; exact keyed records/positions, committed versus aborted transaction visibility, consumers, compaction-safe latest-key state and lifecycle | Physical compaction timing, replicated-broker outage and unexecuted combined stacks |
| Iceberg/PyIceberg 0.12 | Actual local catalog/snapshot/schema/conflicting-commit and scan behavior; explicit Arrow/DataFusion materialization | Arbitrary catalog/connector/table-feature interoperability |
| Flink 2.3 | Java/SQL, actual event-time late output, keyed state/timers, TaskManager-loss checkpoint restore, changed-UID savepoint rejection, compatible parallelism-two restore and measured backpressure; byte-identical retained state with no resubmission | Kafka transactional sink, cross-host HA and a general end-to-end exactly-once claim |
| Cassandra 5.0.9 | Actual CQL/SAI/CAS/timestamp/TTL/delete; real snapshot/SSTable import and byte-verified receipt export; read-only host/source identity through resume/replacement. Separate RF3 outage/ONE-versus-QUORUM and three-node lifecycle passed | Remote whole-cluster disaster recovery; fresh common RF3-wrapper execution |
| Pinot 1.5.1 | Actual controller/broker/server/ZooKeeper; exact offline segment rows/aggregates/selective query and typed negative; exact resume/replacement with retained roles/segment/results | Kafka/hybrid/upsert/index-plan comparisons, multistage joins and HA |
| Hive 4.2.1 / PostgreSQL 17.6 | Actual schema initialization/verification, HiveServer2 SQL and typed missing-column failure; independent Java Thrift names/types/partition/location oracle; exact resume/replacement without reinitialization | ACID, Iceberg extension, upgrade/remote-backup and additional clients |

All accepted workshops removed only verified synthetic resources and retained
pre-existing learner volumes. Qualification does not promise every image remains
cached locally. Reversible accepted project-only images may be reclaimed after
source/image/receipt binding and zero container use are checked; base/ordinary
images and learner state have a separate preservation boundary.

## Explicit prepared-native alternatives

Atlas 2.5 targets Java 8 and warns about untested later JVMs in its pinned source.
No compatible local server/graph/index deployment was qualified. Its project has
an actual Docker-contained REST client, original owned type/entity/lineage
payloads and a separately prepared native-host runbook. Native plan actions pass
without contacting a server. API/graph/index/authentication/lifecycle acceptance
must come from the real prepared server, not a replacement graph simulation.

Delta Sharing belongs to Delta Lake/Linux Foundation, not the Apache Software
Foundation. No matching 1.4.1 prebuilt reference-server asset/image was found.
Its separately prepared Scala server needs a supported actual table store/signing
path. The portable client implements real discovery/metadata/version/file requests
and PyArrow decoding for basic unpartitioned reader-version 1 responses. It checks
footer/type/row/uncompressed budgets before materialization, keeps recipient
credentials off storage requests, rejects redirects/unsupported features and
withholds credentials/signed URLs. Native offline plans are package/source
acceptance only, not an actual Sharing-server exchange or CDF/Delta feature test.

## Preparation and resource contract

Learners use Docker+Bash, including WSL 2 on Windows, without host SDKs. Ordinary
pads never install packages or start services. Copy each project into an owned
work directory and prepare software explicitly before use. Saved owner/project/
image fields override ambient Compose values; native guards prevent implicit
architecture fallback. Resume starts existing containers without build/pull.

The official registry blob endpoint failed verified TLS on this host. No TLS
check was disabled. Kafka/Cassandra/Flink/Pinot use the documented official
checksum-verified archive alternative on compatible already prepared bases.
Hive's explicit mirror choice selects the exact reviewed native child manifests
from its pinned upstream indexes; missing mirror attestations are not substituted
with another release or moving tag. Hive is JRE 21; its separate java21 worker
compiles the real release metadata SDK during preparation, and runtime validates
source/class/image identity before loading the class locally inside the container.

Start one heavy pack at a time and inspect Docker VM capacity separately from
host disk. Service limits are fixture safety budgets, not production forecasts.
The documented limits are roughly 1 GiB for Flight,1 GiB for Kafka,2.5 GiB for Flink,
2 GiB single / 6 GiB replicated Cassandra,3 GiB Pinot roles plus one-shot ingestion, and
3.5 GiB Hive/PostgreSQL plus its one-shot client. Other active work and extraction/
layer export require additional capacity. RF3 needs at least 8 GiB allocated engine
memory and still shares one physical host failure domain.

All generated private owner/credential/cache state is excluded from source
payloads. No engine socket, ambient cloud account or kubeconfig is mounted into
ordinary workers. Down retains state; confirmed destroy removes only verified
owned synthetic data. Unknown outcomes are reconciled without blind replay.
Failed observations and corrected-source results remain distinct receipts.

## Primary inputs

- [Arrow installation](https://arrow.apache.org/docs/python/install.html)
- [DataFusion Python](https://datafusion.apache.org/python/user-guide/introduction.html)
- [PyIceberg](https://py.iceberg.apache.org/)
- [Ballista Python](https://datafusion.apache.org/ballista/user-guide/python/quickstart.html)
- [Airflow images](https://airflow.apache.org/docs/docker-stack/index.html)
- [Kafka releases](https://kafka.apache.org/community/downloads/)
- [Flink downloads](https://flink.apache.org/downloads/)
- [Cassandra releases](https://cassandra.apache.org/_/download.html)
- [Pinot releases](https://pinot.apache.org/download/)
- [Hive release compatibility](https://hive.apache.org/general/downloads/)
- [Atlas pinned JVM/dependencies](https://github.com/apache/atlas/blob/release-2.5.0/pom.xml)
- [Delta Sharing reference server](https://github.com/delta-io/delta-sharing/tree/v1.4.1)

The descriptor inventory is [upstream-images.json](upstream-images.json).
Descriptors establish availability, not actual execution. Each project's public
qualification file and retained private receipts define its precise feature scope.
