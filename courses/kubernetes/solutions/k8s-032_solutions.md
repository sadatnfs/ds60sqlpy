# k8s-032: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

A PodDisruptionBudget, abbreviated PDB, constrains supported voluntary evictions of a selected application. It helps coordinate maintenance with the application's available replicas. It does not stop a machine from failing, guarantee scheduling capacity or make a directly deleted Pod survive. The distinction matters because the same observed lost replica can result from very different control paths.

Our example selects app=hello and sets minAvailable 1 while the Deployment desires two replicas. In a simplified healthy snapshot with both Pods available, one voluntary disruption can fit the budget. If only one is healthy, another disruption does not fit. The API status and eviction decision are authoritative for the actual moment, because readiness and in-progress disruptions can change between observations.

The normal browser run does not drain Nodes or issue learner-controlled eviction requests. This advanced lab needs an exclusive multi-node lease and a host operation restricted to one owned worker Node. The application remains namespaced, but Node maintenance is a separate host-level capability with a deadline, cancellation and restoration plan.

## Exercise 1: Verify selector scope

A budget label should match the application it protects. Including an unrelated healthy Pod could make the arithmetic look safer than the target application really is, while selecting none can leave the intended workload unprotected.

**Expected:** Exactly the two hello Pods contribute to this example.

**Solution reasoning**

- **Approach:** Apply app=hello to each of the three Pods' labels.
- **Why it is correct:** A PodDisruptionBudget counts only Pods its selector matches, so the unrelated Pod has no effect on the budget.
- **Plausible wrong approach:** Counting all three Pods in the namespace would overstate healthy Pods and allow an eviction the budget should block.
- **How to verify:** Exactly the two hello Pods are selected.

## Exercise 2: Predict healthy-count changes

Negative capacity is represented as no allowed disruptions. The live status can include additional controller bookkeeping, so this calculation is a prediction to compare with observations rather than an authorization token.

**Expected:** Potential disruptions 1, 0, 0 in the simplified model.

**Solution reasoning**

- **Approach:** Subtract minAvailable 1 from healthy counts 2, 1 and 0 and floor at zero.
- **Why it is correct:** Allowed disruptions are the healthy Pods above the minimum, which can never be negative.
- **Plausible wrong approach:** Reporting minus 1 for zero healthy Pods suggests a debt the API does not track.
- **How to verify:** The results are 1, 0 and 0.

## Exercise 3: Capture a denied eviction

The refusal demonstrates why the budget exists. Preserve the reason and state, then repair missing readiness or capacity if that is the actual problem. Bypassing the API would invalidate the maintenance exercise.

**Expected:** Denial is tied to the intended PDB and Pod UID.

**Solution reasoning**

- **Approach:** Call the Eviction API with one selected healthy Pod and keep the response and the Pod's UID.
- **Why it is correct:** With allowed disruptions 0, the API server refuses the eviction with 429 and names the blocking budget.
- **Plausible wrong approach:** Using kubectl delete pod to test the budget bypasses the Eviction API, and the PDB does not block it.
- **How to verify:** A 429 names the intended PDB, and the Pod UID is unchanged.

## Exercise 4: Observe a permitted maintenance path

The evidence should include before/after Pod identities and selected Node identity. A replacement that remains Pending means the maintenance goal is not complete, even if the initial eviction was legitimate.

**Expected:** Allowed disruption, replacement readiness and finite application success are recorded.

**Solution reasoning**

- **Approach:** With two healthy replicas, request one owned eviction and track the replacement.
- **Why it is correct:** Allowed disruptions are 1, so one eviction succeeds and the Deployment creates a replacement that must become Ready.
- **Plausible wrong approach:** Stopping at the successful eviction ignores whether capacity returned for clients.
- **How to verify:** The record shows the evicted UID, the replacement UID with Ready time and one successful request.

## Exercise 5: Diagnose unavailable replacement capacity

PDBs cannot create spare resources. The appropriate repair depends on the observed constraint and the qualified host environment. Increasing replicas repeatedly without addressing the constraint may only add Pending Pods.

**Expected:** A specific scheduling/storage cause is named without weakening unrelated policy.

**Solution reasoning**

- **Approach:** Read the Pending Pod's FailedScheduling event and name the single reported condition.
- **Why it is correct:** The scheduler states why no node fit, such as insufficient CPU, unmatched affinity or a volume zone conflict.
- **Plausible wrong approach:** Lowering the PDB minimum to unblock maintenance does nothing for a Pod that cannot be scheduled.
- **How to verify:** One named condition from the event explains the Pending state.

## Exercise 6: State protection limits and restore

The final review should explain what the PDB enforced and what redundancy, placement and storage would need to handle separately. Exact owned cleanup and Node restoration remain part of the maintenance contract.

**Expected:** Only the tested voluntary path is claimed; owned Node state is restored.

**Solution reasoning**

- **Approach:** Limit the claim to voluntary eviction and set spec.unschedulable back to its recorded value.
- **Why it is correct:** A PDB only governs the Eviction API, so direct deletion and node failure are outside what was tested.
- **Plausible wrong approach:** Saying the budget guarantees one replica always ignores node loss, which no PDB prevents.
- **How to verify:** The claim names voluntary eviction only, and the node's unschedulable field matches the original.

## Boundary and troubleshooting review

A blocked eviction is useful evidence of a protected boundary, not an invitation to delete the Pod directly. Record the budget, selected Pod UID, readiness and response reason. A successful eviction is also not enough: replacement readiness and application behavior must satisfy the end-to-end maintenance goal.

This small kind rehearsal does not establish production high availability, zone failure tolerance or durable storage resilience. Report the specific voluntary maintenance path, finite observations and untested failure modes.
