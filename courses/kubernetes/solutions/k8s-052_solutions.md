# k8s-052: explanatory solutions

Compare after your own attempt or an explicit reveal. These explanations describe the synthetic topology and stated API contracts. They are not fabricated runtime receipts.

## Mechanism review

A load balancer distributes traffic among eligible destinations. A Kubernetes Service of type LoadBalancer asks an integrated implementation to provision or configure an external entrypoint. The API object is a request; a controller and supporting infrastructure must exist to fulfill it.

In a cloud, the controller may create provider resources, addresses, listeners and health checks. A local cluster may have no such integration and leave the external address pending. Local load-balancer implementations have their own routing and address-allocation requirements. The course does not install one or incur cloud resources automatically.

Load balancing is not a database replication mechanism, a certificate authority or application authorization. A reachable address can still route to unready nodes, wrong ports or an app that returns errors. Diagnose controller status, infrastructure health and actual request behavior separately.

Inspect Service spec.type, loadBalancerClass when used, traffic policy, ports and status.loadBalancer.ingress. An ingress entry can contain an IP or hostname. Do not assume status arrives immediately or that a returned hostname resolves from every network.

Many implementations use NodePorts, while others can route directly to Pods or use alternate mechanisms. The allocation and routing design is implementation-specific. Changing allocateLoadBalancerNodePorts without knowing the implementation can remove a required path.

## Exercise 1: Predict a LoadBalancer Service on an unsupported local cluster.

The API type needs an implementation. Do not fabricate a public IP or change to an unrelated cluster.

**Expected:** The requested external entrypoint may remain unprovisioned.

## Exercise 2: Name the controller and infrastructure responsibilities.

Kubernetes desired state and provider operations are linked but distinct systems with separate failures.

**Expected:** Reconcile the request and provision actual routing resources.

## Exercise 3: Draw both node-backed and direct-Pod conceptual paths.

Different load balancers use different backend models. Qualification must match the actual installed design.

**Expected:** The implementation choice is explicit rather than assumed.

## Exercise 4: Diagnose assigned address with no successful requests.

A status field is one checkpoint. Continue through the actual request path instead of declaring the service healthy.

**Expected:** Inspect listener, health checks, backend route and app behavior.

## Exercise 5: Explain load-balancer health versus Pod readiness.

A node health check may not prove the intended application response. Correlate the layers.

**Expected:** Infrastructure health and Kubernetes endpoint eligibility can test different things.

## Exercise 6: Plan a local versus cloud qualification.

Cloud provisioning is not a free side effect of reading a tutorial. Keep ownership and cleanup explicit before any live experiment.

For example, a provider quota or controller permission error can prevent address allocation while the internal app remains healthy. Conversely, an allocated address can exist with failing backend health checks. Keep controller reconciliation, provider infrastructure and application evidence in separate rows. This prevents restarting a healthy Pod to repair an unrelated provisioning failure or mistaking a released address for a valid rollback target.

**Expected:** Named implementation, owned resources, cost/cleanup boundary and real request evidence.
