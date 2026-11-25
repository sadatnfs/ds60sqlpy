# k8s-050: explanatory solutions

Attempt each exercise first, then compare ([study guide](../STUDY-GUIDE.md#solutions-and-the-ai-tutor)).

## Mechanism review

The Service API describes desired routing behavior. A data-plane implementation turns that intent into packet handling on nodes. kube-proxy is a common component that watches Service and endpoint state and programs the supported backend for the cluster version. Other networking implementations can provide Service routing through eBPF or different mechanisms.

On Linux, kube-proxy programs exactly one backend, chosen by its configuration. In Kubernetes 1.37 the default is iptables: a KUBE-SERVICES chain jumps to a per-Service KUBE-SVC chain, which picks a per-endpoint KUBE-SEP chain with random-probability rules, and that chain rewrites the destination (DNAT) to the Pod address. The nftables backend, GA since Kubernetes 1.33 and requiring Linux kernel 5.13 or later, keeps its rules in one `kube-proxy` table with verdict maps and processes endpoint changes more efficiently; the documentation says a future release will make it the default and recommends setting the mode explicitly. In nftables mode NodePort Services answer only on the node's primary addresses by default, not on 127.0.0.1. The IPVS backend uses kernel virtual servers plus iptables helpers; it has been deprecated since Kubernetes 1.35, and the current documentation schedules it to be disabled by default in 1.40 and removed in 1.43, so new clusters should choose nftables or iptables.

An eBPF-based implementation can attach programmable logic at particular kernel hooks. That changes how traffic is handled and observed, but it does not eliminate the need for endpoint identity, policy, routing and application acceptance. The API contract and the implementation evidence remain separate layers.

Begin diagnosis by identifying the installed implementation, version and active mode. On a kubeadm-style cluster, including kind, the `mode` field inside the `config.conf` key of the kube-system `kube-proxy` ConfigMap names the backend; an empty value means the release default. A Service object can be correct while a node’s programmed state is stale or broken. Conversely, reading a packet rule does not prove the application accepts a connection.

The course does not modify node packet tables or switch proxy modes. Use the synthetic control/data-plane sequence and consult the prepared environment’s operator documentation. Any privileged host inspection is a separately authorized capability, not part of a browser lesson.

## Exercise 1: Distinguish Service API and data plane.

A declarative object needs an implementation to affect traffic. Both layers require evidence.

**Expected:** Desired routing objects versus actual packet handling.

## Exercise 2: Identify why proxy-mode advice is version-sensitive.

A recommendation that was correct for an older release, such as choosing IPVS for performance, can now point at a deprecated backend. Read the documentation for the installed release, check the node kernel, and record the configured mode explicitly so an upgrade cannot change the backend silently.

**Expected:** In Kubernetes 1.37 iptables is the default, nftables has been GA since 1.33 and needs kernel 5.13 or later, and IPVS has been deprecated since 1.35 with removal scheduled, so advice depends on the release and the node kernel.

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
