# Owned Kubernetes module preparation

This optional profile uses one dedicated kind node and a private scoped worker.
It is separate from ordinary Python/SQL startup. Source files and fake-backed
tests do not establish an installed cluster or a qualified platform. Keep the
main HTTP application stopped during provisioning acceptance unless explicitly
starting the module lab is part of the chosen test.

The pins are kind v0.33.0, kubectl v1.37.0, and
`kindest/node:v1.37.0@sha256:a1ed56cfb0e7b93589bdf97c8cd566405a265939e3620fc4f5de89adff580ae5`.
The [official kind release](https://github.com/kubernetes-sigs/kind/releases/tag/v0.33.0)
is the source of the node digest and architecture support. Tool preparation
retrieves official SHA256 metadata before publishing a downloaded binary.
[Kubernetes tool installation](https://kubernetes.io/docs/tasks/tools/) describes
the release/checksum distribution. TLS verification stays enabled. A registry
certificate failure is a preparation failure, not a reason to disable TLS or
change the node digest.

Before starting, check current host and engine-VM disk space, RAM allocation,
existing resources and download sizes. Budget the worker plus the control-plane
node separately from any Spark/TensorFlow worker. Stop other owned heavy tests
through their normal lifecycle before preparing this node. Do not prune unrelated
images, restart the engine or change its settings as an automatic repair.

Use the course's configured Python interpreter for the host companion. It never
reads or rewrites the user's default kubeconfig. It creates a new private runtime
directory, uses explicit kubeconfig/context arguments, binds the host API only
to127.0.0.1 and refuses remote Docker endpoints. The Windows implementation sets
and verifies a current-user/SYSTEM ACL on only that newly created directory;
actual native Windows acceptance remains a separate required test. WSL uses its
Linux tools and paths. Do not hand a Windows path to a Linux CLI.

Read-only inventory, from the repository root:

```text
python scripts/prepare_kubernetes.py doctor
```

Connected tool preparation is explicit and installs into the chosen tool cache,
not a global PATH or home configuration:

```text
python scripts/prepare_kubernetes.py tools --allow-download
```

Build the tiny fixture and optional worker only after the resource/download
preflight is approved. Both Dockerfiles accept a previously qualified
`DS60_PYTHON_IMAGE` base override. Building is a separate action; no job Run
performs an image pull or dependency installation.

```text
docker build --progress=plain -f docker/kubernetes/Dockerfile.fixture -t ds60sqlpy-k8s-fixture:0.1.0 .
docker build --progress=plain -f docker/kubernetes/Dockerfile.worker -t ds60sqlpy-worker-k8s-kind:0.3.0 .
```

Use the local engine endpoint reported by the existing launcher doctor. For
Rancher Desktop on macOS, the common endpoint is the user's `.rd/docker.sock`;
other engines may use a different socket. This is an example only when that is
the engine you selected:

```bash
python scripts/prepare_kubernetes.py prepare --confirm-create \
  --docker-host "unix://$HOME/.rd/docker.sock" --allow-node-download
```

For a native Windows Docker-compatible named-pipe endpoint:

```powershell
python scripts/prepare_kubernetes.py prepare --confirm-create `
  --docker-host 'npipe:////./pipe/docker_engine' --allow-node-download
```

`--allow-node-download` is required only when the pinned node bytes are absent.
The fixture must already exist locally and is explicitly loaded into the owned
kind node. Where the official registry path has a certificate-chain failure, an
explicit mirror option is accepted only with the **same** release/index digest:

```text
--node-image mirror.gcr.io/kindest/node:v1.37.0@sha256:a1ed56cfb0e7b93589bdf97c8cd566405a265939e3620fc4f5de89adff580ae5
```

The helper prints the private session path and nonsecret status; it never prints
the token, admin certificate or kubeconfig contents. Keep that directory outside
`.learning`, source, exported notes and backups. Save the returned
`DS60_K8S_SESSION_DIR` value in the launching shell. The optional Compose companion
uses this directory for the lease and scoped kubeconfig, and uses the existing
`DS60_MODULE_RUNTIME_DIR` credential for authenticated worker HTTP. It exposes
no worker host port, receives no daemon socket or host admin kubeconfig, and
joins only the module-private network and the kind network needed for its owned
internal API endpoint.

The worker must prove that demoted UIDs65533 and65534 cannot read the original
supervisor credentials, verify the namespace UID/owner against its private
lease, and disable readiness when that probe or lease becomes invalid. Kubectl
runs as the separate credential-only UID65533. Learner YAML cannot choose an
image, command, namespace, host path, plugin, proxy, context or credential.

The first Run supports only fixed-name hello Deployment and optional Service.
It verifies controller and Ready Pod identities, deduplicated ready EndpointSlice
Pod UIDs, and a fresh in-cluster `/version` client when a Service is supplied.
The client is a fixed broker-created Job; users cannot submit arbitrary Jobs.
Every Run cleans only its recorded owner+job-nonce+UID resources, including
readback recovery when creation committed but its response was lost. Deletion
sends an API UID precondition. The private cluster lease remains until explicit
host release. Rolling revisions, Pod-deletion tasks and second-Service transfer
remain scoped manual/teacher exercises in this initial adapter.

Release only the exact owned session after checking its receipt:

```text
python scripts/prepare_kubernetes.py release --session <PRIVATE_SESSION_PATH> --confirm-release
```

The helper checks the control-plane container ID, kind ownership label and
namespace UID before deletion. A replacement or ambiguous object is preserved.
It confirms the owned node is absent before removing its credential files.
Shared networks, public image caches, learner source/evidence and unrelated
containers remain intact. A failed partial preparation retains a private
recovery receipt; where the exact created node identity was recorded, cleanup
is attempted only for that unchanged node. Unproved partial state requires
explicit inspection rather than a broad delete-all or engine reset.
