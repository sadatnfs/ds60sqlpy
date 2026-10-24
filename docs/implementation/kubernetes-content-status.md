# Kubernetes content and runtime status

> Support boundary: this file retains historical implementation evidence. The
> supported product runs in Linux Docker containers, with Windows through WSL 2.
> Native Windows ACLs/backends and native executable builds are not supported
> targets or release gates. Current checks are defined in [validation](../validation.md).

Updated2026-10-23. All42 planned IDs k8s-001 through k8s-042 have authored bodies in canonical courses/kubernetes/lessons.json. Direct prerequisites match docs/expansion/plans/kubernetes.json. The four original pilots remain,with current fixture and prerequisite notes. The38 added lessons have two worked cases,six distinct exercises,learner artifacts,separate manifest/explanatory solutions,case ledgers and executable offline reasoning checks. Current totals are 64,703 guide words and 25,050 explanatory-solution words.

## Content and capability boundary

There are 12 bounded YAML sources and 30 reading worksheets. A YAML source executes only the fixed Deployment,optional Service/ConfigMap or standalone finite task contract. A one-shot run cleans its objects,so live updates,Pod replacement and rollout history remain separate stateful host activities. Reading lessons include real Kubernetes manifests and concrete observations but do not pretend the ordinary worker can apply arbitrary resources.

Advanced host requirements remain explicit: general Secret access beyond the fixed teacher observer below;policy-capable CNI;StorageClass/PVC/StatefulSet and finite marker Jobs;Gateway/Ingress/TLS controller;CRD/operator/admission definitions;exclusive Node maintenance;metrics/load/HPA;traffic editing;conditional updates/watches;control-plane/data backup;replacement stacks;and integrated release/recovery. These capabilities were not qualified by the contract-2 runtime run. Do not install controllers,widen credentials or select an ambient cluster from a learner artifact.

The host-lab guide explains explicit POSIX/WSL targeting and the15-minute lease workflow. Prepare immediately before broker startup and Run,after tool/image preparation. An expired lease is refused;stop the broker,release only the exact owned session and prepare a fresh lease. Saved learner source is preserved. Old fixture0.1 pads receive an actionable version refusal until their owner deliberately reviews and changes the image field.

## Local evidence

The dedicated content suite exercises all38 offline references with socket access denied,validates42 planned IDs and separate artifacts,checks real host manifests against the browser refusal boundary,and proves the storage writer refuses overwrite while the independent reader rejects wrong data. Both dev/test Kustomize overlays were actually rendered using the already prepared kubectl-v1.37.0 without API access and matched their expected JSON. Helm inputs are vendored and schema-bounded;Helm is absent on this host,so its actual renderer is not qualified.

The provenance fixture contains an actual RSA/SHA256 signature over a synthetic attestation. The authoring and regression controls accepted the original and rejected the tampered copy with an existing OpenSSL-compatible verifier. Only public material is stored. This does not establish OCI image publisher provenance,Sigstore identity or cluster signature enforcement.

Final focused completion and runtime regression run: **186 passed in3.91seconds**. After portable regeneration and prose normalization, the content/system subset passed **99 tests in3.56seconds**. Portable regeneration produced zero changed lesson/fixture artifacts. Ruff passed for all four owned content/runtime test files. The earlier missing-status-link failure was resolved by this completed record. Runtime adapter/fixture tests previously passed104 checks with strict MyPy on the three implementation files. No Docker engine or cluster mutations were performed by the content author.

## Actual contract-2 runtime evidence supplied by integration owner

The integration owner built the new images,prepared a fresh owned Linux aarch64 lease and ran12 expected-outcome cases. The receipt is work/kubernetes-v2-acceptance.json:owned service readiness,Deployment-only foundation,unready timeout,wrong-selector timeout,namespace refusal,privileged refusal,cancellation,ConfigMap environment+file,finite task success,injected task failure,startup probe and configured cancellation. These are actual operation receipts,not synthetic lesson traces.

work/kubernetes-v2-classroom-api.json records a configured workload succeeding through /api/modules in14.493seconds,including controller/Pod/EndpointSlice identity,version response,environment/file messages and owned cleanup. work/kubernetes-v2-shutdown.json records SIGTERM during an active unready operation:five owned resources before,zero remaining,worker exit0,in5.078seconds. The exact owned cluster was released and broker stopped;work/kubernetes-v2-release.log and work/kubernetes-v2-final-proof.log record that lifecycle closure. The owner reported no remaining kind nodes.

