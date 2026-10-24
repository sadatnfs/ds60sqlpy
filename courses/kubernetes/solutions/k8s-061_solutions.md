# k8s-061: explanatory solutions

Compare after your own attempt or an explicit reveal. These explanations describe the synthetic topology and stated API contracts. They are not fabricated runtime receipts.

## Mechanism review

A topology label describes placement, such as a node or availability zone. Locality-aware routing tries to prefer nearby endpoints to reduce latency or cross-zone traffic, subject to implementation and policy. It is a preference or constraint with tradeoffs, not a guarantee of balanced load or failure tolerance.

Spreading replicas across zones can improve resilience to a zone failure, but only if scheduling, storage and dependencies also span the required failure domains. A local preference can concentrate traffic on a small number of endpoints if placement is uneven. Capacity and availability must be considered together.

Topology features evolve with Kubernetes versions. Fields, hints and traffic-distribution semantics should be read for the actual release and data plane. The lesson teaches the reasoning with a synthetic two-zone example and does not promise that every local kind cluster can reproduce cloud-zone behavior.

Separate workload placement from traffic selection. Topology spread constraints influence where Pods can be scheduled; Service routing policy influences which eligible endpoint a caller uses. One does not automatically configure the other.

For the synthetic example, zoneA has two ready app endpoints and zoneB has one. A local-only rule can overload the single endpoint in zoneB even when total cluster capacity appears sufficient. A failover policy must define what happens when a zone has no eligible local endpoint.

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

Do not copy a field from a newer tutorial into an older cluster and infer it is enforced.

**Expected:** Use the actual API/controller/data-plane support matrix.

## Exercise 6: Defend a locality tradeoff.

The decision should include measurable goals and a fallback strategy rather than an unqualified local-is-better rule.

Evaluate the failure case as well as steady state. If the only endpoint in zoneB becomes unready, identify whether the selected policy permits a remote endpoint or leaves that caller without a destination. Record error rate and endpoint placement during the transition. Replica count across the whole cluster cannot substitute for enough usable capacity in the failure domain that the routing policy actually selects.

**Expected:** Latency/cost benefits are balanced against capacity and failure behavior.
