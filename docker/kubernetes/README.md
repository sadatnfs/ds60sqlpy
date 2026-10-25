# Owned Kubernetes runtime and fixture

This optional extension uses a dedicated disposable kind node and a private
scoped worker inside the existing classroom. Start with the canonical
[prepare, inspect, start, stop and release walkthrough](../../docs/modules-runtime.md#prepare-and-run-the-owned-kubernetes-lab).
It uses `compose.classroom.yaml` plus the self-contained
`compose.classroom.kubernetes.yaml`; there is no separate host-folder launcher.

The host companion needs a prepared POSIX Python environment on Linux, WSL 2
or macOS and an explicitly selected local Unix-socket Docker endpoint. It never
reads or changes the default kubeconfig and never selects an ambient cluster.
Windows users run the companion inside WSL 2 with Linux paths. The ordinary
classroom still needs no host Python, kind or kubectl.

## Prepared inputs and private state

Current source pins are kind v0.33.0, kubectl v1.37.0 and the exact node image
listed as `NODE_IMAGE` in
[`kubernetes_module.py`](../../src/ds60sqlpy/kubernetes_module.py). The host helper
checks official release SHA256 metadata before publishing tool downloads.
TLS stays enabled. A reviewed mirror may change the node registry prefix while
preserving the exact approved release/index digest; a floating tag or disabled
TLS is not an equivalent input.

Review engine disk space and RAM before adding the worker and control-plane
node. Build both Dockerfiles and prepare the tools before creating a short-lived
session. Neither pressing Run nor opening a lesson installs a tool, pulls an
image or creates a cluster. The fixture image remains
`ds60sqlpy-k8s-fixture:0.2.0`; its protocol version is separate from the classroom
release version used for the worker image. Both Dockerfiles accept an explicit
`DS60_PYTHON_IMAGE` build argument for a reviewed base mirror.

The helper prints a private session path and nonsecret status, never the
credential body. Keep this directory outside source, `.learning`, exported
notes and portable backups. `DS60_K8S_SESSION_DIR` supplies the explicit lease
and scoped kubeconfig mounts. The classroom initializer owns the separate
`classroom-runtime` named volume containing the private worker HTTP token.
The overlay retains every ordinary/GPU worker endpoint and adds Kubernetes.
Its worker joins `module-private` and the owned `kind` network, publishes no
host port and receives no Docker socket or host administrator kubeconfig.

The worker must prove its demoted identities cannot read supervisor secrets,
verify the namespace UID/owner and reject invalid or expired leases. Kubectl
uses the dedicated credential-only UID 65533; ordinary isolated child work uses
UID 65534, and fixture Pods use UID 65532 without service-account token mounts.
Learner YAML cannot select arbitrary images, commands, namespace identities,
host paths, plugins, proxy settings or credentials.

## Lifecycle and cleanup evidence

Prepare requests a 15-minute token and records the returned expiry. Inspection
requires enough remaining lifetime for the longest work deadline and cleanup.
A stopped browser or container does not extend it. An expired session needs
scoped release and fresh explicit preparation, not timestamp edits or an
ambient admin fallback.

Each Run records resource identities, owner and a private nonce. Deletion uses
UID preconditions; ambiguous create responses can be recovered only under the
same owned identity. Work and cleanup have separate deadlines. A cleanup result
that cannot prove absence stays failed. SIGTERM requests bounded cancellation
before shutdown, and the Compose worker has a 30-second stop grace period.

Host release checks the full recorded node container ID, kind owner label and
namespace UID. It preserves replacements and ambiguous resources, proves the
owned node is absent, then removes credential files. It does not delete learner
volumes, shared networks or unrelated engine resources. Partial preparation
retains private recovery evidence; do not replace identity checks with a broad
name-based cleanup.

Source tests and image definitions do not establish a working cluster. Record
actual build, preload, lease, positive/negative operation, cancellation and
cleanup evidence on the platform being qualified. The CI fixture is disposable;
its cleanup command is not a learner-data deletion recipe. Use
[validation](../../docs/validation.md) for maintained qualification commands.

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
