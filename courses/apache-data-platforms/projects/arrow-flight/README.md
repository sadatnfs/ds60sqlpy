# A real Arrow Flight workshop

This project starts an actual Arrow Flight server and transfers record batches
through its client protocol. It is separate from an ordinary classroom pad.
The actual native Linux ARM64 Docker checks cover exact reads, unknown
tickets/descriptors, client namespace diagnostics, exact-container resume and
retained-volume replacement. Native AMD64 acceptance is a separate gate.

Prepare the classroom runtime from the repository root:

```bash
./classroom build --profile data-platforms-python
```

No host Python, compiler or SDK is required by the Docker workshop once the image
exists. Reading the lesson does not prepare or start this separate service.

Copy this complete directory into a new learner-owned location from the repository
root. Do not copy it over an existing workshop directory or maintained sources.

```bash
mkdir -p work
cp -R courses/apache-data-platforms/projects/arrow-flight work/arrow-flight
cd work/arrow-flight
bash run.sh start
bash run.sh check
```

The first start creates a unique project/ownership marker in `.env` and a named
volume holding one three-row Parquet fixture. The server mounts that data read-only.
An initializer verifies existing data rather than replacing it. All image operations
use an existing local image; this launcher does not build, pull or authenticate.
No host port is published. Services communicate on an internal project network.
Use `bash run.sh check` to run the real client within that network; the service
name `server` resolves there, not in a host terminal or browser.

The successful client reports three rows, an east-region total of 11, a logical
source SHA256 and three rejected invalid tickets. An unknown descriptor is also
rejected. The client limits receive-message size, response rows, batches and bytes.
This is one immutable demonstration dataset, not a general remote query service.
There is no authentication in this local fixture and it must not be exposed to a
public interface. The strict allowlisted ticket is a data-selection boundary, not
an identity or authorization system.

## Reuse already published Hub runtime images

If you prefer published combined release images, replace `yourname` with the Hub
namespace and use the concrete release matching this checkout. These commands
pull native platform variants and add the local aliases expected by the workshop;
they do not rebuild or push anything.

```bash
DS60_HUB_ACCOUNT=yourname
docker pull "$DS60_HUB_ACCOUNT/ds60sqlpy:1.0.1-worker-data-platforms-python"
docker tag "$DS60_HUB_ACCOUNT/ds60sqlpy:1.0.1-worker-data-platforms-python" \
  ds60sqlpy-worker-data-platforms-python:1.0.1
docker pull "$DS60_HUB_ACCOUNT/ds60sqlpy:1.0.1-worker-rust-stable"
docker tag "$DS60_HUB_ACCOUNT/ds60sqlpy:1.0.1-worker-rust-stable" \
  ds60sqlpy-worker-rust-stable:1.0.1
```

Rust is needed only for `ipc-check`. The standard Flight client/server path needs
the data-platforms image. These combined tags must have been published first;
a manual architecture-tag set uses the corresponding explicit native suffix
instead. See [the Docker Hub guide](../../../../docs/dockerhub.md) for both layouts. A native image
mismatch fails before the workshop starts; no implicit emulation is selected.

## Network namespaces and cross-language IPC

```bash
bash run.sh network-check
```

This resolves the real `server` service name inside the client container, completes
the exact Flight read, and requires a bounded failure when that client tries its
own loopback address. The service publishes no host port. Reported container IPs
are temporary observations, not addresses to copy into configuration.

For actual Python/Rust IPC, first prepare the native Rust image from the repo root:

```bash
./classroom build --profile rust-stable
```

Back in the copied workshop:

```bash
bash run.sh ipc-check
```

This compiles `ipc_bridge.rs` against the image's prepared Rust Arrow 60 library
without Cargo resolution or downloads. Python Arrow 23 writes a nullable three-row
stream, Rust reads and rewrites it, and Python verifies exact schema, values and
nulls. Temporary stream files are removed after the check. Both images must match
the actual native engine architecture; implicit emulation is refused.

The demonstrated IPC transfer is distinct from the in-process C Data Interface
and the network Flight protocol. It does not measure or promise zero copying at
every boundary, or establish compatibility for every possible extension type.

## Restart and persistence

```bash
bash run.sh stop
bash run.sh resume
bash run.sh check
```

`resume` starts the exact retained server container, without rebuilding or pulling.
The source SHA256 and results should match the first successful read. To replace
containers while retaining data, use `down`, then `start` and `check`. The initializer
refuses mismatched data or an incomplete fixture instead of silently resetting it.
This demonstrates durable local data across service replacement. It does not test
replication, high availability or recovery from a lost Docker volume.

## Inspection and cleanup

```bash
bash run.sh status
bash run.sh logs
bash run.sh down
```

`down` retains the named fixture volume. After deciding the workshop data is no
longer needed, the following explicit command removes only this project's verified
containers, network and volumes:

```bash
bash run.sh destroy --confirm-owned-data-loss
```

Every lifecycle operation checks the ownership label on affected resources before
mutation. It never runs global prune. Keep `.env` with your copied project so the
next session can identify its state. The launcher accepts only a local Unix-socket
Docker context, including Docker through WSL 2 on Windows. A stale `.workshop-lock/pid` identifies the interrupted host process. Check that
process has ended before manually removing its PID file and empty lock directory.
A live or uncertain owner must not be removed; no automatic stale-lock takeover
is attempted.

## Files and limitations

`service.py` defines the actual Flight service, fixed descriptor and ticket.
`client.py` verifies semantic data, identity and failures independently.
`compose.yaml` supplies the Linux process, network, resource and state boundaries.
`run.sh` controls the project lifecycle; it does not execute inside the classroom
worker and does not mount the Docker socket into any service.

The fixed three-row example is designed for understanding the protocol. It does
not measure bandwidth, prove secure multi-tenancy or support arbitrary file paths.
The server intentionally rejects unknown ticket bytes, including path-like values.
