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
to127.0.0.1 and refuses remote Docker endpoints. The companion uses POSIX
permissions on Linux, WSL 2 or macOS. Native Windows credential reads and host
preparation are unsupported and refuse before mutation. Windows users run the
companion inside WSL 2 with Linux paths and a local Unix-socket Docker endpoint;
named-pipe endpoints are unsupported. Do not hand a Windows path to a Linux CLI.

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
docker build --progress=plain -f docker/kubernetes/Dockerfile.fixture -t ds60sqlpy-k8s-fixture:0.2.0 .
docker build --progress=plain -f docker/kubernetes/Dockerfile.worker -t ds60sqlpy-worker-k8s-kind:0.4.0 .
```

Use the local engine endpoint reported by the existing launcher doctor. For
Rancher Desktop on macOS, the common endpoint is the user's `.rd/docker.sock`;
other engines may use a different socket. This is an example only when that is
the engine you selected:

```bash
python scripts/prepare_kubernetes.py prepare --confirm-create \
  --docker-host "unix://$HOME/.rd/docker.sock" --allow-node-download
```

On Windows, run the same Bash/Python preparation inside WSL 2 and use the
Unix-socket endpoint reported by Docker in that Linux terminal.

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
`DS60_K8S_SESSION_DIR` value in the launching shell. Both optional Compose routes
mount the lease and scoped kubeconfig from this explicit directory. Their
worker HTTP credential comes from different storage:

- The primary Docker classroom uses `compose.classroom.kubernetes.yaml` with
  `compose.classroom.yaml`. Its initializer owns the private `classroom-runtime`
  named volume, shared read-only with the app and broker. This route does not
  require `DS60_MODULE_RUNTIME_DIR`.
- The older host-folder launcher uses `compose.kubernetes.yaml` with its module
  Compose files. It mounts the `worker-token` file beneath the explicit
  `DS60_MODULE_RUNTIME_DIR` prepared by that launcher.

Keep each route's matching initializer, credential storage and Compose files
together. Neither broker publishes a host port or receives a daemon socket or
host administrator kubeconfig. It joins only the module-private network and the
kind network needed for its owned internal API endpoint.

The worker must prove that demoted UIDs65533 and65534 cannot read the original
supervisor credentials, verify the namespace UID/owner against its private
lease, and disable readiness when that probe or lease becomes invalid. Kubectl
runs as the separate credential-only UID65533. Learner YAML cannot choose an
image, command, namespace, host path, plugin, proxy, context or credential.

The original hello path supports the fixed-name Deployment and optional Service;
the contract-2 extension below adds a bounded ConfigMap and a standalone finite task.
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


The [module runtime walkthrough](../../docs/modules-runtime.md#prepare-and-run-the-owned-kubernetes-lab)
connects build, private host preparation, explicit-session start, stop and
release. Prepare after building because the scoped lease lasts15 minutes.
Release/failed-preparation cleanup targets only the recorded 64-character hexadecimal Docker
node ID. It does not run a name-based global kind cleanup or remove shared
networks. Same-name replacements and ambiguous engine failures preserve the
private recovery evidence.


## Fixture contract 2 and bounded ordinary labs

The current fixture image is `ds60sqlpy-k8s-fixture:0.2.0`. It preserves `/ready` and the `ds60-fixture-v1` `/version` response while adding only synthetic `/message`, `/file-message`, `/startup` and `/live` responses plus a finite `task` command. A fresh owned lease is required for ConfigMap access. Existing saved learner manifests are never rewritten; a 0.1.0 image reference receives an actionable refusal.

The extended operation accepts either the fixed hello Deployment, optional hello Service and optional hello-config ConfigMap, or one standalone hello-task Job. ConfigMap data is exactly one message with value hello or reviewer. Only its fixed environment reference or read-only `/config/message` mount is admitted. Startup delay is zero or three seconds. Probes use fixed local HTTP paths and bounded periods/thresholds. The finite task has one completion, one parallel Pod, at most one retry and a 5-30 second active deadline. Its only selectable behavior is a fixed success or injected failure outcome.

Pod and EndpointSlice readiness are followed by a separate HTTP proof. Service
forwarding updates are asynchronous, as described in the
[Kubernetes virtual IP documentation](https://kubernetes.io/docs/reference/networking/virtual-ips/).
The fixed client retries transient connection/DNS failures and HTTP 503 within
one shared six-second budget for all version and message reads. Wrong bodies,
invalid URLs, oversized or malformed responses, and redirects fail immediately.
Every fixed HTTP client Job has a sixteen-second deadline, allowing for
Kubernetes scheduling and container startup before its shared six-second HTTP
budget begins. Job retries remain disabled. The caller's operation deadline
still takes precedence, even when shorter than the Job deadline, and owned
cleanup retains its separate reserve. Learner source is never replayed.
Failed owned Jobs expose only
reviewed reason labels, while validation reports retain bounded status and check
results without copying raw output, source or API messages.

The scoped Role adds namespaced ConfigMap creation plus get/delete restricted to hello-config. It adds no Secrets, exec, arbitrary commands, mutable role, host mount or ambient context access. Job completion now also requires a Pod whose namespace, controller Job UID, Run nonce, container identity and zero exit status agree. The finite task's bounded JSON log must match its independent 3-accepted/2-rejected/35-total ledger. Cleanup retains namespace identity, owner/nonce checks, UID-precondition deletion and an independent reserve, including ambiguous create recovery.

Curated inputs are [configured hello](../../courses/kubernetes/fixtures/hello-configured.yaml), [finite task](../../courses/kubernetes/fixtures/hello-task.yaml), [injected task failure](../../courses/kubernetes/fixtures/hello-task-failure.yaml) and [startup/liveness fixture](../../courses/kubernetes/fixtures/hello-startup.yaml). The current source and fake-backed tests do not by themselves qualify the new image or lease. Actual image build, node preload, positive/negative cases, cancellation and cleanup receipts must be recorded by the runtime owner before claiming readiness. Stateful updates, arbitrary Jobs, PVCs, CNI policy, Gateway/CRD installation and node operations remain separate host-lab capabilities.
