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

## Exercise 2: Include DNS in a dependency map.

A hostname-based app dependency starts with a DNS leg. Ignoring it produces confusing broad failures.

**Expected:** Resolver destination and UDP/TCP requirements are explicit.

## Exercise 3: Design a minimal egress matrix.

Use the actual prepared topology. A generic allow-all DNS rule may target the wrong namespace or resolver deployment.

**Expected:** Only named required internal or external flows are permitted.

## Exercise 4: Diagnose named-request failure with direct-IP success.

This contrast is stronger evidence than changing application credentials or opening every port.

**Expected:** Inspect DNS egress and resolver behavior first.

## Exercise 5: Explain why an IP block is not a hostname policy.

Domain-level control needs a named supported extension or proxy design. Do not imply it exists in the standard API.

**Expected:** It matches addresses, which may not be stable or exclusive to one service.

## Exercise 6: Plan an egress qualification after NAT.

Policy evaluation details can differ. Test the actual path before relying on a conceptual address match.

**Expected:** Record implementation, observed addresses and both allowed/denied cases.
