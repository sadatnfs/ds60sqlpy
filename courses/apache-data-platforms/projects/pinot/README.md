# Owned Apache Pinot serving project

This separate workshop runs four actual roles from Pinot 1.5.1: ZooKeeper,
controller, broker and server. Private service DNS connects them. It creates a
three-order offline segment from checked-in synthetic JSON and queries through
the actual broker. There is no simulated serving engine and no Docker socket
inside any service. Native Linux ARM64 offline-service acceptance passed and is recorded in
[QUALIFICATION.md](QUALIFICATION.md).

## Prepare and initialize

Prepare the ordinary `data-platforms-python` classroom profile first, then copy
this entire directory into `work/apache-pinot`. Learners need Docker and Bash,
not host Java, Python or Maven. From the copied directory:

```bash
bash run.sh prepare
bash run.sh start
bash run.sh initialize
bash run.sh check
```

Prepare explicitly pulls the pinned official multiarch digest and creates the
local versioned alias. It does not publish an image. Native platform validation
precedes startup; ARM never requests AMD64 emulation. A verified TLS failure is
a failed preparation, with no automatic insecure workaround.

The four services each have a 768 MiB limit and 384 MiB JVM heap. The one-shot
client uses 256 MiB and ingestion temporarily needs another 768 MiB. Allow at
least 5 GiB available engine memory and adequate image storage. No ports are
published; the client runs on the isolated internal project network.

Initialize is deliberate and only creates an absent owned table. If the table
already contains the exact fixture, it returns without writes. An interrupted
empty or unexpected table is rejected for inspection. Check is read-only and
requires IDs 1/2/3, east total 11, west total 9, selective ID 3 and an actual
unknown-column query exception. It retains no invented latency guarantee.

## Lifecycle

```bash
bash run.sh identity
bash run.sh stop
bash run.sh resume
bash run.sh check
bash run.sh down
bash run.sh start
bash run.sh check
bash run.sh status
bash run.sh logs
```

Resume starts the exact saved containers. Down retains coordination, controller,
server and ingestion-staging volumes. Start after down uses retained state,
without initialization or segment replay. Keep `.env` with the copied source.
The launcher checks every affected container/network/volume ownership label.
It takes a PID-marked action lock and rejects unrecognized arguments.

Pinot QuickStart in this pinned release deletes temporary data in its shutdown
hook. This project instead launches the actual individual roles over distinct
persistent volumes so shutdown is not confused with data regeneration.

## Prepared advanced routes

`realtime-table.json` is a real Kafka connector configuration for the separately
owned integration route. Match its broker DNS, topic, schema and decoder to a
prepared private Kafka network before using it. It is not started automatically.
Hybrid boundaries, upserts and multistage joins are explained in the chapters
and require separate live source-offset/result evidence. Do not claim that an
offline segment test qualifies these features.

After exporting needed evidence, explicit deletion removes only owned data:

```bash
bash run.sh destroy --confirm-owned-data-loss
```

## Explicit official-binary alternative

When the pinned official image cannot be fetched with verified TLS, use this
separate route from a fresh owned copy, without disabling certificate checks:

```bash
bash run.sh prepare --binary
bash run.sh start --binary
bash run.sh initialize
bash run.sh check
```

Prepare builds a local layer on the already prepared native Scala/JVM Java17
base. It downloads the exact 857,203,581-byte Apache 1.5.1 binary, verifies its
published SHA512 before bounded path-safe extraction, and retains Apache license
and notice files. It is a locally built workshop image, not an Apache-published
container. Expect approximately 2 to 3 GiB temporary engine headroom during download,
extraction and layer export. Preparation/lifecycle use one action lock. A saved
project never switches routes automatically; resume does not build or pull.
