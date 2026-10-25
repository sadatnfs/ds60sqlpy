# Kubernetes: beginner to advanced

> **Study in the unified classroom:** run `./classroom` from the repository
> root, then choose **Kubernetes: beginner to advanced** on `/classroom`. Python, SQL and all other
> subjects share this home and workspace. Each subject has its own theme;
> prerequisites guide your choices and you set the pace. The
> [one-command setup](../../docs/one-command-classroom.md) prepares the Docker runtimes and preserves saved
> work.


All 66 lessons have authored guides, learner artifacts, six inspectable exercises and separate explanations. The bounded browser profile executes only its reviewed Deployment/Service/ConfigMap or finite Job contract. Advanced activities are complete offline and host-lab lessons with explicit missing-capability boundaries, not invented browser execution.

Use [host-labs.md](host-labs.md) for exact targeting, 15-minute lease timing, observation and cleanup. Use the [preparation guide](../../docker/kubernetes/README.md) for the actual owned runtime. The [validation guide](../../docs/validation.md) distinguishes local content checks, actual owned-cluster execution and separately prepared host capabilities. Consult CI artifacts for the exact revision and platform before claiming runtime acceptance.

## Lesson sequence

| Lesson | Title | App mode |
| --- | --- | --- |
| [k8s-001](guides/k8s-001.md) | Terminal, files and an owned lab receipt | Reading worksheet; scoped host practice |
| [k8s-002](guides/k8s-002.md) | Processes, containers, images and ports | Reading worksheet; scoped host practice |
| [k8s-003](guides/k8s-003.md) | Kubernetes objects and YAML anatomy | Bounded YAML Run; host transitions separate |
| [k8s-004](guides/k8s-004.md) | Identity, namespaces and explicit targeting | Reading worksheet; scoped host practice |
| [k8s-005](guides/k8s-005.md) | Pods, image locality and logs | Bounded YAML Run; host transitions separate |
| [k8s-006](guides/k8s-006.md) | Deployments and reconciliation | Bounded YAML Run; host transitions separate |
| [k8s-007](guides/k8s-007.md) | Labels, selectors and Services | Bounded YAML Run; host transitions separate |
| [k8s-008](guides/k8s-008.md) | Readiness and eligible Service backends | Bounded YAML Run; host transitions separate |
| [k8s-009](guides/k8s-009.md) | ConfigMaps and configuration boundaries | Bounded YAML Run; host transitions separate |
| [k8s-010](guides/k8s-010.md) | Requests, limits and namespace budgets | Bounded YAML Run; host transitions separate |
| [k8s-011](guides/k8s-011.md) | Jobs and scheduled work | Bounded YAML Run; host transitions separate |
| [k8s-012](guides/k8s-012.md) | Debug from conditions, events and logs | Reading worksheet; scoped host practice |
| [k8s-013](guides/k8s-013.md) | Rollouts, revisions and recovery | Reading worksheet; scoped host practice |
| [k8s-014](guides/k8s-014.md) | Capstone 1: observable stateless service | Bounded YAML Run; host transitions separate |
| [k8s-015](guides/k8s-015.md) | Startup, liveness and readiness are different | Bounded YAML Run; host transitions separate |
| [k8s-016](guides/k8s-016.md) | Init containers and ephemeral shared files | Reading worksheet; scoped host practice |
| [k8s-017](guides/k8s-017.md) | Nonroot workloads and Pod Security | Bounded YAML Run; host transitions separate |
| [k8s-018](guides/k8s-018.md) | ServiceAccounts and RBAC boundaries | Reading worksheet; scoped host practice |
| [k8s-019](guides/k8s-019.md) | Synthetic Secrets and reload semantics | Reading worksheet; scoped host practice |
| [k8s-020](guides/k8s-020.md) | DNS and layered network diagnosis | Bounded YAML Run; host transitions separate |
| [k8s-021](guides/k8s-021.md) | NetworkPolicy with enforcement evidence | Reading worksheet; scoped host practice |
| [k8s-022](guides/k8s-022.md) | Volumes, claims and stateful identity | Reading worksheet; scoped host practice |
| [k8s-023](guides/k8s-023.md) | Gateway, Ingress and the external route | Reading worksheet; scoped host practice |
| [k8s-024](guides/k8s-024.md) | Kustomize and field ownership | Reading worksheet; scoped host practice |
| [k8s-025](guides/k8s-025.md) | Helm values without hidden side effects | Reading worksheet; scoped host practice |
| [k8s-026](guides/k8s-026.md) | Placement and node-local DaemonSets | Reading worksheet; scoped host practice |
| [k8s-027](guides/k8s-027.md) | Observability and service-level evidence | Reading worksheet; scoped host practice |
| [k8s-028](guides/k8s-028.md) | Capstone 2: stateful change with policy | Reading worksheet; scoped host practice |
| [k8s-029](guides/k8s-029.md) | Custom resources and structural schemas | Reading worksheet; scoped host practice |
| [k8s-030](guides/k8s-030.md) | Operators and reconciliation contracts | Reading worksheet; scoped host practice |
| [k8s-031](guides/k8s-031.md) | Admission policy and controlled denial | Reading worksheet; scoped host practice |
| [k8s-032](guides/k8s-032.md) | Disruptions and availability budgets | Reading worksheet; scoped host practice |
| [k8s-033](guides/k8s-033.md) | Autoscaling with a qualified metrics path | Reading worksheet; scoped host practice |
| [k8s-034](guides/k8s-034.md) | Traffic changes and progressive delivery | Reading worksheet; scoped host practice |
| [k8s-035](guides/k8s-035.md) | Watches and optimistic concurrency | Reading worksheet; scoped host practice |
| [k8s-036](guides/k8s-036.md) | Control-plane snapshots and data backups | Reading worksheet; scoped host practice |
| [k8s-037](guides/k8s-037.md) | Version skew and replacement-cluster rehearsal | Reading worksheet; scoped host practice |
| [k8s-038](guides/k8s-038.md) | Image provenance and offline verification | Reading worksheet; scoped host practice |
| [k8s-039](guides/k8s-039.md) | Multitenancy and threat boundaries | Reading worksheet; scoped host practice |
| [k8s-040](guides/k8s-040.md) | Incident response and bounded fault injection | Reading worksheet; scoped host practice |
| [k8s-041](guides/k8s-041.md) | Recovery objectives and reviewable runbooks | Reading worksheet; scoped host practice |
| [k8s-042](guides/k8s-042.md) | Capstone 3: platform release and incident review | Reading worksheet; scoped host practice |
| [k8s-043](guides/k8s-043.md) | Three address spaces: Pod IP, node IP and Service IP | Reading worksheet; separately prepared advanced host capability |
| [k8s-044](guides/k8s-044.md) | CIDRs, subnets, routing and address planning | Reading worksheet; separately prepared advanced host capability |
| [k8s-045](guides/k8s-045.md) | Pod network namespaces, sidecars and localhost | Reading worksheet; separately prepared advanced host capability |
| [k8s-046](guides/k8s-046.md) | CNI, cross-node paths, overlays and MTU | Reading worksheet; separately prepared advanced host capability |
| [k8s-047](guides/k8s-047.md) | ClusterIP Services and Layer 4 routing | Reading worksheet; separately prepared advanced host capability |
| [k8s-048](guides/k8s-048.md) | Cluster DNS, search paths, caching and discovery | Reading worksheet; separately prepared advanced host capability |
| [k8s-049](guides/k8s-049.md) | EndpointSlices, readiness and backend identity | Reading worksheet; separately prepared advanced host capability |
| [k8s-050](guides/k8s-050.md) | Service data planes: iptables, IPVS, nftables and eBPF | Reading worksheet; separately prepared advanced host capability |
| [k8s-051](guides/k8s-051.md) | NodePort and the path through a node | Reading worksheet; separately prepared advanced host capability |
| [k8s-052](guides/k8s-052.md) | LoadBalancer Services: cloud controllers and local limitations | Reading worksheet; separately prepared advanced host capability |
| [k8s-053](guides/k8s-053.md) | Ingress, HTTP routing and controller ownership | Reading worksheet; separately prepared advanced host capability |
| [k8s-054](guides/k8s-054.md) | Gateway API, routes and role-separated configuration | Reading worksheet; separately prepared advanced host capability |
| [k8s-055](guides/k8s-055.md) | TLS termination, certificates and upstream identity | Reading worksheet; separately prepared advanced host capability |
| [k8s-056](guides/k8s-056.md) | NAT, source IP and traffic policies | Reading worksheet; separately prepared advanced host capability |
| [k8s-057](guides/k8s-057.md) | Headless Services and stateful peer discovery | Reading worksheet; separately prepared advanced host capability |
| [k8s-058](guides/k8s-058.md) | NetworkPolicy ingress, selectors and additive rules | Reading worksheet; separately prepared advanced host capability |
| [k8s-059](guides/k8s-059.md) | Egress policy, DNS dependencies and external destinations | Reading worksheet; separately prepared advanced host capability |
| [k8s-060](guides/k8s-060.md) | IPv4, IPv6 and dual-stack Services | Reading worksheet; separately prepared advanced host capability |
| [k8s-061](guides/k8s-061.md) | Topology, zones and locality-aware traffic | Reading worksheet; separately prepared advanced host capability |
| [k8s-062](guides/k8s-062.md) | Probes, graceful draining and rollout traffic continuity | Reading worksheet; separately prepared advanced host capability |
| [k8s-063](guides/k8s-063.md) | Observability: events, logs, metrics and traces | Reading worksheet; separately prepared advanced host capability |
| [k8s-064](guides/k8s-064.md) | A packet-path troubleshooting method from DNS to response | Reading worksheet; separately prepared advanced host capability |
| [k8s-065](guides/k8s-065.md) | Service meshes, multi-cluster traffic and architectural limits | Reading worksheet; separately prepared advanced host capability |
| [k8s-066](guides/k8s-066.md) | Networking capstone: publish, protect, trace and recover | Reading worksheet; separately prepared advanced host capability |

## Deep networking and operations

The extension traces Pod, node and Service addresses through CNI, DNS, EndpointSlices, kernel/eBPF Service routing, NodePort, load balancers, Ingress, Gateway API, TLS, source-IP handling, headless discovery, NetworkPolicy, dual-stack, topology, draining and incident response. The [maintained networking fixtures](fixtures/networking/README.md) include manifests, a synthetic topology and an offline consistency checker. They do not install controllers or add new admitted browser operations. Windows host observations use Bash in WSL 2 and an explicit owned receipt.

## How to work

Read the guide, predict the stated case, write or edit your learner artifact, inspect one progressive hint at a time, then compare the separate solution after an attempt. A successful process or a manual read marker is not proof of understanding. Preserve actual learner edits in the app-owned workspace; the checked-in source is a starter.

The [portable authoring inputs](authoring/complete/README.md) regenerate the 38 added lesson bodies while preserving the four original pilots. Public synthetic signature material is immutable. No lesson downloads tools, starts a cluster or selects an ambient context when opened.
