# Kubernetes track design

Status: planned, checked 2026-10-22. These files are design artifacts outside the active catalog. They install no cluster, add no runner and grant no credential. The existing Kubernetes descriptor remains save/view only. The canonical [42-lesson plan](../plans/kubernetes.json) supplies each outcome, lab, verification, prerequisite and study estimate.

## Outcome and beginner entry

A learner starts with files, a terminal, processes, containers and port diagrams, then learns to declare an owned workload and prove what it is actually doing. No Python or SQL catalog chain is required. `python-55`, `python-svc-02` and `bridge-ops-01` are optional transfer reading for someone who already completed them. They are not mandatory planner gates.

The 42 units separate three different kinds of evidence: control-plane convergence, application traffic/data behavior, and permission/ownership boundaries. Fourteen beginner lessons build a complete stateless service and a fault diagnosis. Fourteen intermediate lessons add identity, state, Gateway/Ingress routing, node-local DaemonSet placement and real policy enforcement. Fourteen advanced lessons use dedicated fixtures for API extension, admission, disruption, recovery and release review. Three capstones integrate those mechanisms; lesson count is a consequence of the distinct mechanisms, not a new promise of 60 calendar days.

## Runtime and privilege model

The proposed runtime IDs are `reading` and `k8s-kind`. A host-side provisioner creates a named course-owned kind cluster only after explicit local-engine selection and consent. It records kind version, Kubernetes node image digest, architecture, node container identities and the control-plane CA/endpoint identity. Kubernetes has no universal user-visible cluster UID; the receipt uses a host-verified `kube-system` namespace UID plus the CA/endpoint and owned node identities. It must never treat the user's ambient kubectl current-context as authorization.

