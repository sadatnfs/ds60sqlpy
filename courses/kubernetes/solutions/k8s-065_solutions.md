# k8s-065: explanatory solutions

Compare after your own attempt or an explicit reveal. These explanations describe the synthetic topology and stated API contracts. They are not fabricated runtime receipts.

## Mechanism review

A service mesh adds traffic-management, identity or observability capabilities around application communication through a particular implementation. It may use sidecar proxies, node-level components or other designs. It does not remove the underlying need for Pod networking, Service discovery, healthy endpoints and application correctness.

Mutual TLS authenticates both ends of a connection under an identity system. It is not the same as application authorization for a business action. A mesh can establish workload identities while the application still needs to decide whether a caller may read a specific record.

Multi-cluster communication introduces additional discovery, routing, identity and failure-domain boundaries. Overlapping Pod CIDRs, different trust roots, regional latency and partial outages complicate the design. A working single-cluster demo does not qualify a cross-region platform.

Draw the actual data and control planes. A mesh control plane distributes configuration and identity material; proxies or equivalent components handle traffic. Failure of one plane can have different effects from failure of the other. Policies and retries must account for idempotency and retry amplification.

This chapter is design and reading practice. The course does not install a mesh, connect clusters or create cloud networks. Use synthetic diagrams to compare when a mesh capability is justified and when application-level libraries or simpler routing are sufficient.

## Exercise 1: Identify mesh control and data planes.

Their failures and evidence differ. A healthy control process does not prove every proxy has applied current policy.

**Expected:** Configuration/identity distribution versus actual traffic handling.

## Exercise 2: Distinguish mTLS and business authorization.

Keep the policy layers explicit. Encryption and authentication do not replace application access decisions.

**Expected:** Peer identity versus permission for a domain-specific action.

## Exercise 3: Draw a two-cluster request path.

The diagram should expose new failure domains rather than drawing one seamless arrow.

**Expected:** Discovery, inter-cluster route, trust and application hops are named.

## Exercise 4: Diagnose retry amplification.

Set bounded policies with operation safety in mind. More retries can worsen an overloaded dependency.

**Expected:** Uncoordinated retry budgets multiply attempts and load.

## Exercise 5: Explain overlapping CIDR risk across clusters.

Cluster-local addresses are not automatically globally unique. Network planning remains necessary.

**Expected:** Address routing can become ambiguous without a deliberate connectivity design.

## Exercise 6: Defend whether a mesh is justified for a workload.

Choose architecture from requirements. Adding infrastructure is not proof of maturity or reliability.

In the retry example, three means three total attempts at each layer, including the initial attempt. With three client attempts and up to three proxy attempts for each, the upstream can see nine attempts. A setting called retries may instead exclude the initial attempt, so inspect its exact definition. For non-idempotent operations, coordinated budgets alone are insufficient; use an operation identity or an outcome-reconciliation protocol to avoid duplicate effects.

**Expected:** Name required capabilities, operational cost and simpler alternatives.
