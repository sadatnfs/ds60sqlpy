# k8s-008 pilot: running, ready and reachable are different

Design preview, checked 2026-10-22. This is a sample for the [planned Kubernetes track](../tracks/kubernetes.md), outside the active catalog. The journey preview can check a prediction; it cannot run a cluster lab. No cluster, image or credential is installed here. Live steps below require the future qualified `k8s-kind` profile and a host-issued owned lease. The separate [solution](kubernetes-pilot-solutions.md) stays closed until an attempt or explicit reveal.

## Level and prerequisites

Beginner, about 120 minutes plus retrieval. Direct planned prerequisite: `k8s-007`, Labels, selectors and Services, which follows the track's terminal/container, explicit-target, Pod and Deployment units. No Python or SQL background is required.

By the end, you will predict a reconciliation, distinguish Pod phase from readiness, trace a Service selector to eligible backend Pod UIDs and prove an HTTP result from inside the cluster. You will also distinguish a readiness failure from a selector failure and clean up only the owned lesson resources.

## The mental model

A Deployment states a desired number of application replicas. Its controllers create or replace Pods to reconcile observed state with that intent. Deleting one controlled Pod changes the observation, not the Deployment's replica intent.

A Pod's `Running` phase describes part of its lifecycle. It is not a promise that the application can serve traffic. A readiness probe is a repeated application check. A failure makes that Pod ineligible for ordinary Service traffic; it does not by itself request a container restart. Liveness is a separate mechanism and is deliberately absent from this pilot.

A Service uses a label selector to select candidate Pods. EndpointSlices describe their network endpoints and conditions. For this controlled fixture, eligible backend evidence means the unique `targetRef.uid` values of endpoints with `conditions.ready == true`, matched to Ready Pods. Count unique Pod UIDs across every slice/IP family, not EndpointSlice objects or raw IP-address count. The fixture must converge to explicit ready values; an unknown condition is not treated as independently verified application readiness. General consumers can interpret an unspecified readiness condition differently, so this lesson asserts the controlled controller-produced conditions rather than a universal nil-value rule.

These mechanisms are documented separately in [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/), [probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) and [EndpointSlices](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/). The examples below combine them into original teaching fixtures.

## What must be prepared before a live attempt

The host, not the browser application, must provide an owned kind cluster and a unique lesson namespace, plus a short-lived scoped worker identity. The host records control-plane identity, namespace UID, owned node identities, image digests, lease expiry and created object UIDs. Worker/admin kubeconfig files and tokens belong only in private ephemeral host-session storage or worker mounts, never `.learning`, source files, exports or progress notes.

The planned image alias `ds60-http-fixture:v1` is not a published or currently built image. It is a required future fixture. Qualification must supply and preload architecture-matched content on every schedulable node, record its digest and allow only that content. Its contract is:

- `serve --port=8080` runs as UID 65532, serves GET `/ready` with status 200/body `ready`, GET `/version` with fixed body `v1`, and 404 for unknown paths;
- `check --url=... --expect-status=200 --expect-body=ready --timeout=5s` exits0 and prints `CHECK_OK status=200 body=ready` only when the expected response arrives;
- a failed check exits2 and prints a bounded `CHECK_FAILED` diagnostic; it has no HTTP shell/upload endpoint and needs no Kubernetes token.

