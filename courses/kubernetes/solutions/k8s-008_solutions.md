# k8s-008 explanatory solutions

Authored beta reference, checked 2026-10-22. These answers correspond to the six tasks in the [learner pilot](../guides/k8s-008.md). They describe the required evidence on an explicitly prepared owned fixture. The bounded one-shot app verifier has a Linux aarch64 positive qualification; these explanatory answers do not claim that every manual exercise has run on a learner system. Keep this page separate from the initial attempt. No answer requires or reveals an admin credential.

## Exercises

### Exercise 1: Predict the controlled all-unready state

The Deployment intent can still request two replicas and the two application processes can be Running, while both Pod Ready conditions are false. With the Service's `publishNotReadyAddresses` absent/false, the set of ordinary eligible ready backends is empty. EndpointSlice objects and even address entries may still exist with false readiness conditions.

A readiness failure does not itself restart a container. The restart count should remain at its controlled-fixture baseline unless another independent cause occurs. A changed Pod UID, OOM event or liveness failure would need a separate explanation. Count unique ready `targetRef.uid` values across all slices, because dual-stack endpoints can repeat the same Pod identity.

**Expected:** no eligible ready backend UID, a bounded failed in-cluster client and Ready false for the intended selected Pods. The premise includes no old Ready replicas.

**Verify:** compare intended/current Pods and restart baselines, inspect the probe failure and explicitly rule out an old ready ReplicaSet before requiring zero backends. If old ready Pods remain during a rolling change, the premise is false; the answer for Exercise5 applies instead.

### Exercise 2: Prove the healthy baseline

The evidence table should contain these independent observations:

| Layer | Expected controlled-fixture evidence |
| --- | --- |
| Desired and observed controller state | replicas 2, updated/ready/available2, observedGeneration at least metadata.generation |
| Application Pods | Two controlled Ready Pod UIDs; phase alone is not the check |
| Service membership | Selector `app: hello`; the same two unique Pod UIDs have explicit ready endpoints |
| Application path | New client Job succeeds and prints `client exits0 with exact trimmed /version body ds60-fixture-v1` |

A success from apply only means the API accepted the requested object. A Deployment status says something about controller observation. Endpoint membership says something about traffic eligibility. The client adds an actual DNS/Service/application observation. None alone proves all four layers.

**Expected:** stable observations twice at least 2 seconds apart inside the qualified observation budget, then a successful client. IPs and Pod names are not hardcoded.

**Verify:** compare UID sets, not only counts; retain the current generation and client attempt UID/log. A successful port-forward can reach one selected process directly and is not the Service-routing evidence required by this task. If the future fixture cannot meet its published budget, report a failed/unqualified run rather than extending an unlimited wait.

### Exercise 3: Repair only the mismatching selector

The Service's wrong selector requests Pods labeled `app: wrong`. The healthy Deployment still produces `app: hello` Pods, so those Ready Pods do not match. The controlled Service has zero eligible backends and a fresh client fails.

The repair is the original Service selector in the learner's saved manifest:

```yaml
spec:
  selector:
    app: hello
```

Apply that saved correction through the scoped target. No Deployment change is needed, and no image rebuild follows from this evidence.

**Expected:** the same healthy Pod UIDs become eligible backends after controller propagation, then a new client succeeds. During the mismatch the Pods themselves can stay Ready.

**Verify:** retain selector/label evidence and before/after backend UID sets. A solution that also changes Pod labels conceals the actual fault and may trigger a needless rollout. Matching labels are necessary for selection; the HTTP/probe results still establish the different application-health conditions.

### Exercise 4: Reconciliation replaces a missing Pod

Record the owning Deployment UID and the two current Ready Pod UIDs. Delete exactly one verified owned Pod. The Deployment intent still requests two replicas, so the controller eventually creates a replacement through its ReplicaSet.

**Expected:** Deployment UID/desired count stay the same, the deleted UID disappears, at least one replacement UID appears, two ready backends return and a fresh client succeeds. The replacement name/IP may differ and the observation need not be instantaneous.

**Verify:** compare UID sets and owner references, then require controller convergence plus HTTP success. Deletion exit 0 is not a replacement check. If the new Pod fails image, resource, scheduling or probe checks, those observations explain a genuine failure to converge; do not delete the namespace to hide the evidence.

