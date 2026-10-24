# k8s-050: explanatory solutions

Compare after your own attempt or an explicit reveal. These explanations describe the synthetic topology and stated API contracts. They are not fabricated runtime receipts.

## Mechanism review

The Service API describes desired routing behavior. A data-plane implementation turns that intent into packet handling on nodes. kube-proxy is a common component that watches Service and endpoint state and programs the supported backend for the cluster version. Other networking implementations can provide Service routing through eBPF or different mechanisms.

iptables, IPVS and nftables refer to Linux packet-processing facilities with different models and operational properties. Their availability, maturity and support status depend on the Kubernetes and operating-system version. Do not assume every current cluster supports every mode or that an old performance claim applies unchanged.

An eBPF-based implementation can attach programmable logic at particular kernel hooks. That changes how traffic is handled and observed, but it does not eliminate the need for endpoint identity, policy, routing and application acceptance. The API contract and the implementation evidence remain separate layers.

Begin diagnosis by identifying the installed implementation, version and active mode. A Service object can be correct while a node’s programmed state is stale or broken. Conversely, reading a packet rule does not prove the application accepts a connection.

The course does not modify node packet tables or switch proxy modes. Use the synthetic control/data-plane sequence and consult the prepared environment’s operator documentation. Any privileged host inspection is a separately authorized capability, not part of a browser lesson.

## Exercise 1: Distinguish Service API and data plane.

A declarative object needs an implementation to affect traffic. Both layers require evidence.

**Expected:** Desired routing objects versus actual packet handling.

## Exercise 2: Identify why proxy-mode advice is version-sensitive.

Use the documentation matching the installed environment rather than a universal mode recommendation.

**Expected:** Support and behavior change with Kubernetes and kernel releases.

## Exercise 3: Draw the watch-to-packet sequence.

The sequence gives you places to check when intent and behavior disagree.

**Expected:** API observation, reconciliation, programmed state and packet decision are separate.

## Exercise 4: Diagnose one-node-only Service failure.

A cluster-wide spec can be correct while one node is unhealthy. Preserve caller placement in the evidence.

**Expected:** Compare node-local data-plane and policy behavior.

## Exercise 5: Explain why eBPF is not an application correctness proof.

A fast or sophisticated data plane can still route to an incorrect app response. Test the user-visible contract.

**Expected:** It is an implementation technique for specific kernel behavior.

## Exercise 6: Plan an implementation-specific incident review.

Do not change packet tables or modes as a speculative lesson repair. Escalate the missing operator capability explicitly.

For the one-node failure example, record the current Service UID, endpoint Pod UIDs and the caller node before inspecting the implementation. A healthy API watch elsewhere does not prove this node installed the same mapping. Use that implementation’s documented read-only observations to distinguish stale reconciliation from an application listener failure, and retain both the failing and repaired paths.

**Expected:** Record active mode, versions, owned probe results and permitted diagnostics.
