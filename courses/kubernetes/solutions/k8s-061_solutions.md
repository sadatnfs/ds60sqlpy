# k8s-061: explanatory solutions

Compare after your own attempt or an explicit reveal. These explanations describe the synthetic topology and stated API contracts. They are not fabricated runtime receipts.

## Mechanism review

A topology label describes placement, such as a node or availability zone. Locality-aware routing tries to prefer nearby endpoints to reduce latency or cross-zone traffic, subject to implementation and policy. It is a preference or constraint with tradeoffs, not a guarantee of balanced load or failure tolerance.

Spreading replicas across zones can improve resilience to a zone failure, but only if scheduling, storage and dependencies also span the required failure domains. A local preference can concentrate traffic on a small number of endpoints if placement is uneven. Capacity and availability must be considered together.

Kubernetes 1.37 offers two Service-level mechanisms. The `spec.trafficDistribution` field accepts `PreferSameZone`, which sends a caller's traffic to ready endpoints in its own zone and falls back cluster-wide when that zone has none, and `PreferSameNode`, which prefers the caller's node, then its zone, then the cluster. `PreferClose`, the first value to reach GA in 1.33, is now a deprecated alias for `PreferSameZone`. The older `service.kubernetes.io/topology-mode: Auto` annotation assigns zone hints in proportion to allocatable CPU, includes safeguards for small endpoint counts and takes precedence over the field when both are set. Without either, traffic is spread across all ready endpoints. The EndpointSlice controller publishes these preferences as hints, and the service proxy must honor them. The lesson's synthetic two-zone example does not promise that a local kind cluster reproduces cloud-zone behavior.

Separate workload placement from traffic selection. Topology spread constraints influence where Pods can be scheduled; Service routing policy influences which eligible endpoint a caller uses. One does not automatically configure the other.

For the synthetic example, zoneA has two ready app endpoints and zoneB has one. A local-only rule can overload the single endpoint in zoneB even when total cluster capacity appears sufficient. A failover policy must define what happens when a zone has no eligible local endpoint.

A spread constraint such as `maxSkew: 1` with `topologyKey: topology.kubernetes.io/zone` and `whenUnsatisfiable: DoNotSchedule` keeps the per-zone counts of matching Pods within one of each other, which is what keeps zone preferences safe. `PreferSameZone` does not rebalance load: a zone with one endpoint sends all of its traffic there. The stricter `internalTrafficPolicy: Local` uses only endpoints on the caller's node and drops traffic when there are none, so it is a requirement rather than a preference.

## Exercise 1: Predict per-endpoint load under equal local client demand.

Locality can reduce network distance while worsening imbalance. Count capacity at the selected failure domain.

**Expected:** ZoneB can place twice the load on its single endpoint.

## Exercise 2: Distinguish placement and traffic policy.

Both influence the final path but are controlled by different mechanisms.

**Expected:** Scheduling location versus request destination choice.

## Exercise 3: Design a two-zone failure scenario.

A resilience claim needs a concrete lost-domain case. Include data dependencies and storage placement.

**Expected:** State which endpoints remain and whether routing can fail over.

## Exercise 4: Diagnose local preference with insufficient nearby capacity.

Cluster-wide counts can hide a zonal bottleneck. Choose a policy consistent with capacity and failover requirements.

**Expected:** Inspect endpoint distribution and actual load, not only total replicas.

## Exercise 5: Explain version-dependent topology behavior.

Do not copy a field from a newer tutorial into an older cluster and infer it is enforced. A service proxy that ignores the hints, or an annotation that takes precedence, changes the actual routing even when the Service field is accepted by the API server.

**Expected:** Name the trafficDistribution values the pinned release accepts (PreferSameZone, PreferSameNode and the deprecated PreferClose), the precedence of the topology-mode annotation and whether the data plane honors EndpointSlice hints.

## Exercise 6: Defend a locality tradeoff.

The decision should include measurable goals and a fallback strategy rather than an unqualified local-is-better rule.

Evaluate the failure case as well as steady state. If the only endpoint in zoneB becomes unready, identify whether the selected policy permits a remote endpoint or leaves that caller without a destination. Record error rate and endpoint placement during the transition. Replica count across the whole cluster cannot substitute for enough usable capacity in the failure domain that the routing policy actually selects.

**Expected:** Latency/cost benefits are balanced against capacity and failure behavior.
