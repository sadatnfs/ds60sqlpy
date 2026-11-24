# k8s-051: explanatory solutions

Compare after your own attempt or an explicit reveal. These explanations describe the synthetic topology and stated API contracts. They are not fabricated runtime receipts.

## Mechanism review

A NodePort Service allocates a port from the cluster’s configured NodePort range and makes the Service available through relevant node addresses according to the data-plane configuration. It usually also has a ClusterIP. A client addresses nodeIP:nodePort, and traffic is directed to an eligible backend.

A node address must actually be reachable from the client. Desktop cluster nodes may be containers or VMs behind additional network boundaries. A valid NodePort allocation does not automatically open a host firewall, publish a VM port or create an internet route. Local and cloud setups therefore have different external paths.

The commonly seen range 30000 through 32767 is a default, not a universal constant. Explicit allocations must fit the configured range and avoid collisions. Do not expose a teaching service publicly just to make a diagram seem more realistic.

Read port as the ClusterIP-facing Service port, targetPort as the Pod listener and nodePort as the node-facing port. The application still listens at its target endpoint. externalTrafficPolicy can affect endpoint selection and source address behavior, covered in a later chapter.

The example uses nodePort 30080 only in a manual fixture. The ordinary classroom adapter does not admit this wider networking operation. A local kind setup needs deliberately prepared port mappings or another supported access route before host-browser acceptance is possible.

## Exercise 1: Label port, targetPort and nodePort.

A request must use the port appropriate to its caller and destination address.

**Expected:** 80, 8080 and 30080 serve distinct path positions.

**Solution reasoning**

- **Approach:** Map port to the ClusterIP listener, targetPort to the container listener and nodePort to the port opened on every node.
- **Why it is correct:** Each field sits at a different hop: 80 on the Service, 8080 in the Pod and 30080 on the node.
- **Plausible wrong approach:** Setting all three to the same number hides which hop each one controls and makes faults hard to place.
- **How to verify:** 80, 8080 and 30080 are each tied to their own position in the path.

## Exercise 2: Predict whether a private node is publicly reachable.

Infrastructure routing and firewall policy remain necessary. Service type alone does not publish the host to the internet.

**Expected:** No public route is implied by NodePort allocation.

**Solution reasoning**

- **Approach:** Check whether any public route reaches the node's address before predicting reachability.
- **Why it is correct:** NodePort only opens a port on node addresses; if those are private, no public client can route to them.
- **Plausible wrong approach:** Assuming that allocating a nodePort makes the Service public skips the network the client must cross.
- **How to verify:** The prediction says no public route is implied.

## Exercise 3: Draw the local-engine NodePort path.

Desktop environments add hops that a cloud-node diagram can omit. Name the actual host arrangement.

**Expected:** Include VM or node-container boundaries when present.

**Solution reasoning**

- **Approach:** Draw the host, any VM or node container, the node port, kube-proxy forwarding and the Pod listener.
- **Why it is correct:** Local engines often run nodes inside a VM or container, which adds a boundary the host must route or map into.
- **Plausible wrong approach:** Drawing the host directly reaching the nodePort ignores that boundary and its port mapping.
- **How to verify:** The drawing includes the VM or node-container boundary when the environment has one.

## Exercise 4: Diagnose timeout before traffic reaches the node.

Locate the earliest failing hop. A correct backend cannot answer packets that never reach the node.

**Expected:** Inspect host/VM route and mapping rather than Pod selectors first.

**Solution reasoning**

- **Approach:** Test whether the host can reach the node address and whether any port mapping exists before checking selectors.
- **Why it is correct:** A timeout before the node means the packet never reached kube-proxy, so the Service and Pods were never involved.
- **Plausible wrong approach:** Editing Pod selectors cannot fix traffic that never arrives at the node.
- **How to verify:** The first checks are the host or VM route and the port mapping.

## Exercise 5: Explain the NodePort range as configurable.

Read the prepared cluster configuration before selecting a fixed port. Avoid collisions with existing owned resources.

**Expected:** The common default is not a guaranteed cluster setting.

**Solution reasoning**

- **Approach:** Read the API server's service node port range setting instead of assuming 30000 to 32767.
- **Why it is correct:** That range is the common default but is set per cluster through an API server flag.
- **Plausible wrong approach:** Hardcoding a nodePort from the default range can be rejected on a cluster with a different range.
- **How to verify:** The answer calls the range configurable and the default an example.

## Exercise 6: Compare NodePort with a deliberate loopback port-forward.

A temporary developer tunnel can be useful but does not qualify a NodePort or public load-balancer path.

**Expected:** They have different scopes, lifetimes and routing mechanisms.

**Solution reasoning**

- **Approach:** Contrast a cluster-wide NodePort with a kubectl port-forward bound to 127.0.0.1 on one machine.
- **Why it is correct:** NodePort persists on every node through kube-proxy, while port-forward is a client session tunneled through the API server.
- **Plausible wrong approach:** Treating them as interchangeable leads to sharing a port-forward address that only works on the local machine.
- **How to verify:** The comparison covers scope, lifetime and routing mechanism.
