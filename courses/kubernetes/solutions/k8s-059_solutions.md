# k8s-059: explanatory solutions

Compare after your own attempt or an explicit reveal. These explanations describe the synthetic topology and stated API contracts. They are not fabricated runtime receipts.

## Mechanism review

Egress policy controls selected Pods' outgoing traffic under an enforcing implementation. A deny-by-default design begins by selecting the workloads and then allowing the dependencies they actually require. It can expose hidden dependencies such as DNS, metadata endpoints, package downloads or external APIs.

DNS is itself network traffic. Blocking it can make every named dependency fail even while a direct allowed IP connection works. UDP is common for DNS, but TCP can also be required. The correct DNS target and policy depend on the cluster’s DNS deployment and any node-local cache.

An IP allowlist is not the same as a domain-name policy. External services can change addresses, use shared infrastructure or return several families. The standard NetworkPolicy API does not provide a general hostname allowlist. Implementation extensions must be named and qualified separately.

A policy with policyTypes Egress and an empty egress list isolates selected Pods without permitting outgoing flows through that policy. Additional applicable policies can add allowances. A source egress allowance is not sufficient when the destination is ingress-isolated: the destination must also permit the connection. Replies for a permitted connection are implicitly allowed, while a new reverse connection is evaluated as a new flow. Peer and port rules should be derived from the actual dependency map.

ipBlock represents CIDR-based address ranges with optional exclusions. Address translation can affect which IP an implementation evaluates at a boundary, so test the actual traffic path. Do not promise identical pre-NAT or post-NAT behavior across every plugin and Service combination.

## Exercise 1: Predict the effect of an empty egress list.

Isolation and additive policy semantics still apply. Review every policy selecting the same Pod.

**Expected:** It contributes no allowed outgoing flows for selected Pods.

**Solution reasoning**

- **Approach:** Note that policyTypes includes Egress and the egress list is empty for the selected Pods.
- **Why it is correct:** Once a policy selects Pods for egress, only listed rules allow outgoing traffic, and an empty list allows none.
- **Plausible wrong approach:** Reading an empty list as no restriction gets the meaning backward.
- **How to verify:** The prediction says it contributes no allowed outgoing flows.

## Exercise 2: Include DNS in a dependency map.

A hostname-based app dependency starts with a DNS leg. Ignoring it produces confusing broad failures.

**Expected:** Resolver destination and UDP/TCP requirements are explicit.

**Solution reasoning**

- **Approach:** Add the cluster DNS Pods or Service and port 53 over UDP and TCP to the dependency map.
- **Why it is correct:** Name lookups happen before any request, so blocking DNS breaks every named call.
- **Plausible wrong approach:** Allowing only UDP 53 can break large responses that fall back to TCP.
- **How to verify:** The map names the resolver destination with both UDP and TCP.

## Exercise 3: Design a minimal egress matrix.

Use the actual prepared topology. A generic allow-all DNS rule may target the wrong namespace or resolver deployment.

**Expected:** Only named required internal or external flows are permitted.

**Solution reasoning**

- **Approach:** Permit only the internal and external flows the workload needs, each with destination and port.
- **Why it is correct:** A minimal list limits what a compromised Pod can reach while keeping required calls working.
- **Plausible wrong approach:** Allowing all egress to simplify testing removes the control the policy was meant to add.
- **How to verify:** Every allowed flow in the matrix is named and required.

## Exercise 4: Diagnose named-request failure with direct-IP success.

This contrast is stronger evidence than changing application credentials or opening every port.

**Expected:** Inspect DNS egress and resolver behavior first.

**Solution reasoning**

- **Approach:** Check DNS egress rules and the Pod's resolver before checking the destination.
- **Why it is correct:** If the IP works, the path to the service is open, which points to blocked or failed name resolution.
- **Plausible wrong approach:** Opening egress to the destination again fixes nothing when the lookup fails.
- **How to verify:** The first checks are DNS egress and resolver behavior.

## Exercise 5: Explain why an IP block is not a hostname policy.

Domain-level control needs a named supported extension or proxy design. Do not imply it exists in the standard API.

**Expected:** It matches addresses, which may not be stable or exclusive to one service.

**Solution reasoning**

- **Approach:** Explain that ipBlock matches addresses, not names.
- **Why it is correct:** A hostname can resolve to changing or shared addresses, so a CIDR may miss new ones or include other services.
- **Plausible wrong approach:** Using a CIDR from one lookup as a permanent hostname allow can break later or overreach.
- **How to verify:** The answer says addresses may not be stable or exclusive.

## Exercise 6: Plan an egress qualification after NAT.

Policy evaluation details can differ. Test the actual path before relying on a conceptual address match.

**Expected:** Record implementation, observed addresses and both allowed/denied cases.

**Solution reasoning**

- **Approach:** Record the CNI, the source address observed at the destination and one allowed and one denied case.
- **Why it is correct:** NAT can change the source the external side sees, so observed addresses explain matching results.
- **Plausible wrong approach:** Testing only an allowed destination cannot show the policy denies anything.
- **How to verify:** The record has implementation, observed addresses and both outcomes.
