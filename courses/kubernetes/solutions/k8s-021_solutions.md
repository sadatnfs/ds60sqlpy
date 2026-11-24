# k8s-021: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

A NetworkPolicy describes allowed traffic relationships for selected Pods when the cluster networking implementation enforces it. Creating the API object is not evidence that packets are filtered. The course therefore requires a separately qualified policy-capable CNI and before/after client observations for this host lab.

The example isolates ingress to app=hello and then allows TCP 8080 from same-namespace Pods labeled role=lesson-client. Policies are additive: the allowed traffic is the union of applicable allow rules. A deny-all ingress policy plus a matching allow policy does not mean the deny rule overrides the allow. Egress isolation is a separate direction and is not enabled by this ingress-only example.

The normal browser adapter does not admit NetworkPolicy or arbitrary client labels. Its basic hello success cannot establish isolation. This worksheet uses real policy manifests and a synthetic traffic matrix until an exclusive policy-enabled lease supplies the required live capability.

## Exercise 1: Identify destination scope

The policy applies to selected destination Pods in its namespace. It does not automatically isolate all namespace egress or unrelated applications.

**Expected:** app=hello destinations, Ingress only.

**Solution reasoning**

- **Approach:** Read spec.podSelector for the destination and spec.policyTypes for direction, ignoring the from peers.
- **Why it is correct:** podSelector app=hello chooses which Pods the policy isolates, and policyTypes Ingress means only inbound traffic to them is affected.
- **Plausible wrong approach:** Reading the client labels under ingress from as the selected Pods would isolate the callers instead of hello.
- **How to verify:** The answer names app=hello Pods and Ingress only, with no Egress.

## Exercise 2: Explain additive rules

NetworkPolicy is not a first-match firewall rule list. The empty ingress policy establishes isolation, but another matching policy can add allowed traffic. The source structure should be reviewed as a set.

**Expected:** The explicit matching allow remains effective; there is no ordered deny override.

**Solution reasoning**

- **Approach:** List every policy that selects hello and take the union of their allowed sources.
- **Why it is correct:** NetworkPolicies are additive allow lists; once any policy isolates a Pod, traffic is allowed if any selecting policy permits it.
- **Plausible wrong approach:** Treating deny-ingress as a rule that overrides allow-client imagines a priority order the API does not define.
- **How to verify:** The allowed set equals allow-client's sources, and no field orders the policies.

## Exercise 3: Check peer selector logic

A formatting change can broaden the eligible sources. This is a concrete reason to inspect rendered manifests and test a denied control client rather than trust a policy name.

**Expected:** One peer means conjunction; separate entries mean alternatives.

**Solution reasoning**

- **Approach:** Count the list items under from and read each item's selectors together.
- **Why it is correct:** Selectors inside one item must all match, while separate items are alternatives, so the indentation of one dash changes AND to OR.
- **Plausible wrong approach:** Reading two separate items as one combined requirement would predict a deny for traffic that one item alone allows.
- **How to verify:** One item with two selectors is AND, and two items are OR.

## Exercise 4: Establish pre-policy controls

The baseline distinguishes policy effects from an already broken service or wrong port. Use bounded requests and retain actual identities rather than copying the synthetic matrix.

**Expected:** Both paths succeed with the expected payload and target receipt.

**Solution reasoning**

- **Approach:** Send both approved client requests before any policy exists and keep caller, payload and target receipt.
- **Why it is correct:** Without a pre-policy success, a later failure could come from the backend rather than from enforcement.
- **Plausible wrong approach:** Applying the policy first and testing only afterward leaves no control to compare against.
- **How to verify:** Both requests succeed with the expected payload before enforcement.

## Exercise 5: Verify the allowed/denied change

The paired control supports the intended traffic boundary. A policy object with no enforcement or an application outage affecting both clients does not satisfy the contract.

**Expected:** Permitted path succeeds; other path fails within its deadline.

**Solution reasoning**

- **Approach:** Repeat the same two requests with the same callers and deadline after applying the policies.
- **Why it is correct:** With only policy state changed, a new failure on the unpermitted path can be attributed to enforcement by the CNI.
- **Plausible wrong approach:** Testing on a cluster whose CNI does not enforce NetworkPolicy would show both paths succeeding and suggest the policy is wrong.
- **How to verify:** The permitted path succeeds and the other fails within its deadline.

## Exercise 6: State limits and cleanup

The handoff should identify the CNI and tested traffic tuple. Cleanup must preserve unrelated policies and namespace settings, and a finite result should not be generalized into complete multitenant isolation.

**Expected:** Only owned policy resources are cleaned; protocols, hosts and capabilities outside the test remain unclaimed.

**Solution reasoning**

- **Approach:** Record policy and client UIDs and state the protocol and namespace the claim covers.
- **Why it is correct:** The test only exercised the listed callers and port, so the isolation claim cannot extend to other protocols or hosts.
- **Plausible wrong approach:** Writing that hello is isolated from everything generalizes from two requests to all traffic.
- **How to verify:** Cleanup lists only owned UIDs, and the claim states its protocol and namespace.

## Boundary and troubleshooting review

NetworkPolicy governs supported network behavior under the implementation's semantics. It is not application authentication, Secret authorization or a virtual-machine boundary. Host/node traffic and implementation-specific behavior need separate understanding.

A passed two-client test proves the observed allowed/denied paths, not every possible protocol or source. Report the exact labels, port, direction and target identities. Leave the live row unavailable when the CNI has not been qualified.
