# k8s-043: explanatory solutions

Compare after your own attempt or an explicit reveal. These explanations describe the synthetic topology and stated API contracts. They are not fabricated runtime receipts.

## Mechanism review

An IP address identifies a network destination within a routing context. Kubernetes commonly exposes three distinct address roles. A Pod IP reaches a particular Pod network endpoint. A node IP reaches a machine participating in the cluster. A Service ClusterIP is a virtual destination whose implementation selects eligible service endpoints. These addresses are not interchangeable names for the same object.

A Pod can be replaced and receive a different IP and UID. A Service can keep its identity and virtual address while its backend Pods change. A node can host many Pods, and its address is not automatically the public address of every application on it. The correct destination depends on the caller and the intended traffic path.

The synthetic topology uses Pod 10.244.1.7, node 192.0.2.10 and Service 10.96.0.20. The node address is from documentation space and is never a real target. These values illustrate roles; actual ranges are cluster configuration. A browser on your laptop generally cannot route directly to an arbitrary ClusterIP or Pod IP in a desktop cluster.

The Pod status can report podIP and podIPs, while its spec names the scheduled node. A Service spec can report clusterIP, clusterIPs, type and ports. Node status contains addresses with types such as InternalIP. Read each field in its own object and preserve the object’s UID so an old address is not confused with a replacement.

A Service routes transport traffic to endpoints. It is not a process that has an application socket bound to every virtual address in the ordinary way. The implementation might program kernel rules or eBPF paths. The application process still listens inside a Pod at its target port.

## Exercise 1: Label all three synthetic address roles.

The role comes from the object and routing context, not from guessing based on a familiar private prefix.

**Expected:** One node address, one Pod address and one virtual Service address.

## Exercise 2: Predict what can change after Pod replacement.

Clients should discover the intended service rather than pinning a disposable Pod address without a specific reason.

**Expected:** Pod UID and IP can change while the Service remains stable.

## Exercise 3: Draw the internal request path with both ports.

Port roles are independent of address roles. The application must actually listen at the target endpoint.

**Expected:** Service port 80 maps to Pod listener 8080.

## Exercise 4: Diagnose a host browser trying a ClusterIP directly.

A valid Service object does not promise host or internet reachability. Use the explicitly provisioned access path.

**Expected:** The host may have no route to that virtual cluster destination.

## Exercise 5: Distinguish a node address from a public load-balancer address.

A node can have private addresses only. External publication requires a separate routing and exposure design.

**Expected:** They may be different infrastructure endpoints with different policies.

## Exercise 6: Explain a successful request with a changed backend UID.

Record the actual serving identity when the exercise requires replacement evidence; a200 response alone cannot identify the process.

**Expected:** Service continuity and backend identity are separate observations.
