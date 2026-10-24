# k8s-046: explanatory solutions

Compare after your own attempt or an explicit reveal. These explanations describe the synthetic topology and stated API contracts. They are not fabricated runtime receipts.

## Mechanism review

The Container Network Interface, or CNI, is a plugin interface used in container networking. In Kubernetes, the chosen network implementation prepares Pod interfaces and connectivity according to cluster configuration. CNI is an interface and ecosystem, not one universal packet-forwarding algorithm.

Cross-node Pod traffic can use routed networks, encapsulation overlays or other implementation-specific mechanisms. An overlay wraps an inner packet in an outer packet so the underlying network can transport it between nodes. Encapsulation consumes header space, affecting the maximum transmission unit, or MTU, available to the inner traffic.

A small request may succeed while a large payload fails when MTU discovery, fragmentation or policy is misconfigured. This is different from a Service selector problem. Diagnose with bounded traffic and actual implementation evidence rather than changing cluster networking from a generic tutorial.

Separate the Pod-facing interface, node routing or overlay endpoint, underlay network and destination Pod interface. The control plane may show Ready Pods while the cross-node data path is broken. CNI setup failures can also prevent Pod sandbox creation before the app starts.

The synthetic topology uses two nodes and two Pod subnets to make the hop sequence visible. It does not claim that every CNI assigns per-node CIDRs in the same way. Optional live observations require the exact prepared CNI and permissions; the course does not install or replace network plugins.

## Exercise 1: Distinguish CNI interface and network implementation.

Do not infer packet behavior from the acronym alone. Inspect the installed implementation and configuration.

**Expected:** A plugin contract versus a concrete routing/policy system.

## Exercise 2: Label inner and outer addresses.

Encapsulation adds a delivery layer. The outer network need not route every Pod address directly.

**Expected:** Pod endpoints inside, node transport endpoints outside in the overlay example.

## Exercise 3: Draw a two-node request path.

A complete path identifies which component can drop or misroute traffic at each stage.

**Expected:** Pod interfaces, node forwarding and underlay hops are explicit.

## Exercise 4: Diagnose small-request success with large-payload failure.

Payload-dependent failure differs from a universally missing endpoint. Use bounded tests and implementation-specific evidence.

**Expected:** Investigate MTU and path behavior in addition to app limits.

## Exercise 5: Explain why Ready does not prove cross-node reachability.

A healthy local listener can coexist with broken node-to-node networking. Test from the relevant caller.

**Expected:** Readiness may be a local check with a narrower path.

## Exercise 6: Plan a CNI-specific qualification without replacing the plugin.

Changing the cluster network is a separate administrative action. A lesson should not perform it as an incidental repair.

**Expected:** Read configuration, state the implementation and run only owned bounded probes.
