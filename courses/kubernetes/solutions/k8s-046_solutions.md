# k8s-046: explanatory solutions

Attempt each exercise first, then compare ([study guide](../STUDY-GUIDE.md#solutions-and-the-ai-tutor)).

## Mechanism review

The Container Network Interface, or CNI, is a plugin interface used in container networking. In Kubernetes, the chosen network implementation prepares Pod interfaces and connectivity according to cluster configuration. CNI is an interface and ecosystem, not one universal packet-forwarding algorithm.

Cross-node Pod traffic can use routed networks, encapsulation overlays or other implementation-specific mechanisms. An overlay wraps an inner packet in an outer packet so the underlying network can transport it between nodes. Encapsulation consumes header space, affecting the maximum transmission unit, or MTU, available to the inner traffic.

A small request may succeed while a large payload fails when MTU discovery, fragmentation or policy is misconfigured. This is different from a Service selector problem. Diagnose with bounded traffic and actual implementation evidence rather than changing cluster networking from a generic tutorial.

Separate the Pod-facing interface, node routing or overlay endpoint, underlay network and destination Pod interface. The control plane may show Ready Pods while the cross-node data path is broken. CNI setup failures can also prevent Pod sandbox creation before the app starts.

The synthetic topology uses two nodes and two Pod subnets to make the hop sequence visible. It does not claim that every CNI assigns per-node CIDRs in the same way. Optional live observations require the exact prepared CNI and permissions; the course does not install or replace network plugins.

## Exercise 1: Distinguish CNI interface and network implementation.

Do not infer packet behavior from the acronym alone. Inspect the installed implementation and configuration.

**Expected:** A plugin contract versus a concrete routing/policy system.

**Solution reasoning**

- **Approach:** Separate the CNI specification, which defines how a runtime calls a plugin, from the plugin that programs routes and policy.
- **Why it is correct:** CNI only standardizes add and delete calls; packet behavior comes from the installed implementation and its config.
- **Plausible wrong approach:** Predicting overlay or policy behavior from the word CNI alone skips reading which plugin is installed.
- **How to verify:** The answer names a plugin contract on one side and a concrete routing and policy system on the other.

## Exercise 2: Label inner and outer addresses.

Encapsulation adds a delivery layer. The outer network need not route every Pod address directly.

**Expected:** Pod endpoints inside, node transport endpoints outside in the overlay example.

**Solution reasoning**

- **Approach:** Label the inner header with Pod addresses and the outer header with node transport addresses.
- **Why it is correct:** Encapsulation wraps the Pod packet so the underlay only needs routes between nodes, not to every Pod address.
- **Plausible wrong approach:** Expecting the underlay to route Pod addresses directly describes a routed design, not this overlay.
- **How to verify:** Inner addresses are Pods, and outer addresses are nodes.

## Exercise 3: Draw a two-node request path.

A complete path identifies which component can drop or misroute traffic at each stage.

**Expected:** Pod interfaces, node forwarding and underlay hops are explicit.

**Solution reasoning**

- **Approach:** Draw source Pod interface, source node forwarding, underlay hops, destination node forwarding and target Pod interface.
- **Why it is correct:** Each stage can drop or misroute a packet, so naming them shows where to look when the request fails.
- **Plausible wrong approach:** Drawing a single arrow from Pod to Pod hides the node and underlay steps where most faults occur.
- **How to verify:** Pod interfaces, node forwarding and underlay hops each appear in the path.

## Exercise 4: Diagnose small-request success with large-payload failure.

Payload-dependent failure differs from a universally missing endpoint. Use bounded tests and implementation-specific evidence.

**Expected:** Investigate MTU and path behavior in addition to app limits.

**Solution reasoning**

- **Approach:** Compare which request sizes pass and fail and treat MTU as a hypothesis next to application limits.
- **Why it is correct:** Encapsulation adds header bytes, so packets near the MTU can be dropped while small requests still pass.
- **Plausible wrong approach:** Concluding the endpoint is missing ignores that small requests succeed on the same path.
- **How to verify:** The plan includes an MTU or path check alongside application size limits.

## Exercise 5: Explain why Ready does not prove cross-node reachability.

A healthy local listener can coexist with broken node-to-node networking. Test from the relevant caller.

**Expected:** Readiness may be a local check with a narrower path.

**Solution reasoning**

- **Approach:** State what the readiness probe actually exercises and compare it with the cross-node path.
- **Why it is correct:** The kubelet probes from the Pod's own node, so a Ready Pod says nothing about traffic from other nodes.
- **Plausible wrong approach:** Treating Ready as proof any client can reach the Pod would miss a broken node-to-node path.
- **How to verify:** The answer says readiness may test a narrower local path and calls for a test from the relevant caller.

## Exercise 6: Plan a CNI-specific qualification without replacing the plugin.

Changing the cluster network is a separate administrative action. A lesson should not perform it as an incidental repair.

**Expected:** Read configuration, state the implementation and run only owned bounded probes.

**Solution reasoning**

- **Approach:** Read the plugin configuration, name the implementation and plan owned bounded probes only.
- **Why it is correct:** Replacing or reconfiguring the cluster network is an administrative change that affects every workload.
- **Plausible wrong approach:** Reinstalling the CNI to fix a lesson probe would break networking for others on the cluster.
- **How to verify:** The plan reads config, names the plugin and runs only owned probes.
