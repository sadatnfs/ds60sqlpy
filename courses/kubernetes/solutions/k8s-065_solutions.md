# k8s-065: explanatory solutions

Attempt each exercise first, then compare ([study guide](../STUDY-GUIDE.md#solutions-and-the-ai-tutor)).

## Mechanism review

A service mesh adds traffic-management, identity or observability capabilities around application communication through a particular implementation. It may use sidecar proxies, node-level components or other designs. It does not remove the underlying need for Pod networking, Service discovery, healthy endpoints and application correctness.

Mutual TLS authenticates both ends of a connection under an identity system. It is not the same as application authorization for a business action. A mesh can establish workload identities while the application still needs to decide whether a caller may read a specific record.

Multi-cluster communication introduces additional discovery, routing, identity and failure-domain boundaries. Overlapping Pod CIDRs, different trust roots, regional latency and partial outages complicate the design. A working single-cluster demo does not qualify a cross-region platform.

Draw the actual data and control planes. A mesh control plane distributes configuration and identity material; proxies or equivalent components handle traffic. Failure of one plane can have different effects from failure of the other. Policies and retries must account for idempotency and retry amplification.

This chapter is design and reading practice. The course does not install a mesh, connect clusters or create cloud networks. Use synthetic diagrams to compare when a mesh capability is justified and when application-level libraries or simpler routing are sufficient.

## Exercise 1: Identify mesh control and data planes.

Their failures and evidence differ. A healthy control process does not prove every proxy has applied current policy.

**Expected:** Configuration/identity distribution versus actual traffic handling.

**Solution reasoning**

- **Approach:** Assign configuration and identity distribution to the control plane and traffic handling to the data plane proxies.
- **Why it is correct:** The control plane pushes config and certificates, while sidecar or node proxies carry requests.
- **Plausible wrong approach:** Expecting the control plane to carry requests misplaces where traffic failures occur.
- **How to verify:** The answer separates distribution from traffic handling.

## Exercise 2: Distinguish mTLS and business authorization.

Keep the policy layers explicit. Encryption and authentication do not replace application access decisions.

**Expected:** Peer identity versus permission for a domain-specific action.

**Solution reasoning**

- **Approach:** Contrast mTLS, which proves which workload is calling, with authorization for a specific business action.
- **Why it is correct:** Knowing the peer's identity does not say whether that peer may perform an operation such as a refund.
- **Plausible wrong approach:** Treating mTLS as full authorization lets any authenticated service call any endpoint.
- **How to verify:** The answer separates peer identity from action permission.

## Exercise 3: Draw a two-cluster request path.

The diagram should expose new failure domains rather than drawing one seamless arrow.

**Expected:** Discovery, inter-cluster route, trust and application hops are named.

**Solution reasoning**

- **Approach:** Draw discovery, the inter-cluster route, trust establishment and the application hop.
- **Why it is correct:** Each hop has its own owner and failure mode, from discovery records to cross-cluster certificates.
- **Plausible wrong approach:** Drawing one arrow between clusters hides the trust and route steps.
- **How to verify:** All four hops are named.

## Exercise 4: Diagnose retry amplification.

Set bounded policies with operation safety in mind. More retries can worsen an overloaded dependency.

**Expected:** Uncoordinated retry budgets multiply attempts and load.

**Solution reasoning**

- **Approach:** Multiply retry counts across each layer that retries to find the worst-case attempts.
- **Why it is correct:** Three layers retrying three times can send 27 attempts for one request, adding load to a struggling backend.
- **Plausible wrong approach:** Adding retries at every layer to improve reliability multiplies load during an outage.
- **How to verify:** The answer shows uncoordinated budgets multiplying attempts.

## Exercise 5: Explain overlapping CIDR risk across clusters.

Cluster-local addresses are not automatically globally unique. Network planning remains necessary.

**Expected:** Address routing can become ambiguous without a deliberate connectivity design.

**Solution reasoning**

- **Approach:** Show that if two clusters share a Pod CIDR, one address can mean two different Pods.
- **Why it is correct:** Routers and proxies cannot tell which cluster an overlapping address belongs to without translation.
- **Plausible wrong approach:** Connecting clusters with default CIDRs assumes ranges are unique when they may match.
- **How to verify:** The answer says routing can become ambiguous without a deliberate design.

## Exercise 6: Defend whether a mesh is justified for a workload.

Choose architecture from requirements. Adding infrastructure is not proof of maturity or reliability.

In the retry example, three means three total attempts at each layer, including the initial attempt. With three client attempts and up to three proxy attempts for each, the upstream can see nine attempts. A setting called retries may instead exclude the initial attempt, so inspect its exact definition. For non-idempotent operations, coordinated budgets alone are insufficient; use an operation identity or an outcome-reconciliation protocol to avoid duplicate effects.

**Expected:** Name required capabilities, operational cost and simpler alternatives.

**Solution reasoning**

- **Approach:** List required capabilities, the operational cost of the mesh and simpler alternatives.
- **Why it is correct:** A mesh adds proxies, certificates and upgrades, which are justified only by capabilities the workload needs.
- **Plausible wrong approach:** Adopting a mesh because it is popular adds cost without a named need.
- **How to verify:** The decision names capabilities, cost and alternatives.
