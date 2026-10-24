# Kubernetes: browser Runs, evidence worksheets and owned host labs

The course teaches Kubernetes from object anatomy through controlled platform changes. Each lesson says which activity the app can actually execute. A source manifest describes intent. An API response establishes acceptance and identity. Controller status describes reconciliation. A client response or data checksum establishes an application result. Cleanup has its own receipt. Keep these evidence levels separate when recording progress.

## Prepare immediately before the lab

Build or download the explicitly approved images and tools before preparing the private Kubernetes session. The current lease lasts fifteen minutes, so prepare immediately before starting the broker and running the bounded cases. If it expires before Run, the readiness guard should refuse it. Preserve learner source, stop the expired broker, release only the exact owned session through the host helper, and prepare a fresh session. Do not bypass expiry with ambient credentials or change the runtime to ignore the cleanup reserve. See the [owned preparation guide](../../docker/kubernetes/README.md).

## The current bounded browser operation

The prepared `k8s-kind` worker accepts one fixed hello Deployment, an optional hello Service, and an optional hello-config ConfigMap. Alternatively it accepts one standalone hello-task Job. It uses the approved image `ds60sqlpy-k8s-fixture:0.2.0`, preloaded by the host, and `imagePullPolicy: Never`. It does not pull an image during Run. Read the actual current qualification receipt before claiming a platform works; source and unit tests alone do not establish it.

The ConfigMap has one synthetic message, either hello or reviewer. Its admitted consumers are a fixed environment reference and a read-only `/config/message` projection. The fixed server exposes `/message` from its environment and `/file-message` from the current file contents. Startup delay is zero or three seconds. Readiness, startup and liveness probes use the fixed local paths and bounded thresholds described by each source.

The finite Job has one completion and one parallel Pod, at most one retry and a 5-30 second active deadline. The only learner-selected task outcomes are a fixed success or an injected failure. Success prints an exact synthetic ledger with three accepted rows, two rejected rows and total 35. The controller verifies Job and Pod ownership, container exit status and bounded output. It never accepts an arbitrary Python command, shell fragment, remote URL or image.

Every browser operation uses a private lease that names one owned cluster and namespace identity. It creates only fixed resources, waits within a deadline and cleans its recorded UIDs using owner and per-Run nonce checks. A lost create response is reconciled only if the object proves the same nonce. A same-name replacement is preserved. The private cluster lease remains until the host's explicit release operation.

Because a Run cleans up afterward, it is not a persistent interactive cluster session. Reapplying a new pad starts another one-shot operation, not a rolling update of the previous Run's object. Lessons about Pod deletion, live ConfigMap updates, revisions or state recovery explicitly identify their separate host-lab steps. A one-shot success cannot serve as evidence for those stateful transitions.

## What the prepared worker does not provide

| Activity | Required separate capability |
| --- | --- |
| Pod deletion or live update of an existing workload | A stateful owned operation with recorded before/after UIDs and field ownership |
| Secret inspection or synthetic Secret mounts | A dedicated teacher-provided synthetic fixture and scoped access, absent from the normal worker |
| NetworkPolicy enforcement | A policy-capable CNI plus measured allowed/denied traffic paths |
| PVC/StatefulSet persistence | A qualified StorageClass and an explicit retention/reclaim policy |
| Gateway/Ingress/TLS | Preinstalled controller, Gateway/route permissions, loopback listener and verified synthetic trust material |
| CRD/operator/admission policy | Host-provisioned reviewed cluster-scoped definitions and namespaced exercise instances |
| Node drain, disruption or autoscaling | Exclusive qualified node/metrics topology and bounded host operations |
| Control-plane snapshots or replacement clusters | Separate owned cluster receipts and distinct application-data backup evidence |
| Helm/Kustomize rendering | Already prepared pinned local tools and vendored inputs, with no downloads during a lesson |

These chapters remain complete reading and host-lab guides when their extra capability is absent. Their synthetic manifests and traces let you reason through the mechanism offline. Label those results synthetic, and leave the live acceptance row unavailable instead of inventing a success transcript.

## Start from an owned receipt