A short availability dip does not contradict eventual reconciliation. Conversely, the existence of a controller is not a promise that every impossible desired state will become healthy.

### Exercise 5: A failed rolling readiness change can retain old backends

Changing `/ready` to `/missing` in the Pod template creates a new Deployment revision. Under the normal rolling strategy, the controller can retain old Ready replicas while new replicas fail readiness. Therefore a client may continue receiving a successful old-version response even though the new revision never becomes available.

The useful evidence separates three groups: old controlled Ready Pods, new controlled unready Pods, and the Service's eligible backend UID set. Associate Pods with ReplicaSet/revision metadata. A rollout wait returning nonzero at its deadline is the expected negative result for the deliberately bad revision.

The repair is the saved healthy probe path:

```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: http
  periodSeconds: 2
  failureThreshold: 2
```

**Expected:** the repaired desired state converges, its intended revision becomes available and a fresh client succeeds. Old successful traffic alone is not evidence that the broken new revision passed.

**Verify:** inspect observed generation and updated/ready/available counts together with revision-specific UID membership and response evidence. Do not require zero Service backends for every rolling readiness failure. The all-unready exercise is a separate controlled fixture, not a description of every rollout strategy.

### Exercise 6: Transfer the diagnosis and clean up the owned resources

For metrics, inspect that Service's selector and the second Deployment's `app: metrics` Pod labels. Then compare only metrics Ready Pod UIDs with that Service's ready EndpointSlice target UIDs and run a metrics client against its declared port/path. Echo's health does not prove metrics routing, and there is no reason to edit hello merely because the second Service is wrong.

The cleanup proof has a different purpose from diagnosis. Before deletion, compare the current namespace UID, resource UIDs and lease ownership markers with the host receipt. Delete only the recorded hello Deployment, Service and client Job. Controller-owned Pods, ReplicaSets and EndpointSlices should then disappear through their ownership lifecycle.

**Expected:** fixed lesson resources and owned dependents are absent, unrelated resources remain, saved learner manifests/evidence remain, and the host provides a release/revocation receipt. The ordinary worker does not delete namespaces, edit cluster roles or remove the host authentication identity itself.

**Verify:** query the named resources, `app=hello` workload dependents and slices labeled for the deleted Service. A same-name resource with a different UID is an ambiguity to refuse, not permission to delete it. Host release checks that its disposable namespace still has the expected identity, then revokes RoleBinding permissions/deletes its private worker ServiceAccount and confirms access denial. Short token lifetime and permission revocation are related but different controls; never assume an issued JWT can be individually revoked just by deleting a local file.

## A concise evidence record

A learner record can contain fixture image digest, lease identifier/expiry, namespace UID, source hash, desired/observed generation/counts, Ready Pod UID set, eligible backend UID set, client attempt status/body contract, observed fault/recovery and cleanup receipt. It must omit the worker kubeconfig, bearer token, admin certificates, raw Secret values and private snapshots. A cluster identity/namespace receipt is not a credential.

The proposed fixture aliases, budgets and client log strings are qualification contracts. They are not a transcript from a cluster created during this design phase. If live infrastructure is absent, a careful explanation can earn reasoning feedback while runtime acceptance remains pending.

## Rubric and retrieval

Use the learner's ten-point rubric with at least 8/10, every applicable live check, explicit owned targeting and a correct distinction between all-unready state and a failed rolling revision. A copied healthy manifest with no explanation is not mastery. Ask the learner to explain a different Service name, a different selected label and one independent competing failure cause without opening this solution.

Primary references are the [Deployment controller](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/), [probe behavior](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/), [EndpointSlice conditions](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/) and [RBAC good practices](https://kubernetes.io/docs/concepts/security/rbac-good-practices/), checked 2026-10-22. No production availability, security isolation or native OS qualification follows from this sample alone.

The [complete healthy YAML reference](k8s-008_solution.yaml) uses only the approved local fixture image. The [client Job](../fixtures/hello-check.yaml) checks /version while readiness probes check /ready. Root host/cluster preparation and actual runtime receipts remain separate from these authored files.
