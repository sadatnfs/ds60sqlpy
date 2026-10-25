# Observe a synthetic Secret through three lifetimes

This teacher-operated fixture belongs to `k8s-019`. It gives a real consuming
application to the lesson's environment, projected-file and reload explanation.
It accepts exactly two public byte strings, `DUMMY_LESSON_ONLY` and
`DUMMY_LESSON_ROTATED`. They are teaching markers, not credentials. Never replace
these strings with a password, API token or real Secret value.

The normal browser worker continues to reject Secrets, Secret references and
this program override. A teacher must separately prepare an exclusive local
course session and authorize this fixed observation. The teacher runner uses
the preparation's private administrator context because the ordinary worker
Role deliberately lacks these operations. It does not change that Role, launch
a cluster, select an ambient context, execute commands inside Pods or download
an image. The caller needs the repository's prepared Python environment, pinned
kubectl, existing fixture image and an already prepared owned session.

## Follow one value through the system

The API object's desired value is only the first stage. On container startup,
Kubernetes supplies `SYNTHETIC_MARKER` through `env[].valueFrom.secretKeyRef`.
The operating system gives the process that environment. The Python application
captures its label once in `Observation.__init__`. A later API update does not
rewrite the environment of the running process.

The same Secret key is mounted as `/synthetic/message`. The manifest mounts the
whole Secret volume read-only, with an `items` entry selecting one key and
renaming it to `message`. There is no `subPath`. The application opens that path
again on each observation, so it can see a newer projected file after Kubernetes
refreshes the volume. Holding an old file descriptor or using `subPath` would
change this experiment. Kubernetes propagates Secret volume updates eventually;
an accepted patch does not establish that the file has already changed.

The application also keeps a separate `cached` label in memory. It initializes
this once from the projected file and changes it only when the fixed `POST
/reload` endpoint succeeds. Thus file freshness and application use can disagree
without either observation being fabricated. Reload reads the file once and
returns the label it actually adopted. A lock serializes observations and reloads
within this process; it does not make a transaction with the Kubernetes API.

The label `initial` stands for the first public marker and `rotated` for the
second. `pod_uid` is supplied by the downward API. `boot_id` is a newly generated
process identifier. The teacher crosschecks the Pod UID against API readback
and the controller owner graph; merely receiving a UID in an HTTP body would
not prove ownership.

| Observation stage | Environment | Projected file | Application cache | Identity expectation |
| --- | --- | --- | --- | --- |
| Initial ready process | initial | initial | initial | First Pod UID and boot ID |
| Secret patch accepted | initial | initial or rotated | initial | Same process; projection timing unobserved |
| File refresh observed | initial | rotated | initial | Same Pod UID and boot ID |
| Explicit reload completed | initial | rotated | rotated | Same Pod UID and boot ID |
| Replacement Pod ready | rotated | rotated | rotated | New Pod UID and new boot ID |

This table is a prediction until the teacher obtains an actual evidence record.
A container restart could change the boot ID while keeping the Pod UID. This
runner deliberately replaces one recorded Pod, allowing the Deployment's
ReplicaSet to create a new Pod, so both identities must change. It does not
claim to test a rollout, every restart cause or simultaneous API updates.

## Read the concrete manifest

`render.py` embeds the exact `app.py` text into the fixed ConfigMap and produces
`manifest.json` and `rotate.json` without contacting any API. The three objects
are Secret `synthetic-message`, ConfigMap `synthetic-secret-observer-program`
and Deployment `synthetic-secret-observer`. There is one replica and no Service,
Ingress, persistent storage or host mount. Before creating anything, the runner
refuses existing objects under any of these names. It adds the explicit owned
namespace and fresh run nonce itself.

The Pod uses `ds60sqlpy-k8s-fixture:0.2.0` with `imagePullPolicy: Never`. Its
command is the fixed Python observer mounted at `/lesson/app.py`. It runs as
UID/GID 65532, with `fsGroup: 65532` so the group-readable Secret projection can
be read. JSON's `defaultMode: 288` is decimal for octal 0440: owner and group may
read, neither may write, and other users have no permissions from these mode
bits. File permissions are separate from API authorization or encryption at
rest. A mode declaration does not prove either of those controls.

The Pod has a read-only root filesystem, drops all capabilities, disallows
privilege escalation, uses RuntimeDefault seccomp, and does not mount a service
account token. It requests 25m CPU/32Mi memory and is limited to 100m/96Mi. A
readiness probe calls `/ready`, which validates the marker without mutating the
cache. The one-second termination grace bounds this teaching process's shutdown;
it is not advice for an application that needs time to flush durable work.

The observer exposes only `GET /ready`, `GET /observe` and `POST /reload`.
Responses contain the five identity/label fields, never marker bytes. Unknown
paths return a fixed error. Reload rejects bodies, duplicate Content-Length
headers and every Transfer-Encoding header. The file reader accepts only the
exact two byte sequences, with no newline normalization, and bounds its read.
An unknown or missing marker yields a generic 503 without revealing bytes or
paths. Routine HTTP logging is disabled. This small server demonstrates a
lifecycle mechanism; it is not a general authenticated secret-management service.

## Regenerate and inspect offline

From the repository root, use the [prepared contributor environment](../../../../CONTRIBUTING.md)
in Bash on Linux, macOS or Windows WSL 2:

```sh
uv run --no-sync python courses/kubernetes/fixtures/secret-observer/render.py
uv run --no-sync python -m pytest tests/test_kubernetes_secret_observer.py
```

The tests use fresh temporary files, a loopback HTTP server and fake API
responses. They establish program and ownership logic, not kubelet projection
or actual Kubernetes cleanup. The lesson's small encoding check remains useful
as a separate offline exercise and also makes no cluster request.

