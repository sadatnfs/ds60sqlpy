# k8s-021: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

A NetworkPolicy describes allowed traffic relationships for selected Pods when the cluster networking implementation enforces it. Creating the API object is not evidence that packets are filtered. The course therefore requires a separately qualified policy-capable CNI and before/after client observations for this host lab.

The example isolates ingress to app=hello and then allows TCP8080 from same-namespace Pods labeled role=lesson-client. Policies are additive:the allowed traffic is the union of applicable allow rules. A deny-all ingress policy plus a matching allow policy does not mean the deny rule overrides the allow. Egress isolation is a separate direction and is not enabled by this ingress-only example.

The normal browser adapter does not admit NetworkPolicy or arbitrary client labels. Its basic hello success cannot establish isolation. This worksheet uses real policy manifests and a synthetic traffic matrix until an exclusive policy-enabled lease supplies the required live capability.

## Exercise 1: Identify destination scope

The policy applies to selected destination Pods in its namespace. It does not automatically isolate all namespace egress or unrelated applications.

**Expected:** app=hello destinations, Ingress only.

## Exercise 2: Explain additive rules

NetworkPolicy is not a first-match firewall rule list. The empty ingress policy establishes isolation, but another matching policy can add allowed traffic. The source structure should be reviewed as a set.

**Expected:** The explicit matching allow remains effective; there is no ordered deny override.

## Exercise 3: Check peer selector logic

A formatting change can broaden the eligible sources. This is a concrete reason to inspect rendered manifests and test a denied control client rather than trust a policy name.

**Expected:** One peer means conjunction; separate entries mean alternatives.

## Exercise 4: Establish pre-policy controls

The baseline distinguishes policy effects from an already broken service or wrong port. Use bounded requests and retain actual identities rather than copying the synthetic matrix.

**Expected:** Both paths succeed with the expected payload and target receipt.

## Exercise 5: Verify the allowed/denied change

The paired control supports the intended traffic boundary. A policy object with no enforcement or an application outage affecting both clients does not satisfy the contract.

**Expected:** Permitted path succeeds; other path fails within its deadline.

## Exercise 6: State limits and cleanup

The handoff should identify the CNI and tested traffic tuple. Cleanup must preserve unrelated policies and namespace settings, and a finite result should not be generalized into complete multitenant isolation.

**Expected:** Only owned policy resources are cleaned; protocols, hosts and capabilities outside the test remain unclaimed.

## Boundary and troubleshooting review

NetworkPolicy governs supported network behavior under the implementation's semantics. It is not application authentication, Secret authorization or a virtual-machine boundary. Host/node traffic and implementation-specific behavior need separate understanding.

A passed two-client test proves the observed allowed/denied paths, not every possible protocol or source. Report the exact labels, port, direction and target identities. Leave the live row unavailable when the CNI has not been qualified.
