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

## Exercise 2: Predict whether a private node is publicly reachable.

Infrastructure routing and firewall policy remain necessary. Service type alone does not publish the host to the internet.

**Expected:** No public route is implied by NodePort allocation.

## Exercise 3: Draw the local-engine NodePort path.

Desktop environments add hops that a cloud-node diagram can omit. Name the actual host arrangement.

**Expected:** Include VM or node-container boundaries when present.

## Exercise 4: Diagnose timeout before traffic reaches the node.

Locate the earliest failing hop. A correct backend cannot answer packets that never reach the node.

**Expected:** Inspect host/VM route and mapping rather than Pod selectors first.

## Exercise 5: Explain the NodePort range as configurable.

Read the prepared cluster configuration before selecting a fixed port. Avoid collisions with existing owned resources.

**Expected:** The common default is not a guaranteed cluster setting.

## Exercise 6: Compare NodePort with a deliberate loopback port-forward.

A temporary developer tunnel can be useful but does not qualify a NodePort or public load-balancer path.

**Expected:** They have different scopes, lifetimes and routing mechanisms.