Until this fixture and a scoped lease actually exist, do the prediction/trace exercises using the stated contracts and label the evidence as a design exercise. Do not claim a live pass or substitute an arbitrary public image. `imagePullPolicy: Never` must fail visibly when the preload is absent. The [kind offline guide](https://kind.sigs.k8s.io/docs/user/working-offline/) explains why both node and workload preparation matter.

The worker has only this namespace's workload permissions. It cannot create namespaces or modify cluster roles. Its authentication ServiceAccount is outside the workload namespace, and workload token mounting is denied. Neither browser nor worker gets a Docker socket or host admin kubeconfig. A namespace is not a general hostile-code sandbox; this fixture holds synthetic data only.

## Manual scoped command path

This is an alternative host-terminal path after preparation, not an implemented app action. The host supplies `DS60_LESSON_KUBECONFIG`, `DS60_LESSON_CONTEXT` and `DS60_LESSON_NAMESPACE` for the scoped identity. No command below falls back to the ambient current-context. The host receipt must be checked before apply, patch or deletion; context name alone does not establish ownership.

Bash on macOS/Linux/WSL:

```bash
: "${DS60_LESSON_KUBECONFIG:?A scoped host-issued kubeconfig is required}"
: "${DS60_LESSON_CONTEXT:?An explicit lesson context is required}"
: "${DS60_LESSON_NAMESPACE:?An owned lesson namespace is required}"
K=(kubectl --kubeconfig "$DS60_LESSON_KUBECONFIG"
   --context "$DS60_LESSON_CONTEXT" --namespace "$DS60_LESSON_NAMESPACE"
   --request-timeout=10s)
"${K[@]}" auth can-i create deployments.apps
"${K[@]}" auth can-i create namespaces
```

PowerShell, in the same Windows/WSL environment that owns the prepared tools:

```powershell
foreach ($name in @('DS60_LESSON_KUBECONFIG', 'DS60_LESSON_CONTEXT', 'DS60_LESSON_NAMESPACE')) {
    if ([string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable($name))) {
        throw "Missing host-issued lesson setting: $name"
    }
}
$KubeArgs = @('--kubeconfig', $env:DS60_LESSON_KUBECONFIG,
    '--context', $env:DS60_LESSON_CONTEXT, '--namespace', $env:DS60_LESSON_NAMESPACE,
    '--request-timeout=10s')
kubectl @KubeArgs auth can-i create deployments.apps
kubectl @KubeArgs auth can-i create namespaces
```

**Expected:** the first authorization result is `yes`; namespace creation is `no` and may return nonzero. This is an intentional negative authorization check, not a reason to switch to an admin identity. For every real apply/get/wait command, check its exit status; PowerShell uses `$LASTEXITCODE`. Do not print the kubeconfig body or token. In WSL, use Linux paths and its tools; do not hand a Windows path to a Linux kubectl and assume translation.

## Worked example 1: two eligible replicas

Save this as your learner `echo.yaml`. The namespace is intentionally absent; the reviewed worker operation binds it from the private lease. The host also binds ownership labels/UID receipts, verifies the fixture image and rejects namespace escapes.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: echo
  labels:
    app: echo
spec:
  replicas: 2
  selector:
    matchLabels:
      app: echo
  template:
    metadata:
      labels:
        app: echo
    spec:
      automountServiceAccountToken: false
      securityContext:
        runAsNonRoot: true
        runAsUser: 65532
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: echo
          image: ds60-http-fixture:v1
          imagePullPolicy: Never
          args: ["serve", "--port=8080"]
          ports:
            - name: http
              containerPort: 8080
          readinessProbe:
            httpGet:
              path: /ready
              port: http
            periodSeconds: 2
            failureThreshold: 2
          resources:
            requests: {cpu: 10m, memory: 16Mi}
            limits: {cpu: 100m, memory: 64Mi}
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop: ["ALL"]
---
apiVersion: v1
kind: Service
metadata:
  name: echo
spec:
  selector:
    app: echo
  ports:
    - name: http
      port: 8080
      targetPort: http
```

Read the anatomy before applying: `spec.replicas` expresses Deployment intent; `spec.selector.matchLabels` connects its controller to the Pod template label; Service `spec.selector` selects candidate Pods. The named `http` port connects the Service target and the container's port 8080. The probe requests `/ready` on that port. A declared container port does not itself create a listening server.

Bash:

```bash
"${K[@]}" apply -f echo.yaml
"${K[@]}" rollout status deployment/echo --timeout=90s
"${K[@]}" get deployment echo -o json
"${K[@]}" get pods -l app=echo -o json
"${K[@]}" get endpointslices -l kubernetes.io/service-name=echo -o json
```

PowerShell:

```powershell
kubectl @KubeArgs apply -f echo.yaml
if ($LASTEXITCODE -ne 0) { throw 'Apply failed' }
kubectl @KubeArgs rollout status deployment/echo --timeout=90s
if ($LASTEXITCODE -ne 0) { throw 'Rollout did not converge' }
kubectl @KubeArgs get deployment echo -o json
kubectl @KubeArgs get pods -l app=echo -o json
kubectl @KubeArgs get endpointslices -l kubernetes.io/service-name=echo -o json
```

**Expected after convergence:** Deployment desired/updated/ready/available replicas are 2, observedGeneration has caught up to metadata.generation, two controlled Pods are Ready, and two unique ready EndpointSlice backend UIDs match those Pods. Pod names, IPs, resourceVersion and timing vary; no fixed values are invented. `publishNotReadyAddresses` is absent/false on the Service. This pilot targets steady state, so wait for controller propagation within the bounded observation window rather than assuming atomic updates across these resources.

Prove the application path with a client Job in the same owned namespace. Save `echo-check.yaml`:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: echo-check
  labels:
    app: echo-check
spec:
  backoffLimit: 0
  activeDeadlineSeconds: 10
  ttlSecondsAfterFinished: 180
  template:
    metadata:
      labels:
        app: echo-check
    spec:
      restartPolicy: Never
      automountServiceAccountToken: false
      securityContext:
        runAsNonRoot: true
        runAsUser: 65532
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: check
          image: ds60-http-fixture:v1
          imagePullPolicy: Never
          args: ["check", "--url=http://echo:8080/ready", "--expect-status=200",
                 "--expect-body=ready", "--timeout=5s"]
          resources:
            requests: {cpu: 10m, memory: 16Mi}
            limits: {cpu: 100m, memory: 64Mi}
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop: ["ALL"]
```

Run it only after the ownership/fixture checks. Bash:

```bash
"${K[@]}" apply -f echo-check.yaml
"${K[@]}" wait --for=condition=complete job/echo-check --timeout=30s
"${K[@]}" logs job/echo-check
```

PowerShell:

```powershell
kubectl @KubeArgs apply -f echo-check.yaml
if ($LASTEXITCODE -ne 0) { throw 'Client Job apply failed' }
kubectl @KubeArgs wait --for=condition=complete job/echo-check --timeout=30s
if ($LASTEXITCODE -ne 0) { throw 'Client verification did not complete successfully' }
kubectl @KubeArgs logs job/echo-check
```

For a deliberately negative case, do not wait for Complete as though success were expected. Inspect the bounded failed Job and its logs as the expected-failure evidence, then classify it against that exercise's contract.

**Expected:** Job succeeds and the future fixture prints `CHECK_OK status=200 body=ready`. Keep its UID/status/log receipt. A Service port-forward is useful for inspecting one process, but may bypass the ordinary Service/backend path; it is not the independent routing proof for this exercise.

## Worked example 2: running but not ready

First record Pod UIDs and restart counts. Change only the Deployment template's readiness path in `echo.yaml` from `/ready` to `/missing`, then apply the edited file. Do not use `kubectl edit` as a replacement for saving the desired-state source. The changed template may create a new ReplicaSet; identify the current-generation Pods rather than assuming old/new Pods have the same UID.

In a qualified teacher fixture, the two intended new processes can start while their readiness checks return404. Observe the rollout until the declared bounded deadline; a rollout timeout is expected for this bad configuration. Do not interpret a nonzero rollout status as an absent API object. Old ready Pods may remain during the failed rolling update, so the Service can still have old eligible backends. This is the important difference between a real rolling update and the simpler statement that two already-running Pods become unready.

To demonstrate zero eligible backends without relying on rolling-update strategy, the future host fixture also supplies a controlled `readiness-failure` case: it starts the Deployment with the bad path from an empty owned namespace, or performs a documented fixture transition that makes every selected current Pod fail readiness without keeping old replicas. Its acceptance is Running processes, Ready false and zero eligible backend UIDs. That case does not promise a container restart; no liveness probe is configured. Its in-cluster client fails within its deadline, but the exact lower-level connection-refused/timeout text can vary.

**Verify both distinctions:** for an ordinary rolling change, record old versus new ReplicaSet/Pod UIDs and which version still serves traffic; for the isolated all-unready fixture, require zero unique ready backend UIDs and a bounded failed client. Restore `/ready` and require fresh convergence plus a successful new client Job. Do not claim every readiness change immediately removes all existing Service backends.

## Exercises

### 1. Predict an all-unready fixture

Before running the controlled all-unready case, predict the Deployment/Pod/Service observations when both selected HTTP processes run but probe `/missing` returns 404. State whether a readiness failure itself should restart those containers.

**Expected:** the intended processes may be Running, Pod Ready is false, and the set of eligible ready backend UIDs is empty. EndpointSlice objects/addresses can still exist. Readiness alone is not a restart request.

**Verify:** inspect Pod conditions and restart-count baseline, flatten every Service EndpointSlice, deduplicate ready target UIDs and run a fresh bounded client. Record the controlled fixture's absence of old ready replicas; otherwise the zero-backend prediction does not apply.

Hints: (1) separate phase from readiness; (2) inspect endpoint conditions, not only addresses; (3) check whether old ready Pods still match the Service before predicting zero.

### 2. Prove a healthy baseline independently

Starting from a fresh prepared namespace, apply the healthy `echo.yaml` and client Job. Build a concise evidence table with Deployment generation/counts, Ready Pod UIDs, ready backend UIDs and the client result.

**Expected:** desired/updated/ready/available replicas are 2, the two UID sets agree and the client reports status 200/body `ready` with a successful Job.

**Verify:** observe stable convergence twice at least 2 seconds apart within a90-second lesson window, then inspect the client Job's succeeded count and log. Do not use `apply` exit 0 or a screenshot of Running Pods as the entire check. The implementation must qualify this observation budget; it is not a universal cluster performance guarantee.

Hints: (1) four observations answer four different questions; (2) compare identities, not just equal counts; (3) a successful in-cluster request closes the application-path gap left by API status alone.

### 3. Repair a selector mismatch

Keep the healthy Deployment unchanged. In the learner Service manifest only, change its selector from `app: echo` to `app: wrong`, apply and diagnose. Repair the learner source and reapply it.

**Expected:** while mismatched, the Pods can remain Ready with unchanged Pod UIDs, but the Service has zero matching eligible backend UIDs and a fresh client fails. After repair, the original ready UIDs are eligible and a new client succeeds.

**Verify:** compare the Service selector with template/Pod labels, retain before/after UID sets, and require the client result after repair. Do not change both selector and Pod labels merely to make two wrong changes agree.

Hints: (1) a Service selects labels, not an image name; (2) inspect the existing Ready Pods before changing them; (3) repair the one mismatching selector in saved source.

### 4. Observe reconciliation after one Pod disappears

From the healthy baseline, record Deployment UID and both ready Pod UIDs. Delete exactly one recorded, owned application Pod after the lease/UID check. Do not delete the Deployment, namespace or every Pod.

**Expected:** Deployment UID and desired replicas 2 remain unchanged. Eventually two ready Pods exist again, at least one has a new UID, the deleted UID is absent from eligible backends and a new client succeeds.

**Verify:** compare UID sets and the Deployment's observed generation/counts, then inspect the client Job. A transient dip is not by itself a failed reconciliation; failure to recover within the bounded fixture window is a real failed verification to investigate.

Hints: (1) find the controller's declared intent; (2) a replacement Pod has a new identity; (3) verify convergence and traffic after replacement, not just that deletion returned success.

### 5. Explain a failed rolling readiness change

Apply the `/missing` readiness template as an ordinary rolling update to the healthy Deployment, keeping the default rolling strategy. Predict first, then explain why old ready Pods may continue serving while new Pods fail readiness. Restore the saved healthy source.

**Expected:** the bad revision fails to converge; its new Pods show probe failures. Old Ready backends can remain, so zero total Service backends is not a required observation. After restore, the healthy source converges and a fresh client succeeds.

**Verify:** associate every observed Pod with its ReplicaSet/revision and readiness condition, record the nonzero rollout wait as a deliberate negative result, and verify the restored generation plus ready backend membership. Do not count successful old-version responses as acceptance of the bad new revision.

Hints: (1) a Deployment rolling update protects availability where possible; (2) split old and new Pod identities; (3) ask which revision served the response before calling the update successful.

### 6. Transfer the method and clean up safely

Design a second Service named `metrics`, intended to select a second fixture Deployment labeled `app: metrics`. Write a diagnostic plan for Running/Ready Pods with a wrong Service selector, without changing `echo`. Then finish the live pilot by cleaning up only recorded `echo`, client Job and controller-owned dependents.

**Expected:** your transfer plan names the metrics selector/Pod/EndpointSlice/client evidence separately from echo. Cleanup removes recorded lesson resources, leaves unrelated objects untouched and yields a host release receipt; learner source and nonsecret evidence remain saved.

**Verify:** before deletion match lease namespace UID and object UIDs. After deletion, the three named resources are absent, no `app=echo` controlled Pods/ReplicaSets remain, and no EndpointSlice remains owned by the deleted Service. Host cleanup revokes the RoleBinding/worker identity and checks denial; the ordinary worker never deletes namespaces or admin identities.

Hints: (1) change names and selectors in the reasoning, not the underlying evidence standard; (2) ownership is checked before deletion, not inferred afterward; (3) preserving learner work and deleting temporary infrastructure are different operations.

## Repeating a client check and final cleanup

A finished Job is immutable in relevant template fields. To repeat a check, the future broker creates a new owned attempt name. On the manual route, retain the prior receipt, verify ownership, delete only the completed `echo-check` Job and reapply the same source. Do not silently discard failed evidence or retry a side-effecting workload.

After verifying ownership, Bash cleanup for the fixed names is:

```bash
"${K[@]}" delete deployment/echo service/echo job/echo-check --ignore-not-found=true --wait=true --timeout=30s
"${K[@]}" get deployment/echo service/echo job/echo-check --ignore-not-found -o name
"${K[@]}" get pods,replicasets -l app=echo -o name
"${K[@]}" get pods -l batch.kubernetes.io/job-name=echo-check -o name
"${K[@]}" get endpointslices -l kubernetes.io/service-name=echo -o name
```

PowerShell:

```powershell
kubectl @KubeArgs delete deployment/echo service/echo job/echo-check --ignore-not-found=true --wait=true --timeout=30s
if ($LASTEXITCODE -ne 0) { throw 'Owned cleanup did not finish' }
kubectl @KubeArgs get deployment/echo service/echo job/echo-check --ignore-not-found -o name
kubectl @KubeArgs get pods,replicasets -l app=echo -o name
kubectl @KubeArgs get pods -l batch.kubernetes.io/job-name=echo-check -o name
kubectl @KubeArgs get endpointslices -l kubernetes.io/service-name=echo -o name
```

**Expected:** no remaining owned workload/backend names. If a namespace or object UID no longer matches, stop the operation instead of forcing deletion. Host release of a verified owned namespace is a separate operation, and credential files remain outside portable progress throughout.

## Diagnosis and retrieval

| Observation | Useful next evidence | Avoid this false conclusion |
| --- | --- | --- |
| `ErrImageNeverPull` | Qualified node-image inventory and exact allowed fixture digest | The app should download any image from Run |
| Running but not Ready | Probe path/result and current revision | Running proves the application is serving |
| Ready Pods but zero eligible backends | Service selector, Pod labels and EndpointSlice target UIDs | Rebuilding the image is necessarily the fix |
| New revision unready, old traffic still good | ReplicaSet ownership and serving version | The new rollout succeeded |
| Unauthorized/Forbidden | Lease expiry versus the exact denied action | Switch to a host-admin kubeconfig |

Close the manifests and explain: which controller replaces a deleted Pod, which field selects candidate backends, which observation proves HTTP behavior, why a rolling update can retain old backends, and why cleanup needs identity checks. Repeat the explanation for metrics with different names. Never paste credentials or raw Secret data into a teacher prompt.

## Rubric and evidence boundary

Score 0,1 or 2 for prediction; explicit target/ownership; desired-state/backend/client evidence; fault diagnosis; and scoped cleanup/transfer. Readiness for the next lesson needs at least 8/10, every applicable live check passing, no ambient/admin target use and an explanation that distinguishes an all-unready fixture from a rolling update. If only transcripts were studied, record a reasoning result, not live runtime acceptance. The owned kind profile, HTTP/client image, broker, token lifecycle and OS/architecture matrix are all pending implementation/qualification here. No actual Kubernetes command is claimed executed by this design.

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning to coach planned k8s-008, Running, ready and reachable are different.
Read docs/expansion/samples/kubernetes-pilot.md; its echo.yaml and echo-check.yaml blocks are the learner artifacts.
This is an unregistered design preview. Do not claim a runnable cluster profile or use the ambient kubectl context.
Direct planned prerequisite is k8s-007. Explain one concept, ask my prediction, let me attempt, then give one hint at a time.
Do not read docs/expansion/samples/kubernetes-pilot-solutions.md or solutions/ content until I ask or make an honest attempt.
Ask for redacted Deployment/Pod/backend/client observations and ownership receipts, never tokens or kubeconfig bodies.
Distinguish all-unready state from a failed rolling update with old ready replicas. Keep cleanup within the host-owned lease.
Finish with the metrics transfer task and retrieval in my own words, with any unavailable live checks clearly marked pending.
```