## Run only against a fresh teacher-owned session

Prepare the owned session immediately before the lesson using the explicit
preparation workflow in [host-labs.md](../../host-labs.md). The usual worker
credential expires after about 15 minutes. This runner requires at least seven
minutes remaining, even though it uses the matching teacher context, so an old
session cannot silently become an indefinite administrator route. A released
session cannot be reused. Keep its private files outside learner progress and
exports, and never print the kubeconfig, token or private key.

The teacher supplies the absolute session directory from the new preparation
receipt and the absolute pinned kubectl path. The runner derives the explicit
teacher context, namespace and expected namespace UID from the matching private
receipt and lease. It checks the kubeconfig has one fixed context, the exact
loopback server and cluster CA, and embedded certificate credentials only.
It rejects credential plugins and ambient kubeconfig selection. Use a new output
directory whose parent already exists. These commands neither prepare nor
release a cluster:

Bash on Linux/macOS or Windows WSL 2:

```sh
: "${LAB_SESSION:?Set the fresh private session directory from preparation}"
: "${LAB_KUBECTL:?Set the pinned kubectl executable path}"
: "${LAB_EVIDENCE:?Set a new evidence directory beneath an existing parent}"
uv run --no-sync python courses/kubernetes/fixtures/secret-observer/teacher.py \
  --session "$LAB_SESSION" --kubectl "$LAB_KUBECTL" \
  --output "$LAB_EVIDENCE" --confirm-synthetic-secret
```

Argument paths are separate tokens, so paths containing spaces work. The runner
uses no shell interpolation or default context. Do not paste an example session
from a previous teacher's notes. Do not replace a denial with another identity.
The observation is limited to the prepared owned namespace; the wrapper's fixed
operations do not reduce the underlying administrator credential's authority,
so keep that file private and under teacher control.

The runner first checks the namespace UID and ownership label, then refuses
preexisting fixture names. It records creation intent and returned object UIDs.
The Deployment, ReplicaSet and Pod must have the expected owner chain and fresh
nonce. One port-forward targets that exact Pod and binds only 127.0.0.1 on an
OS-assigned port. There is no arbitrary Pod selector or exec command.

Rotation uses a JSON Patch with tests for the Secret UID and resourceVersion
before changing the public marker. A changed identity or concurrent edit fails
instead of overwriting someone else's state. The runner polls the real file
label for at most 150 seconds. It does not sleep a fixed duration and assume an
update happened. It requires the environment and cache to remain initial during
that observation, invokes reload, then stops its port-forward and deletes only
the recorded Pod UID. A replacement Pod must belong to the same owned
Deployment. Its environment, file and initial cache must all be rotated.

## Interpret evidence and failure

The new directory contains `evidence.json` with source hashes, namespace and
object identities, observed image IDs, four label snapshots, elapsed projection
time and cleanup status. API resourceVersion strings establish that the source
was observed at two versions; they are opaque and are not seconds or a global
sequence to subtract. A measured projection delay is one observation, not an
upper bound for other clusters. The program does not prove encryption at rest,
real-secret confidentiality, network-policy isolation or production readiness.

A startup failure can mean missing image, key, mode/group access or application
validation. Distinguish Deployment progress, Pod events and readiness before
assuming a networking fault. A 150-second projection timeout is a failed or
inconclusive observation in this environment. Inspect the explicit owned Pod
and kubelet setup through the teacher workflow; do not lengthen waits forever
or broaden normal worker privileges. If the boot ID changes during the wait,
the test refuses to mix observations from different processes.

A nonzero exit is never a pass. Read both `observation_passed` and
`cleanup_confirmed`. A successful observation with failed cleanup still exits 2.
The runner suppresses raw kubectl error bodies because those can echo submitted
fields. Its value-free failure type is a lead for private diagnosis, not a claim
that the exact root cause was established.

## Cleanup is an independent result

The runner closes its own port-forward in a `finally` block. It rechecks the
namespace and object ownership before cleanup and issues Kubernetes
DeleteOptions with `preconditions.uid`, foreground propagation and a bounded
grace period. It removes the recorded Deployment, ConfigMap and Secret, then
checks their absence and the absence of its nonce-labeled Pods/ReplicaSets.
It never issues a broad namespace delete or deletes a same-name replacement.
SIGINT/SIGTERM trigger the same bounded cleanup path; a second such signal is
ignored during cleanup. A process kill or machine crash can prevent this path.

If creation may have succeeded but its UID could not be recorded, cleanup
refuses that ambiguous object and retains the intent/nonce for teacher review.
Do not delete by name alone to make the receipt green. The separate owned-session
release operation validates the recorded control-plane identity and exact local
engine endpoint before removing that exclusive course cluster. Stop the owned
classroom lab and worker before releasing their session, following the
[owned Kubernetes runbook](../../../../docs/modules-runtime.md#prepare-and-run-the-owned-kubernetes-lab). Use the exact preparation receipt's session:

Bash on Linux/macOS or Windows WSL 2:

```sh
uv run --no-sync python scripts/prepare_kubernetes.py release \
  --session "$LAB_SESSION" --confirm-release
```

Release is separate from this fixture's object cleanup. Retain both receipts.
After expiry, release that exact owned session and prepare a new one; never edit
expiry timestamps or reuse its credentials. Do not remove learner pads,
progress, unrelated containers or another teacher's objects.

## References

- [Kubernetes Secret volume updates and subPath behavior](https://kubernetes.io/docs/concepts/configuration/secret/#using-secrets-as-files-from-a-pod)
- [Secret-backed environment variables and updates](https://kubernetes.io/docs/tasks/inject-data-application/distribute-credentials-secure/#define-container-environment-variables-using-secret-data)
- [Deployment ownership and replacement](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