An earlier lease expired before broker qualification. The readiness guard correctly refused it,and the owner released that exact session before the successful fresh run. That operational retry is why the beginner guidance emphasizes preparation timing. This Linux aarch64 evidence does not qualify every OS/architecture or any of the advanced capabilities listed above.

## Reproducible authoring and remaining work

courses/kubernetes/authoring/complete/build_all.py regenerates only the38 added IDs and merges them into canonical lessons.json,preserving001,002,003,008. Explicit batch inputs retain the topic-specific text,examples and solutions;enhance.py adds scoped observation commands and storage marker manifests. The immutable signature public fixture is deliberately not regenerated. No parallel lesson inventory remains.

The integration owner handles generated catalog/readers,dashboard registration and broad acceptance. Kubernetes content and bounded runtime contracts can be frozen after the focused final tests. The systems author next owes a substantive C++ guide depth pass,including complete copy-runnable examples and topic-specific debugging. Scala/Spark remaining38 lessons remain queued with the integration owner.

## Synthetic Secret consumer, 23 October 2026

`k8s-019` now includes the durable `fixtures/secret-observer/` application,
renderer, full Secret/ConfigMap/Deployment manifest, teacher runner and detailed
README. The guide authoring input and executable JSON solution reference the
real consumer; `build_all.py` regenerates the fixture before the chapter.
The chapter remains a reading/teacher-lab capability. The ordinary browser
manifest allowlist, worker Role and fixture image are unchanged.

Offline checks cover exact public marker bytes, bounded reads, environment/file/
cache lifetimes, coherent single-read reload, label-only HTTP errors, no-body
request framing, fixed manifest security, normal-worker refusal, explicit
context/CA/namespace binding, preexisting-name preservation, accepted-create
response timeout recovery, controller ownership, replacement preservation,
UID/resourceVersion patch tests, and SIGINT/SIGTERM cleanup dispatch. The final
focused run includes 20 new observer tests plus the existing Kubernetes tests.
These fake/loopback checks are separate from the live evidence below.

Actual macOS-hosted Linux arm64 qualification used a fresh owned kind v0.33.0 /
Kubernetes v1.37.0 session and the existing fixture 0.2.0 image. The first run
reached the initial application successfully but exposed `kubectl patch
--patch-file -` as an invalid stdin route. It failed closed, cleaned its objects
and released its exact session. The runner now writes a real JSON patch file in
the fresh evidence directory while retaining UID and resourceVersion test
operations. A full-flow regression covers that command contract.

The corrected fresh-session run passed in 75.701 seconds. The projected file
changed at 62.898 seconds while environment and application cache remained
initial under the same Pod UID and boot ID. Explicit reload changed only the
cache. Replacing the recorded Pod produced a different Pod UID/boot ID with all
three channels rotated. UID-precondition cleanup confirmed absence of the
recorded Secret, ConfigMap, Deployment and nonce-owned Pods/ReplicaSets; exact
owned cluster release returned zero. A final Docker listing found no kind nodes.

Receipt: `work/kubernetes-secret-observer-acceptance.json`. It records current
app/render/teacher/manifest SHA256 hashes, namespace/object identities, image IDs,
all four actual label observations, projection duration and independent cleanup/
release results. The local fixture image identity was
`sha256:57730e381b72a8c2ab565819e1398fc39848ef5ce3624a2432a79f287791a493`.
No engine configuration, image build, learner volume, unrelated resource or
ordinary worker permission changed. No credentials or marker bytes were copied
from a real Secret. The two markers are fixed public teaching data.

This qualifies the documented positive teacher workflow on this platform.
Cancellation, collision and replacement guards are covered offline; this run
does not claim live fault-injection acceptance of every guard, native Windows
acceptance, encryption-at-rest verification or general Secret management.
Other advanced storage/network/controller capabilities remain separately scoped
and unqualified by this observation.

Final fixture gate: 189 focused Kubernetes tests passed in 1.61s; Ruff and strict
MyPy for the dedicated test passed. Re-running the complete Kubernetes authoring
entry point changed zero files. All four executable/manifest source hashes still
match the successful live receipt. Earlier failure provenance is retained in
`work/kubernetes-secret-observer-first-attempt.json`, including its actual initial
observation, successful fixture cleanup and exact-session release log.
