# k8s-044: explanatory solutions

Compare after your own attempt or an explicit reveal. These explanations describe the synthetic topology and stated API contracts. They are not fabricated runtime receipts.

## Mechanism review

CIDR notation combines an address with a prefix length, such as 10.244.0.0/16. The prefix describes which leading bits identify the network. A longer prefix describes a smaller address set. CIDR membership is a binary relationship, not a string-prefix test.

Clusters need address planning for nodes, Pods and Services, and may interact with a host LAN, VPN or cloud network. Overlapping ranges can make a destination ambiguous or route traffic to the wrong place. A configuration can be valid YAML while its network plan is unusable in the actual environment.

Pod and Service CIDRs serve different purposes. Pod ranges allocate workload endpoints according to the CNI and cluster design. Service ranges allocate virtual service destinations. A Service IP should not be assumed to appear as an ordinary Pod interface address. Dual-stack adds another family of addresses and routes rather than replacing these distinctions.

Use an IP-address library for membership and overlap reasoning. In a/24 IPv4 network there are 256 numeric addresses, but usable allocations depend on the system’s rules and reservations. Do not turn the arithmetic count into a guaranteed Kubernetes capacity claim.

A routing table chooses a next hop according to destination and policy, commonly preferring the most specific matching prefix. An overlapping VPN route can affect traffic before it reaches a cluster component. Investigate the caller’s route context rather than changing Kubernetes selectors to fix a host routing conflict.

## Exercise 1: Predict Pod-IP membership in the fixture CIDR.

Use network arithmetic rather than text comparison. Membership says nothing yet about whether the address is allocated or reachable.

**Expected:** 10.244.1.7 belongs to 10.244.0.0/16.

## Exercise 2: Compare/16 and/24 address set sizes.

Prefix length counts fixed bits. More fixed bits leave fewer varying address bits.

**Expected:** The/24 is the smaller, more specific network.

## Exercise 3: Build a nonoverlapping synthetic address-plan table.

The plan must include networks outside Kubernetes that the caller traverses. Ignoring the host can leave an otherwise coherent cluster unreachable.

**Expected:** Node, Pod and Service ranges plus host/VPN ranges are compared.

## Exercise 4: Diagnose a VPN route overlapping the Pod range.

Locate the first wrong next hop. Changing a Service selector does not repair the host route decision.

**Expected:** The caller can select an unintended route before cluster delivery.

## Exercise 5: Explain why 256 addresses do not guarantee 256 allocatable endpoints.

Arithmetic cardinality is only one input. The allocator and network design determine actual usable capacity.

**Expected:** Reservation and implementation rules reduce or constrain allocation.

## Exercise 6: Defend an address plan for a second local cluster.

Multiple local clusters still share a host environment. Explicit planning prevents hard-to-diagnose cross-target ambiguity.

**Expected:** Ranges and routes avoid collisions with the first cluster and host networks.
