# k8s-014: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

The beginner capstone assembles a stateless service from a Deployment, a Service and a ConfigMap, then verifies the application through a bounded client Job. Each component solves a different problem:the Deployment maintains replicas, the Service selects and routes, the ConfigMap supplies synthetic data, and the client observes the resulting HTTP contract.

The current browser source is a complete admitted contract-2 resource set. Its one-shot execution can check controller convergence, owned Ready Pod identities, unique Service backends, version response and both configuration-consumption paths. It then removes only recorded owned UIDs. The six-task capstone also requires predictions, error analysis and a reviewable evidence packet, which are not automatically graded by process success.

A stateless fixture has no persistent application data to preserve, but identity and cleanup still matter. A same-name object created by another run is not yours to delete. The capstone includes a controlled selector or task failure so the learner can demonstrate that a wrong mechanism is rejected rather than merely collect a green status.

## Exercise 1: Review the complete desired set

The source graph predicts how data and traffic should flow. It does not supply server-assigned UIDs or prove that controllers acted. Those observations belong in the later receipt.

**Expected:** Two replicas, matching app labels, fixed port chain and both message consumers are identified.

## Exercise 2: Establish controller ownership

A matching label or raw Pod count is insufficient. The capstone needs the controller graph so unrelated resources cannot satisfy the desired replica claim.

**Expected:** Exactly two owned Ready Pod identities for the intended generation.

## Exercise 3: Verify routing and values

The client test closes a different boundary from controller status. It verifies that traffic reaches the expected fixture through the Service and that configuration is visible at the application layer.

**Expected:** UID sets match; version and both message values are exact.

## Exercise 4: Inject one bounded fault

The negative case demonstrates sensitivity to a plausible error. It is useful even when failure is expected, provided the result is not mislabeled as a successful service. Keep runtime phase and cleanup evidence together.

**Expected:** The named check fails within budget and cleanup still targets only owned UIDs.

## Exercise 5: Repair and compare a fresh run

Because the browser cleans every Run, the repaired scenario is a new creation. Comparing the source change and resulting checks explains the mechanism without inventing a stateful transition.

**Expected:** The intended checks pass with new actual resource identities.

## Exercise 6: Hand off acceptance and limits

A good handoff is reproducible and bounded. It should let the reviewer see why a wrong selector failed and why the repaired service passed, while preserving privacy and avoiding unsupported production or recurrence claims.

**Expected:** Source, nonsecret target identity, controller/backend/client/failure/cleanup evidence and unqualified surfaces are explicit.

## Boundary and troubleshooting review

A passed fixture does not establish production capacity, high availability, network policy enforcement or persistence. It proves the observed owned synthetic service contract under the qualified runtime. Written ownership reasoning and the chosen negative case remain part of the learning evidence.

Do not export private kubeconfigs or fabricate cleanup from a missing browser page. If cleanup cannot be proved, retain the private recovery receipt and identify the remaining object rather than deleting all similarly named resources.
