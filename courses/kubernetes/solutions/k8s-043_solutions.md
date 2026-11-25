# k8s-043: explanatory solutions

Attempt each exercise first, then compare ([study guide](../STUDY-GUIDE.md#solutions-and-the-ai-tutor)).

## Mechanism review

An IP address identifies a network destination within a routing context. Kubernetes commonly exposes three distinct address roles. A Pod IP reaches a particular Pod network endpoint. A node IP reaches a machine participating in the cluster. A Service ClusterIP is a virtual destination whose implementation selects eligible service endpoints. These addresses are not interchangeable names for the same object.

A Pod can be replaced and receive a different IP and UID. A Service can keep its identity and virtual address while its backend Pods change. A node can host many Pods, and its address is not automatically the public address of every application on it. The correct destination depends on the caller and the intended traffic path.

The synthetic topology uses Pod 10.244.1.7, node 192.0.2.10 and Service 10.96.0.20. The node address is from documentation space and is never a real target. These values illustrate roles; actual ranges are cluster configuration. A browser on your laptop generally cannot route directly to an arbitrary ClusterIP or Pod IP in a desktop cluster.

The Pod status can report podIP and podIPs, while its spec names the scheduled node. A Service spec can report clusterIP, clusterIPs, type and ports. Node status contains addresses with types such as InternalIP. Read each field in its own object and preserve the object’s UID so an old address is not confused with a replacement.

A Service routes transport traffic to endpoints. It is not a process that has an application socket bound to every virtual address in the ordinary way. The implementation might program kernel rules or eBPF paths. The application process still listens inside a Pod at its target port.

## Exercise 1: Label all three synthetic address roles.

The role comes from the object and routing context, not from guessing based on a familiar private prefix.

**Expected:** One node address, one Pod address and one virtual Service address.

**Solution reasoning**

- **Approach:** Assign each address by the object that reports it: Node status addresses, Pod status podIP and the Service spec clusterIP.
- **Why it is correct:** Each address comes from a different allocator, so its role is fixed by where it is recorded, not by what its digits look like.
- **Plausible wrong approach:** Guessing roles from a familiar private prefix such as 10.x fails because node, Pod and Service ranges can all use private space.
- **How to verify:** Exactly one address is labeled node, one Pod and one virtual Service, each traced to the field that reported it.

## Exercise 2: Predict what can change after Pod replacement.

Clients should discover the intended service rather than pinning a disposable Pod address without a specific reason.

**Expected:** Pod UID and IP can change while the Service remains stable.

**Solution reasoning**

- **Approach:** Compare the Pod's UID and podIP with the Service's clusterIP before and after the Pod is replaced.
- **Why it is correct:** A replacement Pod is a new object with a new UID and usually a new IP, while the Service object and its clusterIP are untouched.
- **Plausible wrong approach:** Hardcoding the old Pod IP in a client works until the first replacement and then sends traffic to an address that may belong to nothing.
- **How to verify:** The prediction lists Pod UID and IP as changeable and the Service clusterIP as stable.

## Exercise 3: Draw the internal request path with both ports.

Port roles are independent of address roles. The application must actually listen at the target endpoint.

**Expected:** Service port 80 maps to Pod listener 8080.

**Solution reasoning**

- **Approach:** Draw the client calling the Service on port 80 and the request arriving at the Pod listener on 8080.
- **Why it is correct:** The Service port is what clients dial, while targetPort names where the container actually listens, and kube-proxy rewrites one to the other.
- **Plausible wrong approach:** Assuming the Pod must also listen on 80 because the Service does would misplace the listener and leave targetPort pointing at nothing.
- **How to verify:** The drawing labels port 80 on the Service side and 8080 on the Pod side.

## Exercise 4: Diagnose a host browser trying a ClusterIP directly.

A valid Service object does not promise host or internet reachability. Use the explicitly provisioned access path.

**Expected:** The host may have no route to that virtual cluster destination.

**Solution reasoning**

- **Approach:** Explain that the ClusterIP exists only in rules programmed on cluster nodes and name the provisioned access path instead.
- **Why it is correct:** kube-proxy or the CNI implements the virtual IP on nodes, so a host outside the cluster usually has no route to it.
- **Plausible wrong approach:** Debugging the Service selector because the browser times out treats a host routing gap as a backend fault.
- **How to verify:** The answer says the host may lack a route and points to the explicitly provisioned access path.

## Exercise 5: Distinguish a node address from a public load-balancer address.

A node can have private addresses only. External publication requires a separate routing and exposure design.

**Expected:** They may be different infrastructure endpoints with different policies.

**Solution reasoning**

- **Approach:** Contrast a node's own address with the address a cloud load balancer publishes.
- **Why it is correct:** Nodes often have only private addresses, and a public load balancer is a separate endpoint with its own routing and firewall rules.
- **Plausible wrong approach:** Assuming a node IP is publicly reachable because a LoadBalancer Service exists merges two endpoints that may have different policies.
- **How to verify:** The answer treats them as different infrastructure endpoints with separate policies.

## Exercise 6: Explain a successful request with a changed backend UID.

Record the actual serving identity when the exercise requires replacement evidence; a 200 response alone cannot identify the process.

**Expected:** Service continuity and backend identity are separate observations.

**Solution reasoning**

- **Approach:** Record the serving Pod UID alongside the response when replacement evidence is required.
- **Why it is correct:** The Service keeps answering across replacements, so a 200 shows Service continuity but not which Pod produced it.
- **Plausible wrong approach:** Treating two identical 200 responses as proof the same Pod served both ignores that the backend can change behind the Service.
- **How to verify:** The record pairs each response with its backend UID, keeping continuity and identity separate.
