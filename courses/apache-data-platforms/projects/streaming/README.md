# Kafka streaming workshop

This project starts only its owned Kafka broker. Flink and Pinot preparation
belongs to their separate projects; no other service is implicitly started here. The explicitly selected
binary route has passed actual native Linux ARM64 checks: exact keyed records,
invalid replication and unknown-topic errors, duplicate-free fixture initialization,
exact container reuse on stop/resume, data/cluster retention after replacement,
transaction isolation, committed consumer offsets and independent reader groups.
The disposable test resources were removed after the checks.

The upstream Kafka image has verified AMD64/ARM64 descriptors, but its blob
download failed TLS verification on the authoring engine. That image itself has
not been runtime-qualified here. The alternative below uses the same Kafka 4.4.0
release from Apache's official distribution and verifies its published SHA512
before extraction. No TLS verification is disabled and no route switches silently.

## Upstream image workflow

Copy this whole directory into a fresh learner-owned location from the repository
root. Keep the copied `.env` and named volume to resume the same workshop later.

```bash
mkdir -p work
cp -R courses/apache-data-platforms/projects/streaming work/apache-streaming
cd work/apache-streaming
bash run.sh prepare
bash run.sh start
bash run.sh check
```

`prepare` explicitly pulls the pinned official multi-platform Kafka 4.4.0 image
for the actual native Docker engine architecture. It does not authenticate or
publish images. Unsupported engine architectures fail before a pull. The launcher
never silently requests AMD64 emulation on ARM. `start` uses existing local images
and creates a unique owned project and Kafka cluster ID. No host SDK is needed.

The topology has one Kafka process serving broker and KRaft controller roles,
two data partitions, and replication factor one. The container is limited to one
CPU and 1 GiB memory, with a 512 MiB JVM heap. This is a teaching topology without
replica or controller high availability. A broker restart can preserve disk data;
it cannot keep this one-node service available while the broker is down.

The client runs inside the broker container using upstream command-line tools.
Kafka advertises `kafka:9092` on the private Compose network. No host listener is
published. A host application cannot use this internal name directly. Later
multi-service clients will share this network; adding a host listener requires
an explicit loopback binding and a correctly advertised host port.

## Explicit verified-binary alternative

When the upstream image is unavailable through a trusted download path, prepare
the existing native Java 21 classroom image from the repository root:

```bash
./classroom build --profile java21
```

In a fresh copied workshop directory, explicitly select the alternative:

```bash
bash run.sh prepare --binary
bash run.sh start --binary
bash run.sh check
```

The build downloads the official Kafka 4.4.0 binary archive inside Docker, checks
the exact reviewed SHA512, rejects unsafe archive entries and installs the binaries
on the prepared Java 21 image. It needs no host Java, Maven or Python installation.
The resulting local image is `ds60-apache-kafka-binary:4.4.0`; it is not an image
published by Apache and it is not uploaded by these commands. See the
[binary input lock](binary-image/artifact-lock.json) for its source and checksum.

The chosen route is saved in `.env`. Subsequent `resume`, `check` and `start`
commands reuse that choice without `--binary`. Trying `start --binary` on a saved
upstream-image workshop fails explicitly. Use a separately owned copy to test the
other route; changing image provenance is not an automatic recovery operation.
The launcher validates the actual native base/image architecture and refuses
implicit emulation. ARM64 execution has been qualified locally; AMD64 execution
remains a separate native acceptance gate.

## Expected checks and repeatability

The checker creates `classroom-events` only if absent, then produces three keyed
synthetic orders only when its log is empty. It verifies all key/value payloads,
including the distinction between source order and partition-local ordering.
Running the checker again must leave the same three log records. This is
idempotent fixture initialization, separate from Kafka producer deduplication.

It also requires failure when a topic requests replication factor two from the
single-broker set and when an unknown topic is described. A nonzero command alone
is not evidence of the intended rejection; runtime qualification must inspect
these actual diagnostics. Existing unexpected data causes an explicit failure,
not an automatic topic deletion or reset.

## Transaction, consumer and retention observations

The explicit binary route includes the prepared JDK needed by the Java clients:

```bash
bash run.sh check-transactions
bash run.sh check-consumers
bash run.sh check-retention
bash run.sh check-schema
```

The transaction probe checks exact committed and aborted payload visibility:
`read_committed` returns three records and `read_uncommitted` returns four. Two
separate identical business send calls remain two committed records despite
producer idempotence. No injected network-retry deduplication is claimed.

The consumer probe observes replay before commit, retained next offsets after
commit, zero rows on committed resume, and full reads by a different group. It
uses manual assignment and therefore makes no actual rebalance claim. Its unique
temporary group metadata is deleted after all consumers close; source records
remain.

