# k8s-032: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

A PodDisruptionBudget, abbreviated PDB, constrains supported voluntary evictions of a selected application. It helps coordinate maintenance with the application's available replicas. It does not stop a machine from failing, guarantee scheduling capacity or make a directly deleted Pod survive. The distinction matters because the same observed lost replica can result from very different control paths.

Our example selects app=hello and sets minAvailable1 while the Deployment desires two replicas. In a simplified healthy snapshot with both Pods available, one voluntary disruption can fit the budget. If only one is healthy, another disruption does not fit. The API status and eviction decision are authoritative for the actual moment, because readiness and in-progress disruptions can change between observations.

The normal browser run does not drain Nodes or issue learner-controlled eviction requests. This advanced lab needs an exclusive multi-node lease and a host operation restricted to one owned worker Node. The application remains namespaced, but Node maintenance is a separate host-level capability with a deadline, cancellation and restoration plan.

## Exercise 1: Verify selector scope

A budget label should match the application it protects. Including an unrelated healthy Pod could make the arithmetic look safer than the target application really is, while selecting none can leave the intended workload unprotected.

**Expected:** Exactly the two hello Pods contribute to this example.

## Exercise 2: Predict healthy-count changes

Negative capacity is represented as no allowed disruptions. The live status can include additional controller bookkeeping, so this calculation is a prediction to compare with observations rather than an authorization token.

**Expected:** Potential disruptions1, 0, 0 in the simplified model.

## Exercise 3: Capture a denied eviction

The refusal demonstrates why the budget exists. Preserve the reason and state, then repair missing readiness or capacity if that is the actual problem. Bypassing the API would invalidate the maintenance exercise.

**Expected:** Denial is tied to the intended PDB and Pod UID.

## Exercise 4: Observe a permitted maintenance path

The evidence should include before/after Pod identities and selected Node identity. A replacement that remains Pending means the maintenance goal is not complete, even if the initial eviction was legitimate.

**Expected:** Allowed disruption, replacement readiness and finite application success are recorded.

## Exercise 5: Diagnose unavailable replacement capacity

PDBs cannot create spare resources. The appropriate repair depends on the observed constraint and the qualified host environment. Increasing replicas repeatedly without addressing the constraint may only add Pending Pods.

**Expected:** A specific scheduling/storage cause is named without weakening unrelated policy.

## Exercise 6: State protection limits and restore

The final review should explain what the PDB enforced and what redundancy, placement and storage would need to handle separately. Exact owned cleanup and Node restoration remain part of the maintenance contract.

**Expected:** Only the tested voluntary path is claimed; owned Node state is restored.

## Boundary and troubleshooting review

A blocked eviction is useful evidence of a protected boundary, not an invitation to delete the Pod directly. Record the budget, selected Pod UID, readiness and response reason. A successful eviction is also not enough: replacement readiness and application behavior must satisfy the end-to-end maintenance goal.

This small kind rehearsal does not establish production high availability, zone failure tolerance or durable storage resilience. Report the specific voluntary maintenance path, finite observations and untested failure modes.