Use the [preparation guide](../../docker/kubernetes/README.md) and [runtime walkthrough](../../docs/modules-runtime.md#prepare-and-run-the-owned-kubernetes-lab). The host receipt identifies the cluster, namespace, namespace UID, owner nonce, expiry and approved capabilities. Credentials remain in the private runtime directory, outside learner progress, exports and source control. Never paste a token or kubeconfig content into a pad, screenshot or report.

A namespace name is not enough: names can be deleted and reused. Compare the recorded namespace UID and ownership marker with a fresh readback before a mutation. The same rule applies to cleanup of objects. A failed identity check means the intended target has not been established; do not fall back to current-context or a default namespace.

The ordinary worker Role has only its reviewed namespaced resource actions and readback. It cannot read Secrets, execute inside Pods, create arbitrary roles, install a controller, patch Nodes or create namespaces. A denied operation is sometimes the expected evidence of least privilege, not a reason to broaden credentials.

## Read-only host observations with explicit targeting

The following examples assume an already provisioned capability and environment variables copied from its nonsecret path/context/namespace fields. They do not create a cluster or discover an ambient target. Run from the repository root. Substitute the exact lesson resource in later commands only when the chapter names it and the receipt permits it.

POSIX shell:

```sh
: "${LAB_KUBECONFIG:?Use the private path from the owned receipt}"
: "${LAB_CONTEXT:?Use the exact context from the owned receipt}"
: "${LAB_NAMESPACE:?Use the exact namespace from the owned receipt}"
kubectl --kubeconfig "$LAB_KUBECONFIG" --context "$LAB_CONTEXT" --namespace "$LAB_NAMESPACE" get deployment hello -o json
```

PowerShell:

```powershell
if (-not $env:LAB_KUBECONFIG -or -not $env:LAB_CONTEXT -or -not $env:LAB_NAMESPACE) {
    throw 'Use the private path, context and namespace from the owned receipt.'
}
& kubectl --kubeconfig $env:LAB_KUBECONFIG --context $env:LAB_CONTEXT --namespace $env:LAB_NAMESPACE get deployment hello -o json
if ($LASTEXITCODE -ne 0) { throw 'The explicit owned-target read failed.' }
```

Keep the explicit arguments on every call. The examples intentionally fail when a targeting variable is absent. Do not use `kubectl config use-context`, overwrite a default kubeconfig or select a production/shared context to make a lesson work.

For a readback, retain only relevant nonsecret fields: name, namespace, UID, owner references, generation, observedGeneration, conditions and bounded diagnostic excerpts. Events and logs can contain application data, so inspect synthetic fixtures and avoid copying real credentials or unrelated tenant information. A log line describes a process event; it does not replace an API identity or client correctness check.

## Apply and cleanup are separate controlled operations

Browser-source YAML omits namespace because the reviewed operation binds it from the lease. Host-lab JSON examples also avoid pretending that a hard-coded namespace is your actual target. A host capability must bind the target, inject ownership markers, record returned UIDs and enforce its resource allowlist before applying them. A static JSON `List` is an inspectable manifest collection, not authorization to apply every listed resource to any cluster.

Do not substitute a broad `kubectl apply -f` or `delete namespace` for a missing capability. For advanced host practice, the teacher/operator prepares the reviewed resource set in an exclusive disposable scope and supplies the exact operation and cleanup contract. Cluster-scoped prerequisites such as a CRD or controller belong to that host preparation, not the learner's namespaced credentials.

Cleanup compares namespace identity, object name, owner marker, Run nonce and UID. The API deletion includes a UID precondition so a same-name replacement cannot be removed between read and delete. The worker reserves fresh cleanup time after work timeout or cancellation. If cleanup cannot be established, retain the private recovery receipt and report the remaining resource identity; do not erase unrelated objects or prune the engine.

Stateful lessons also need a data-retention decision. Deleting a Pod, PVC, PV and underlying storage are different actions. A reclaim policy is not a backup. Record whether synthetic data should survive the exercise and verify a checksum after any recovery before declaring it successful.

## Make a useful evidence packet

For each exercise record the expected mechanism, exact input or source change, target receipt identity without credentials, observed object UIDs/conditions, application or data result, and cleanup outcome. Include a negative case that distinguishes the intended mechanism from a plausible shortcut. For example, a Running Pod can be unready; a Service can exist without eligible backends; a Job count can be inconsistent with an unrelated Pod; and a Ready restored application can still contain the wrong data.

The offline `*_checks.py` programs use only authored synthetic data and standard-library calculations. They make no Kubernetes API calls. Their passing result proves that the teaching calculation matches its fixture, not that a controller, CNI, storage driver or host platform was exercised. The learner worksheet preserves predictions and explanations separately from official solution files.
