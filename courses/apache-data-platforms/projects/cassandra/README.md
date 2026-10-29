# Actual Cassandra CQL workshop

This separate project prepares Apache Cassandra 5.0.9 from its official binary
archive, checks the published SHA512 before extraction, and runs a real local
CQL node. It is not a Python simulation or an ordinary classroom pad. The single-node native Linux ARM64 path has passed actual CQL, SAI, conditional
updates, TTL/delete, snapshot/SSTable restore and retained-state lifecycle checks.
The optional three-node RF3 outage path has also passed native ARM64 acceptance, exact three-container resume and retained three-volume replacement with read-only host-UUID/value/policy comparison. Actual AMD64
execution is reserved for native hosted runners; no local emulation is used.

The base is the prepared classroom Scala/JVM image because it contains Java 17.
Cassandra 5 must not inherit Java 21 just because another lesson uses that JDK.
The image additionally prepares Cassandra Python driver 3.30.1 and its hash-locked
native dependencies during build. No package installation occurs while reading
or running a tutorial.

## Preparation and startup

From the repository root, prepare the native Java 17 base:

```bash
./classroom build --profile scala-jvm
mkdir -p work
cp -R courses/apache-data-platforms/projects/cassandra work/apache-cassandra
cd work/apache-cassandra
bash run.sh prepare
bash run.sh start
bash run.sh check
```

The explicit prepare step builds only the local `ds60-apache-cassandra-binary:5.0.9`
image with visible logs and no registry login or push. It is not an image published
by Apache. The archive source/checksum is in `binary-image/artifact-lock.json`.
The launcher refuses wrong-architecture bases before building and never silently
requests AMD64 emulation on ARM.

First start records a unique workshop identity in `.env` and creates one owned
named volume. The node has two CPUs, a 2 GiB container limit and 768 MiB JVM heap.
Its direct-memory limit is explicitly 256 MiB, independent from the Docker VM
size. Its logs, commitlog, data files, hints and caches live in that volume; configuration
is generated in temporary memory from the pinned release. No host ports or engine
socket are exposed. The prepared Python client runs on the private project
network and requires no host Python, compiler, Java or Cassandra installation.

## Use a published Hub Java 17 base

Once the matching combined release is published, the base can be pulled and given
the existing local alias instead of rebuilding the Scala/JVM runtime. Replace
`yourname` with the publishing namespace:

```bash
DS60_HUB_ACCOUNT=yourname
docker pull "$DS60_HUB_ACCOUNT/ds60sqlpy:1.1.0-worker-scala-jvm"
docker tag "$DS60_HUB_ACCOUNT/ds60sqlpy:1.1.0-worker-scala-jvm" \
  ds60sqlpy-worker-scala-jvm:1.1.0
```

Back in the copied workshop directory, use `bash run.sh prepare` to build the small Cassandra layer from its pinned
official archive and native client locks. No image upload or host SDK installation
is involved. Use concrete release tags, not a moving latest alias, for this base.
Manual publisher tags additionally include their explicit native architecture.

## Exact observations

The bounded client verifies a three-order retained fixture, a customer partition's
clustering order, rejection of an unsupported unindexed filter, RF 1 reads at ONE
and QUORUM, and real unavailability for a TWO-replica read. A one-node topology
cannot demonstrate multi-node consistency, replication or availability.

It performs a successful conditional update, rejects a stale condition and
conditionally restores only that known probe value. It also checks explicit
write-timestamp ordering and observes logical TTL expiry under a deadline.
Logical expiry does not prove physical tombstone removal or secure erasure.
Unexpected retained order or conditional-update state is rejected without a reset.
The complete source is `client.py`; outputs remain explicit about unproved claims.

## Real table-level snapshot and restore

```bash
bash run.sh check-backup
```

This explicit single-node action snapshots the known source table, copies its
SSTable components into a correctly named keyspace/table staging layout, imports
them with extended verification into a separate restore target and checks every
order identity and value. It preserves original source bytes and data. Staging
and the exact snapshot tag are cleaned; the restored table and atomic source-bound
receipt remain in owned state for inspection. At most four successful or partial
restore targets are retained per workshop. Export evidence before explicit project
destruction if it is still needed.

A completed restore and a failed evidence write are reported separately. A storage
warning does not mean the restore was rolled back, and is not permission to replay
it blindly. This local table-level exercise does not establish remote backups or
whole-cluster disaster recovery. It deliberately refuses the replicated topology.

## Optional three-node replica workshop

This topology uses the same native image and no extra downloads, but requires at
least 8 GiB allocated to the Docker engine and sufficient remaining capacity for
three 2 GiB node limits. Keep it separate from the single-node saved project. From the repository root:

```bash
cp -R courses/apache-data-platforms/projects/cassandra work/apache-cassandra-replicated
cd work/apache-cassandra-replicated
bash run.sh start --replicated
bash run.sh check-replication
```

Initial nodes bootstrap sequentially
rather than bypassing range-movement safety. The saved topology cannot switch
silently. The outage check writes or validates one value at RF3/ALL, stops two
verified owned nodes, observes ONE versus QUORUM, resumes those exact containers
and checks recovered quorum readback. Native ARM64 qualification passed this outage and recovered quorum readback. Actual native AMD64 remains a separate hosted-runner gate.
Three containers share one physical Docker-engine failure domain.

A cancelled outage can leave the selected nodes stopped if its process was killed
before cleanup. Inspect `status`, then use `resume` to recover the exact saved
containers. That recovery does not rerun or fabricate the interrupted observation.

## Resume, replacement and cleanup

```bash
bash run.sh stop
bash run.sh resume
bash run.sh check
bash run.sh down
bash run.sh start
bash run.sh check
bash run.sh status
bash run.sh logs
```

Resume reuses the retained container without builds or pulls. Down removes owned
containers/network but preserves the data volume. Start after down replaces the
process over retained data. Actual survival across these boundaries must be
qualified separately from successful initial startup.

To remove only this workshop's verified owned data after it is no longer needed:

```bash
bash run.sh destroy --confirm-owned-data-loss
```

Keep `.env` with the copied project. The launcher checks exact ownership labels,
uses a PID-marked lock, accepts only a local Unix-socket Docker context and never
runs global prune. Windows learners use their WSL 2 terminal and Linux Docker
engine. No automatic stale-lock takeover or data reset occurs.