The retention probe verifies actual one-partition/RF1 metadata and `cleanup.policy=compact`
through the Kafka Admin API. It initializes three updates only when the source end
offset is zero, then reads with a bounded KafkaConsumer until its actual end position.
A valid cleaner may already have removed offset 0 (`acct-1=v1`), so two or three
physical records are accepted. Offsets 1/2, their exact latest payloads, source end
offset 3 and the latest state (`acct-1=v2`, `acct-2=v3`) remain mandatory. Other,
duplicate, partial or changed data is rejected without reset.

The JSON records SHA256 of exact `retention-events.txt` bytes, observed offsets,
physical record count and latest-key state. It always reports
`physical_compaction_demonstrated:false`: this is compaction-tolerant readback,
not a forced-cleaner experiment. Offsets are positions and are not renumbered
when old data is removed. Waiting for exactly three physical messages would be
incorrect after legitimate compaction.

The tiny noncompacted `classroom-events` and `classroom-transactions` study topics
explicitly use `cleanup.policy=delete`, `retention.ms=-1` and `retention.bytes=-1`.
Each checker validates the actual effective configuration and topology, so valid
week-old study data cannot expire merely because of the broker's time/byte defaults.
Initialization remains bounded and runs only for an empty fixture. Unexpected
existing policy or payload is preserved and rejected; no topic is silently altered,
reseeded or deleted. This is a bounded teaching policy, not a recommendation for
an unbounded production stream.

The ordinary event checker also reports exact source-file SHA256 and per-partition
end positions for keys `0` and `1`, totaling three. Transaction visibility stays
strict at three committed versus four uncommitted data records. Compaction is the
only fixture whose historical physical count may shrink. Consumer-group offset
retention is a separate broker policy; the temporary group test cleans up only
its own group metadata.

The schema action is a separately labeled local JSON reader validator, not a
schema-registry deployment or broker enforcement. It accepts one additive field
and rejects a missing, string or Boolean amount. It uses the prepared Python
interpreter in the binary route. All commands use fixed bounded fixtures; they
are not arbitrary cluster-administration interfaces.

## Stop, resume and retained data

```bash
bash run.sh stop
bash run.sh resume
bash run.sh check
bash run.sh down
bash run.sh start
bash run.sh check
```

`resume` starts the retained broker container without a build or pull. `down`
removes only owned containers/network and retains the Kafka volume. Starting again
checks that persisted `meta.properties` matches the saved cluster ID. Data without
valid metadata is refused rather than automatically reformatted.

The volume holds Kafka logs and KRaft metadata. `.env` holds the independent
workshop identity. Neither is stored in the image. Moving only the source folder
to another Docker engine does not copy its named volume or the retained log.
Backups and migration need an explicit data-transfer procedure.

## Diagnostics and cleanup

```bash
bash run.sh status
bash run.sh logs
bash run.sh down
```

The separate destructive command below removes only this workshop's verified
owned volumes as well as its containers/network:

```bash
bash run.sh destroy --confirm-owned-data-loss
```

Do not delete volumes while expecting to preserve progress or source events. The
launcher validates labels on every affected container, network and volume before
mutation and never performs a global prune. It requires a local Unix-socket Docker
context, including Docker through WSL 2 on Windows.

## Source and version references

- [Apache Kafka 4.4.0 release](https://kafka.apache.org/community/downloads/)
- [Official Kafka Docker image source](https://github.com/apache/kafka/blob/4.4.0/docker/jvm/Dockerfile)
- [Official single-node KRaft configuration example](https://github.com/apache/kafka/blob/4.4.0/docker/examples/docker-compose-files/single-node/plaintext/docker-compose.yml)
- [Course platform descriptor inventory](../../authoring/upstream-images.json)

The Compose file pins the combined upstream image digest, not an ARM-only child.
Each platform's published descriptor still needs actual native acceptance. Kafka
is an Apache project. Future Delta Sharing integration belongs to its separately
identified Delta Lake/Linux Foundation service pack.

## Reuse a published Java base from Docker Hub

If the matching combined release exists, replace `yourname` with its publisher's
namespace and prepare the same local Java 21 alias without rebuilding the base:

```bash
docker pull yourname/ds60sqlpy:1.0.0-worker-java21
docker tag yourname/ds60sqlpy:1.0.0-worker-java21 ds60sqlpy-worker-java21:1.0.0
```

Docker chooses the native architecture from that manifest; the workshop verifies
it before the explicit `prepare --binary` build. This is a pull and local tag,
with no registry push. Combined worker tags include `worker-`. The workshop still
prepares its checksum-verified Kafka distribution separately.
