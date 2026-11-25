# k8s-044: explanatory solutions

Attempt each exercise first, then compare ([study guide](../STUDY-GUIDE.md#solutions-and-the-ai-tutor)).

## Mechanism review

CIDR notation combines an address with a prefix length, such as 10.244.0.0/16. The prefix describes which leading bits identify the network. A longer prefix describes a smaller address set. CIDR membership is a binary relationship, not a string-prefix test.

Clusters need address planning for nodes, Pods and Services, and may interact with a host LAN, VPN or cloud network. Overlapping ranges can make a destination ambiguous or route traffic to the wrong place. A configuration can be valid YAML while its network plan is unusable in the actual environment.

Pod and Service CIDRs serve different purposes. Pod ranges allocate workload endpoints according to the CNI and cluster design. Service ranges allocate virtual service destinations. A Service IP should not be assumed to appear as an ordinary Pod interface address. Dual-stack adds another family of addresses and routes rather than replacing these distinctions.

Use an IP-address library for membership and overlap reasoning. In a/24 IPv4 network there are 256 numeric addresses, but usable allocations depend on the system’s rules and reservations. Do not turn the arithmetic count into a guaranteed Kubernetes capacity claim.

A routing table chooses a next hop according to destination and policy, commonly preferring the most specific matching prefix. An overlapping VPN route can affect traffic before it reaches a cluster component. Investigate the caller’s route context rather than changing Kubernetes selectors to fix a host routing conflict.

## Exercise 1: Predict Pod-IP membership in the fixture CIDR.

Use network arithmetic rather than text comparison. Membership says nothing yet about whether the address is allocated or reachable.

**Expected:** 10.244.1.7 belongs to 10.244.0.0/16.

**Solution reasoning**

- **Approach:** Apply the /16 mask to 10.244.1.7 and compare the network bits with 10.244.0.0.
- **Why it is correct:** A /16 fixes the first two octets, and 10.244 matches, so the address is inside the range regardless of the last two octets.
- **Plausible wrong approach:** Comparing strings, such as checking that both start with 10.244.0, would wrongly reject 10.244.1.7.
- **How to verify:** Membership is true, with no claim yet that the address is allocated or reachable.

## Exercise 2: Compare/16 and/24 address set sizes.

Prefix length counts fixed bits. More fixed bits leave fewer varying address bits.

**Expected:** The/24 is the smaller, more specific network.

**Solution reasoning**

- **Approach:** Count varying bits for each prefix length: 16 for /16 and 8 for /24.
- **Why it is correct:** More fixed prefix bits leave fewer host bits, so a /24 holds 256 addresses and a /16 holds 65536.
- **Plausible wrong approach:** Reading the larger number 24 as the larger network reverses the relationship.
- **How to verify:** The /24 is identified as the smaller, more specific network.

## Exercise 3: Build a nonoverlapping synthetic address-plan table.

The plan must include networks outside Kubernetes that the caller traverses. Ignoring the host can leave an otherwise coherent cluster unreachable.

**Expected:** Node, Pod and Service ranges plus host/VPN ranges are compared.

**Solution reasoning**

- **Approach:** List node, Pod and Service ranges together with host and VPN ranges, and check each pair for overlap.
- **Why it is correct:** A caller routes through its own host and VPN networks first, so an overlap there can capture traffic before it reaches the cluster.
- **Plausible wrong approach:** Checking only the three cluster ranges against each other misses a VPN range that shadows the Pod CIDR.
- **How to verify:** Every pair in the table, including host and VPN ranges, is shown not to overlap.

## Exercise 4: Diagnose a VPN route overlapping the Pod range.

Locate the first wrong next hop. Changing a Service selector does not repair the host route decision.

**Expected:** The caller can select an unintended route before cluster delivery.

**Solution reasoning**

- **Approach:** Trace the caller's route lookup for a Pod address and find the first hop that leaves the intended path.
- **Why it is correct:** When a VPN route overlaps the Pod range, the host may prefer it, so packets leave toward the VPN before the cluster sees them.
- **Plausible wrong approach:** Editing the Service selector cannot change which route the host chose for the destination address.
- **How to verify:** The answer names the overlapping VPN route as the first wrong next hop.

## Exercise 5: Explain why 256 addresses do not guarantee 256 allocatable endpoints.

Arithmetic cardinality is only one input. The allocator and network design determine actual usable capacity.

**Expected:** Reservation and implementation rules reduce or constrain allocation.

**Solution reasoning**

- **Approach:** Separate the address count of a /24 from how many addresses the allocator will hand out.
- **Why it is correct:** Network and broadcast addresses, gateway reservations and per-node block sizes reduce or partition what can be assigned to Pods.
- **Plausible wrong approach:** Planning for 256 Pods per /24 assumes every address is assignable, which no implementation guarantees.
- **How to verify:** The answer names at least one reservation or allocation rule that reduces usable endpoints.

## Exercise 6: Defend an address plan for a second local cluster.

Multiple local clusters still share a host environment. Explicit planning prevents hard-to-diagnose cross-target ambiguity.

**Expected:** Ranges and routes avoid collisions with the first cluster and host networks.

**Solution reasoning**

- **Approach:** Choose node, Pod and Service ranges for the second cluster that avoid the first cluster's and the host's ranges.
- **Why it is correct:** Both clusters share one host routing table, so overlapping ranges make destinations ambiguous on that host.
- **Plausible wrong approach:** Copying the first cluster's defaults for convenience creates identical ranges and routes that conflict.
- **How to verify:** Every range in the new plan is distinct from the first cluster and the host networks.