The normal worker receives only a short-lived, audience-appropriate credential for one lease namespace. Its ServiceAccount lives in a private provisioner-owned authentication namespace, outside the workload namespace. No privileged ServiceAccount, real credential or production Secret is placed in the learner namespace. The application browser never receives a raw Docker socket, admin kubeconfig or cluster-admin token. The worker also receives no Docker socket. Host admin material and worker kubeconfig/token files stay in an ephemeral private host-session directory or read-only worker mount, never in `.learning`, course exports, learner backups or evidence transcripts. Token expiration uses the server-returned expiry, not an invented guarantee based on the requested duration. [ServiceAccount lifecycle](https://kubernetes.io/docs/reference/access-authn-authz/service-accounts-admin/).

A namespace Role is not a hostile-workload sandbox. Creating Pods can expose namespace resources indirectly, so only synthetic data belongs there. Host-installed admission rejects privileged workloads, host namespaces/paths, arbitrary volume/device mounts, service-account token mounting and images outside the fixture allowlist. RBAC denies cross-namespace access and privilege escalation. [RBAC guidance](https://kubernetes.io/docs/concepts/security/rbac-good-practices/) supports this least-privilege boundary. Network isolation requires separately qualified enforcement; do not assume kind's default networking implements every policy.

The default transport is a host-provisioned worker on the controlled engine network, orchestrated by a host-local broker with fixed reviewed operations and explicit target arguments. Its internal control-plane endpoint, TLS CA and server name must be qualified together. An optional manual host-terminal path uses a separately scoped worker identity; it is not a browser-controlled host shell. A containerized worker cannot simply use the host's loopback API address. That proof is an implementation gate, not an excuse to expose the API on every host interface or mount an admin kubeconfig. Structured manifest content is input; manifests cannot supply an arbitrary shell command or cluster target.

Advanced lessons needing CRDs, admission policy, node disruption, metrics/CNI changes or control-plane recovery require an exclusive dedicated cluster lease. The host provisioner performs fixed reviewed privileged operations after the lease/operation check. Browser and ordinary worker identities remain limited. RBAC `resourceNames` does not constrain creation to a name, so the design does not hand the worker unrestricted CRD/role creation and call it scoped. A host-precreated named fixture or broker-owned operation is the boundary. No shared user cluster, production context or another learner's namespace is used for an advanced exercise.

## Version and platform qualification

The primary-source review found kind v0.33.0 and supported Kubernetes minor branches 1.37, 1.36 and 1.35. The kind release publishes a default 1.37.0 node image digest; a final implementation must qualify a supported patch/node-image pair from that release's supported assets, pin the full digest for each architecture and recheck support at release time. A later Kubernetes patch is not assumed usable with an arbitrary kind node image. [kind release](https://github.com/kubernetes-sigs/kind/releases/tag/v0.33.0), [Kubernetes releases](https://kubernetes.io/releases/).

| Host | Proposed route | Qualification still required |
| --- | --- | --- |
| Windows 11 x64 | Existing supported local Linux engine, preferably its WSL 2 route; host preparation and worker tools stay in one clearly named Windows/WSL environment | API reachability/TLS, quoted paths, loopback service inspection, filesystem permissions and complete cancellation/cleanup |
| Windows ARM | Separate pending profile | Native Linux arm64 node/workload image availability and the selected Windows engine/tool support; no x64-emulation acceptance claim |
| macOS Apple Silicon | Native arm64 kind node/workload images through the existing local engine | Multi-node boot, storage, host-broker transport and disconnected cache proof |
| macOS Intel | Native amd64 images on a supported OS/engine | Same proof with its exact architecture and current host support |
| Linux amd64/arm64 | Matching local engine and native node/workload images | Rootful/rootless capabilities, cgroups, ownership and addon-specific behavior; rootless is not blanket claimed |

The official [kind WSL2 guide](https://kind.sigs.k8s.io/docs/user/using-wsl2/) documents a Linux route; it is not permission to install WSL, change the learner's existing engine settings or assume every current Windows machine qualifies. Windows-container mode is not the profile. All platform runtime cells are pending in this design phase. Cluster preparation, addons and multi-node labs have measured CPU/RAM/disk budgets only after actual proof. No existing engine VM is resized or restarted by this plan.

## Offline fixture contract

The host preparation bundle will include checksummed kind/kubectl binaries, release-pinned node images, architecture-matched workload/client images, public schemas, a pinned vendored Helm chart, synthetic storage/data fixtures, failure transcripts and controller/policy/metrics fixtures for the relevant advanced lease. It will record licenses, download sources and fixture digests. The [kind offline guide](https://kind.sigs.k8s.io/docs/user/working-offline/) requires preparing node images and using release digests; workload images must also be loaded onto every node that can schedule them. A cached host image alone is not evidence of a node cache.

The beginner HTTP fixture is a proposed course-owned image alias `ds60-http-fixture:v1`, not an existing published image. Host preparation must resolve/verify its content and preload it before enabling the pilot. Its planned server runs as UID 65532, has no writable root filesystem requirement and exposes only GET `/ready` returning status 200/body `ready`, GET `/version` returning a fixed version, and 404 for unknown paths. It has no HTTP shell/upload interface. A separate `check` mode performs a bounded HTTP request and exits0 only for its expected status/body. The fixture requires no Kubernetes token. The upstream agnhost test server was reviewed but is not the default: its [netexec source](https://raw.githubusercontent.com/kubernetes/kubernetes/master/test/images/agnhost/netexec/netexec.go) also contains shell/upload endpoints. No HTTP fixture image is built or claimed available here.

Gateway lessons use a dedicated host-qualified controller/CRD lease and an owned Route; there is no assumed cloud LoadBalancer address. A synthetic TLS fixture verifies its supplied public CA explicitly without `--insecure` or installing a trust root globally. Ingress remains useful to read, but the [official Ingress documentation](https://kubernetes.io/docs/concepts/services-networking/ingress/) calls its API frozen and recommends Gateway for new development. Restricted synthetic DaemonSets teach one Pod per eligible node without pretending a learner can install a privileged node agent.

The [pilot](../samples/kubernetes-pilot.md) uses `imagePullPolicy: Never` and is therefore honest about a missing preload. Missing images, unsupported CNI, absent metrics, expired credentials and an unprepared cluster each have their own capability message. Run never repairs those states by installing a cluster/addon or downloading arbitrary images. Offline transcript/diagram exercises remain useful when an owned live lease is unavailable; they are labeled reading evidence, not live acceptance.

## Teaching and assessment model

Beginners predict controller behavior, inspect desired versus observed state, make one change, verify independently and explain a failure. The [separate pilot solution](../samples/kubernetes-pilot-solutions.md) opens only after an attempt or an explicit reveal. Teacher feedback first asks for the relevant observation, then offers one hint. A pass requires the learner's explanation plus discriminating evidence; clicking Apply, waiting for a green badge or listing an object is insufficient.

The core evidence triangle is: Deployment generation/replica convergence, Pod readiness and eligible EndpointSlice target UIDs, then an in-cluster client response. A Pod can be Running but unready. Unready addresses may remain in EndpointSlices with `ready:false`; count eligible entries, not only objects. A Service port-forward often forwards directly to a selected Pod and is not sufficient proof of ClusterIP selection or ordinary Service routing. [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/), [EndpointSlices](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/).

Other anti-misconceptions have explicit counterexamples: labels do not create application health; readiness is not liveness; a request is not a CPU cap; quota admission is not scheduling; a Secret is not encrypted by base64; a PVC is not a backup; an applied NetworkPolicy is not enforcement; HPA is not instant; PDB does not prevent every outage; a digest is not publisher identity; and a kind replacement rehearsal is not a production HA or in-place upgrade proof. NetworkPolicy lessons require an actual allowed/denied connection test on a qualified CNI, as the [Kubernetes documentation](https://kubernetes.io/docs/concepts/services-networking/network-policies/) requires.

## Three integration reviews

1. `k8s-014`: a stateless service must converge to two eligible backend UIDs, return the fixed payload through an in-cluster client, recover one fault and clean up only its owned resources.
2. `k8s-028`: a synthetic stateful release must prove data markers, actual network policy, limited identity, failed-change recovery and an explicit retention/reclaim choice.
3. `k8s-042`: a custom-resource release and incident drill must include application/data/authorization gates, dedicated-lease receipts for every privileged action and measured recovery evidence. An etcd snapshot is assessed separately from a PVC/data backup.

Every stage includes retrieval after a delay, a fault whose symptoms resemble another fault, and a transfer task with changed resource names/labels. The advanced learner explains why their evidence excludes a competing cause and which production claims the local fixture cannot support.

## Cleanup, progress and activation gates

The host records namespace UID and created resource UIDs before allowing changes. Cleanup is idempotent, bounded and owner-checked: remove only recorded resources or the still-owned disposable namespace, verify no owned objects remain, then revoke the RoleBinding and delete the provisioner-owned worker identity. Deleting the identity/permissions and checking denial is distinct from waiting for token expiry. An expired lease must not keep a stale credential active. Never force-remove arbitrary finalizers, delete an ambient namespace or delete a cluster whose owned node identities no longer match.

Progress stores learner manifests, predictions, redacted observation fields, fixture hashes and reasoning. It never stores kubeconfig, bearer tokens, admin certificates, raw Secret data or an etcd snapshot. A snapshot can contain credentials and belongs only in private lease storage with an explicit retention decision. The learner's source/evidence survives cancellation or unavailable infrastructure; the temporary cluster does not become a portable credential backup.

Before catalog activation, create the real `courses/kubernetes/` files and local guidance, implement and test the reviewed broker/lease/credential lifecycle, qualify the full OS/architecture/addon matrix, prove offline operation and cleanup after every failure stage, then register additively and run the normal depth/practice/navigation/app/MCP checks. This design performs none of those cluster actions and claims no live Kubernetes acceptance.

## Planned lesson sequence

This table is a compact view of the canonical JSON plan; the JSON contains the concrete lab and independent verification for every row.

### Beginner

| ID | Lesson | Minutes | Direct planned prerequisites |
| --- | --- | ---: | --- |
| `k8s-001` | Terminal, files and an owned lab receipt | 75 | None |
| `k8s-002` | Processes, containers, images and ports | 90 | `k8s-001` |
| `k8s-003` | Kubernetes objects and YAML anatomy | 90 | `k8s-002` |
| `k8s-004` | Identity, namespaces and explicit targeting | 90 | `k8s-003` |
| `k8s-005` | Pods, image locality and logs | 90 | `k8s-004` |
| `k8s-006` | Deployments and reconciliation | 105 | `k8s-005` |
| `k8s-007` | Labels, selectors and Services | 90 | `k8s-006` |
| `k8s-008` | Readiness and eligible Service backends | 120 | `k8s-007` |
| `k8s-009` | ConfigMaps and configuration boundaries | 90 | `k8s-008` |
| `k8s-010` | Requests, limits and namespace budgets | 105 | `k8s-006` |
| `k8s-011` | Jobs and scheduled work | 90 | `k8s-005` |
| `k8s-012` | Debug from conditions, events and logs | 105 | `k8s-008`, `k8s-010`, `k8s-011` |
| `k8s-013` | Rollouts, revisions and recovery | 105 | `k8s-009`, `k8s-012` |
| `k8s-014` | Capstone 1: observable stateless service | 180 | `k8s-009`, `k8s-010`, `k8s-011`, `k8s-012`, `k8s-013` |

### Intermediate

| ID | Lesson | Minutes | Direct planned prerequisites |
| --- | --- | ---: | --- |
| `k8s-015` | Startup, liveness and readiness are different | 105 | `k8s-008`, `k8s-013` |
| `k8s-016` | Init containers and ephemeral shared files | 105 | `k8s-005`, `k8s-009` |
| `k8s-017` | Nonroot workloads and Pod Security | 105 | `k8s-010` |
| `k8s-018` | ServiceAccounts and RBAC boundaries | 120 | `k8s-004`, `k8s-017` |
| `k8s-019` | Synthetic Secrets and reload semantics | 105 | `k8s-009`, `k8s-018` |
| `k8s-020` | DNS and layered network diagnosis | 105 | `k8s-007`, `k8s-012` |
| `k8s-021` | NetworkPolicy with enforcement evidence | 120 | `k8s-018`, `k8s-020` |
| `k8s-022` | Volumes, claims and stateful identity | 120 | `k8s-010`, `k8s-016` |
| `k8s-023` | Gateway, Ingress and the external route | 120 | `k8s-013`, `k8s-017`, `k8s-020` |
| `k8s-024` | Kustomize and field ownership | 105 | `k8s-003`, `k8s-013` |
| `k8s-025` | Helm values without hidden side effects | 120 | `k8s-019`, `k8s-024` |
| `k8s-026` | Placement and node-local DaemonSets | 120 | `k8s-010`, `k8s-012` |
| `k8s-027` | Observability and service-level evidence | 120 | `k8s-012`, `k8s-015`, `k8s-020` |
| `k8s-028` | Capstone 2: stateful change with policy | 240 | `k8s-017`, `k8s-018`, `k8s-021`, `k8s-022`, `k8s-023`, `k8s-025`, `k8s-027` |

### Advanced

| ID | Lesson | Minutes | Direct planned prerequisites |
| --- | --- | ---: | --- |
| `k8s-029` | Custom resources and structural schemas | 120 | `k8s-028` |
| `k8s-030` | Operators and reconciliation contracts | 135 | `k8s-006`, `k8s-029` |
| `k8s-031` | Admission policy and controlled denial | 120 | `k8s-017`, `k8s-029` |
| `k8s-032` | Disruptions and availability budgets | 135 | `k8s-026`, `k8s-028` |
| `k8s-033` | Autoscaling with a qualified metrics path | 135 | `k8s-010`, `k8s-027`, `k8s-032` |
| `k8s-034` | Traffic changes and progressive delivery | 135 | `k8s-013`, `k8s-021`, `k8s-027` |
| `k8s-035` | Watches and optimistic concurrency | 120 | `k8s-003`, `k8s-018`, `k8s-030` |
| `k8s-036` | Control-plane snapshots and data backups | 150 | `k8s-018`, `k8s-022`, `k8s-028` |
| `k8s-037` | Version skew and replacement-cluster rehearsal | 135 | `k8s-024`, `k8s-028`, `k8s-029` |
| `k8s-038` | Image provenance and offline verification | 135 | `k8s-017`, `k8s-025`, `k8s-031` |
| `k8s-039` | Multitenancy and threat boundaries | 120 | `k8s-018`, `k8s-021`, `k8s-031` |
| `k8s-040` | Incident response and bounded fault injection | 150 | `k8s-027`, `k8s-032`, `k8s-035` |
| `k8s-041` | Recovery objectives and reviewable runbooks | 150 | `k8s-036`, `k8s-037`, `k8s-040` |
| `k8s-042` | Capstone 3: platform release and incident review | 300 | `k8s-030`, `k8s-031`, `k8s-033`, `k8s-034`, `k8s-038`, `k8s-039`, `k8s-041` |

## Primary sources checked 2026-10-22

- [kind Quick Start](https://kind.sigs.k8s.io/docs/user/quick-start/): Host preparation, platform binaries, owned cluster names and loading local images.
- [kind v0.33.0 release](https://github.com/kubernetes-sigs/kind/releases/tag/v0.33.0): Version qualification candidate and release-published node image digests.
- [kind Working Offline](https://kind.sigs.k8s.io/docs/user/working-offline/): Preload node/workload images and record exact content digests before disconnected study.
- [kind Using WSL2](https://kind.sigs.k8s.io/docs/user/using-wsl2/): Windows Linux-container/WSL2 route; current engine prerequisites require separate verification.
- [Kubernetes supported releases](https://kubernetes.io/releases/): Recheck supported minor/patch versions at implementation;1.37/1.36/1.35 are listed at review.
- [Kubernetes Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/): Desired/observed state, rollout generation and controller-managed Pods.
- [Kubernetes probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/): Readiness traffic eligibility versus liveness/startup restart behavior.
- [Kubernetes EndpointSlices](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/): Ready/serving/terminating endpoint conditions and UID-based backend checks.
- [Kubernetes RBAC good practices](https://kubernetes.io/docs/concepts/security/rbac-good-practices/): Least privilege, namespace escalation risks and separation of worker/admin identities.
- [Kubernetes ServiceAccounts](https://kubernetes.io/docs/reference/access-authn-authz/service-accounts-admin/): Bound short-lived tokens and credential lifecycle; requested duration is not a fabricated expiration guarantee.
- [Kubernetes NetworkPolicy](https://kubernetes.io/docs/concepts/services-networking/network-policies/): A policy object does not prove enforcement without a capable networking implementation.
- [agnhost netexec source](https://raw.githubusercontent.com/kubernetes/kubernetes/master/test/images/agnhost/netexec/netexec.go): The test server exposes shell/upload endpoints, motivating a smaller course-owned HTTP fixture instead.

- [Kubernetes Gateway API](https://kubernetes.io/docs/concepts/services-networking/gateway/): Route/controller roles and separate qualification.
- [Kubernetes Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/): frozen API and the Gateway direction.
- [Kubernetes DaemonSet](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/): one Pod per eligible node and placement semantics.
