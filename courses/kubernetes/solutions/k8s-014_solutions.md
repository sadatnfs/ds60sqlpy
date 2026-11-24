# k8s-014: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

The beginner capstone assembles a stateless service from a Deployment, a Service and a ConfigMap, then verifies the application through a bounded client Job. Each component solves a different problem: the Deployment maintains replicas, the Service selects and routes, the ConfigMap supplies synthetic data, and the client observes the resulting HTTP contract.

The current browser source is a complete admitted contract-2 resource set. Its one-shot execution can check controller convergence, owned Ready Pod identities, unique Service backends, version response and both configuration-consumption paths. It then removes only recorded owned UIDs. The six-task capstone also requires predictions, error analysis and a reviewable evidence packet, which are not automatically graded by process success.

A stateless fixture has no persistent application data to preserve, but identity and cleanup still matter. A same-name object created by another run is not yours to delete. The capstone includes a controlled selector or task failure so the learner can demonstrate that a wrong mechanism is rejected rather than merely collect a green status.

## Exercise 1: Review the complete desired set

The source graph predicts how data and traffic should flow. It does not supply server-assigned UIDs or prove that controllers acted. Those observations belong in the later receipt.

**Expected:** Two replicas, matching app labels, fixed port chain and both message consumers are identified.

**Solution reasoning**

- **Approach:** Add the ConfigMap and its two consumers to the k8s-008 source, then trace every reference with the field that creates it.
- **Why it is correct:** Selector, configMapKeyRef and volume name are lookups by name or label, while ownership only appears later from the controllers.
- **Plausible wrong approach:** Drawing ownerReferences between source objects invents links the YAML cannot contain, because they are written by controllers at runtime.
- **How to verify:** Each arrow carries selector, configMapKeyRef or volume name, and two replicas with matching app labels are identified.

## Exercise 2: Establish controller ownership

A matching label or raw Pod count is insufficient. The capstone needs the controller graph so unrelated resources cannot satisfy the desired replica claim.

**Expected:** Exactly two owned Ready Pod identities for the intended generation.

**Solution reasoning**

- **Approach:** Follow the Run result's ownership chain from Deployment to current ReplicaSet to each Ready Pod.
- **Why it is correct:** Only Pods controlled by the current ReplicaSet count toward this generation's desired replicas.
- **Plausible wrong approach:** Counting all Pods with app=hello could include an old ReplicaSet's Pod or an unrelated one and still show two.
- **How to verify:** Exactly two owned Ready Pod UIDs sit under the current ReplicaSet.

## Exercise 3: Verify routing and values

The client test closes a different boundary from controller status. It verifies that traffic reaches the expected fixture through the Service and that configuration is visible at the application layer.

**Expected:** UID sets match; version and both message values are exact.

**Solution reasoning**

- **Approach:** Compare the endpoint UID set with the owned Ready set, then each response with the fixed version and both message values.
- **Why it is correct:** Matching sets show the Service routes only to this Deployment's Pods, and exact values show the configuration reached both the environment and volume consumers.
- **Plausible wrong approach:** Checking only the version value would pass even if the ConfigMap key were wrong, since version does not depend on the message.
- **How to verify:** UID sets are equal and the version and both message values match the contract exactly.

## Exercise 4: Inject one bounded fault

The negative case demonstrates sensitivity to a plausible error. It is useful even when failure is expected, provided the result is not mislabeled as a successful service. Keep runtime phase and cleanup evidence together.

**Expected:** The named check fails within budget and cleanup still targets only owned UIDs.

**Solution reasoning**

- **Approach:** Pick one admitted fault, such as selector app=wrong, write which check will fail, then Run.
- **Why it is correct:** Each fault breaks one link: a wrong selector empties endpoints, a wrong probe path keeps Pods unready and a failing task fails its Job.
- **Plausible wrong approach:** Running several faults at once makes it impossible to say which change caused the failed check.
- **How to verify:** The failed check matches your written prediction and cleanup lists only this Run's UIDs.

## Exercise 5: Repair and compare a fresh run

Because the browser cleans every Run, the repaired scenario is a new creation. Comparing the source change and resulting checks explains the mechanism without inventing a stateful transition.

**Expected:** The intended checks pass with new actual resource identities.

**Solution reasoning**

- **Approach:** Restore the faulted field and submit a new Run, then compare checks and identities with the failed one.
- **Why it is correct:** The browser cleans up after every Run, so the repaired Run creates fresh objects and is a new observation.
- **Plausible wrong approach:** Describing the repair as patching the earlier Service assumes state that was already deleted.
- **How to verify:** Every UID differs between Runs and the previously failing check now passes.

## Exercise 6: Hand off acceptance and limits

A good handoff is reproducible and bounded. It should let the reviewer see why a wrong selector failed and why the repaired service passed, while preserving privacy and avoiding unsupported production or recurrence claims.

**Expected:** Source, nonsecret target identity, controller/backend/client/failure/cleanup evidence and unqualified surfaces are explicit.

**Solution reasoning**

- **Approach:** Assemble source, target identity without secrets and evidence for each claim, and list the surfaces not qualified.
- **Why it is correct:** A second learner can reproduce the reasoning only when each claim points to evidence in the packet itself.
- **Plausible wrong approach:** Writing production ready or always available adds claims no bounded Run measured.
- **How to verify:** A second learner finds evidence for every claim using the packet alone.

## Boundary and troubleshooting review

A passed fixture does not establish production capacity, high availability, network policy enforcement or persistence. It proves the observed owned synthetic service contract under the qualified runtime. Written ownership reasoning and the chosen negative case remain part of the learning evidence.

Do not export private kubeconfigs or fabricate cleanup from a missing browser page. If cleanup cannot be proved, retain the private recovery receipt and identify the remaining object rather than deleting all similarly named resources.
