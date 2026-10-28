# Real Ballista on one Docker host

This optional project runs released Ballista 54.1.0 native scheduler/executor code
through its Python binding, with DataFusion 54 and Arrow 23.0.1. One scheduler and
one executor run as independent native processes with an independent client on
one container host. It is actual
RPC, scheduling, shuffle and query execution, not a Python mechanism model. It
has no multi-host or high-availability claim. See [qualification](QUALIFICATION.md)
for actual platform acceptance and limitations.

Ordinary classroom pads do not start services or run these commands. Use a Linux,
macOS or Windows/WSL2 terminal with a local Docker engine and Compose 2.28 or later.
No host Python, Rust, compiler or database is required.

## Prepare and start

From the repository root, copy the complete folder into a fresh owned directory:

```bash
mkdir -p work
cp -R courses/apache-data-platforms/projects/ballista work/ballista
cd work/ballista
bash run.sh prepare
bash run.sh start
bash run.sh check
```

Preparation builds an isolated image from pinned Python 3.12/Trixie and hash-locked
native packages. Linux/glibc 2.39 or later is required by the released Ballista wheel.
Both AMD64 and ARM64 wheel closures were resolved. The launcher inspects the native
engine and refuses other architectures or implicit emulation before preparation.
Prepared dependencies are never fetched during lesson execution.

An explicit local fallback can reuse an already prepared native Swift/Noble
classroom image, which has Python 3.12 and glibc 2.39. This avoids another base pull
but does not make Ballista depend on Swift language features:

```bash
bash run.sh prepare --reuse-swift
bash run.sh start
bash run.sh check
```

Use that preparation in a fresh project copy. Its distinct image and route are
saved in the regular private `.env` ownership record. A saved route is not silently
changed. The preparation script validates the pinned pip bootstrap wheel and all
package hashes. `requirements.in`, architecture locks and `upstream.json` record
the environment. No TLS verification is disabled.

## Read, inspect and compare

```bash
bash run.sh paths
bash run.sh plans
bash run.sh clients
bash run.sh bounded-output
bash run.sh evidence
bash run.sh status
bash run.sh logs
```

The canonical source has 200 deterministic orders. The checker derives expected
region counts and sums independently, then compares actual Ballista and embedded
DataFusion 54 outputs. `paths` detects a removed disposable source through its independent row-identity
oracle, because this release returns an empty listing rather than an engine
exception. It never touches
the canonical data. `plans` records actual plan text and a hot-key query. `clients`
checks a supported Python DataFrame action. `bounded-output` limits returned rows
and bytes. Plan text is diagnostic; exact result identities remain the oracle.

`evidence` reads retained receipts and never runs their queries again. At most 64
bounded receipts are retained; reaching the limit fails explicitly. Export or
review owned evidence before deliberately making room, rather than automatically
deleting learning history. A failed query receipt distinguishes the actual error
from a later fresh request. Never infer safe replay from an unknown outcome.

## Capacity, failures and resume

```bash
bash run.sh one-slot
bash run.sh check
bash run.sh two-slots
bash run.sh check
bash run.sh failure-check
```

All native processes stay in one container with a fixed bounded allocation.
Task-slot changes are explicit quiescent reconfigurations that restart the native
scheduler/executor pair. They do not preserve scheduler job state. A whole-container
restart returns to the documented one-slot default; saved source and receipts remain.
One versus two task slots is not a claim of doubled physical capacity. The failure
check stops the only owned executor, retains a bounded failed/unknown client
receipt, reaps that client, restores capacity, then
restarts the scheduler/executors while reading prior receipts without replay.
It does not claim interruption of an identified in-flight task or durable scheduler
job-history recovery. The released wrapper uses its default scheduler backend.

```bash
bash run.sh stop
bash run.sh resume
bash run.sh evidence
```

Resume starts the exact retained cluster container without a build or
pull. `down` removes only owned containers/network and retains the fixture/evidence
volume. `start` can replace containers while verifying retained source bytes.

## Scope and cleanup

No host ports, engine socket, cloud credentials or unrelated data are mounted.
Source is read-only inside services. The initializer owns its named fixture
volume. The canonical source is verified before each query; the shared process
container has a writable owned data/evidence mount and bounded ephemeral shuffle
storage. The shared cluster has a 2 GiB memory limit, two CPUs and 256 processes, including
its separate short-lived client, with 512 MiB ephemeral shuffle storage. These are limits,
not measured peak-usage promises.

```bash
bash run.sh down
```

After deciding the disposable workshop evidence is no longer needed:

```bash
bash run.sh destroy --confirm-owned-data-loss
```

Every affected resource must match the project ownership labels. There is no
global prune. Keep `.env` to identify the same project later. A PID-marked lock
prevents concurrent lifecycle actions; inspect a stale owner before removing only
that lock's files. Moving source to another Docker engine does not migrate volumes.

The separately prepared [native Rust client](rust-client/README.md) is not the
ordinary Rust pad. Its source, compilation and actual server readback have separate
qualification gates. The prepared Python route already invokes real Rust services.

## Released wrapper networking limitation

The54.1.0 Python scheduler wrapper configures the listener but does not expose its
advertised external host. The native default remains localhost. Actual testing
found that separate-container executors could listen successfully while callbacks
to that advertised address failed. The first query timed out and its failed
receipt was retained. This project therefore uses separate processes in one
container namespace, where the advertised loopback address is correct. It does
not rewrite DNS or claim cross-host shuffle. A configurable native-binary multi-
executor deployment requires separate preparation and qualification.

## Reuse a published classroom base from Docker Hub

If the matching release is published, prepare the same local base alias without
rebuilding it. Replace `yourname` with the publisher's namespace. Docker selects
the native architecture from the combined manifest:

```bash
docker pull yourname/ds60sqlpy:1.0.0-worker-swift-linux
docker tag yourname/ds60sqlpy:1.0.0-worker-swift-linux ds60sqlpy-worker-swift-linux:1.0.0
```

Then use the explicit `--reuse-swift` preparation in a fresh copied workshop. The
launcher still verifies the native image architecture. This pulls and locally
retags an existing Swift/Noble base; it does not push an image or rebuild that base.
The separate workshop dependencies are prepared by the explicit workshop command.
Combined worker tags include `worker-`; `1.0.0-swift-linux` is not this layout.
