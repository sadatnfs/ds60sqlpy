# k8s-042: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

The final capstone is a reviewable release and recovery story. A policy-compliant custom resource expresses intent; a qualified controller creates owned child resources; the application responds correctly; the data contract holds; a bounded incident is diagnosed and repaired; and the owned environment is cleaned without disturbing unrelated resources. No single green status represents that entire chain.

Use the LessonReport API from k8s-029 and the reconciliation contract from k8s-030. The host must supply the exact CRD/controller, admission, metrics, traffic and storage/recovery capabilities used by the selected scenario. The normal browser adapter does not provide them. Begin with the complete offline evidence packet and explicitly mark live gates unavailable until their corresponding capability receipts exist.

The learner acts as both implementer and reviewer: first predict the expected observations, then compare actual evidence, then challenge the weakest conclusion. The capstone is not a license to install arbitrary operators, change cluster policy or choose another context. Privileged actions remain fixed host operations in an exclusive owned lease, with separate receipts and stop conditions.

## Exercise 1: Prepare the capability and ownership packet

The packet prevents execution assumptions from being hidden in prose. A CRD, controller, policy, metrics path or storage driver must actually exist under the declared host contract before its live outcome can be claimed.

**Expected:** Every requested live action has a qualified capability or an explicit unavailable row.

**Solution reasoning**

- **Approach:** Map each requested live action to a capability receipt or an unavailable row, with versions, source hashes and owned identities.
- **Why it is correct:** Every later gate depends on a named capability, so an unlisted one leaves that gate unsupported.
- **Plausible wrong approach:** Assuming the storage and CNI from capstone 2 still apply skips the receipt for this scenario.
- **How to verify:** Every action has a receipt or an unavailable row.

## Exercise 2: Defend desired state and admission

This makes each control interpretable. A local parser rejection is useful but cannot stand in for server policy enforcement, while an accepted custom resource still requires a functioning controller before it produces a workload.

**Expected:** Schema, authorization and admission conclusions remain separate.

**Solution reasoning**

- **Approach:** Record schema, authorization and admission outcomes as three separate rows with evidence.
- **Why it is correct:** Each layer rejects for different reasons, so a single pass or fail hides which control acted.
- **Plausible wrong approach:** Reporting one denial as proof that all three layers work conflates them.
- **How to verify:** Three rows exist, each with its own permitted and denied evidence.

## Exercise 3: Prove owned convergence and release behavior

The joined evidence rules out several false positives, such as stale readiness or a response from the wrong backend. The finite sample remains bounded evidence and does not establish an exact traffic ratio or unlimited reliability.

**Expected:** Current-generation owned resources serve the expected marker through the intended route.

**Solution reasoning**

- **Approach:** Build one table joining parent generation, child owner UID, readiness and application samples.
- **Why it is correct:** Convergence is proven only when current-generation children owned by the parent are Ready and serve the marker.
- **Plausible wrong approach:** Accepting a ready child without checking its owner UID could count a leftover from an earlier parent.
- **How to verify:** Each row links generation, owner UID, readiness and the sampled marker.

## Exercise 4: Investigate one bounded incident

The investigation should show why the repair follows from observations. Restarting or deleting broadly would make it harder to distinguish the cause and could violate the owned scope even if the symptom temporarily disappeared.

**Expected:** Timestamped causal explanation with exact target and cancellation/restore behavior.

**Solution reasoning**

- **Approach:** Inject one fault and timestamp baseline, fault, symptom, repair and post-repair response.
- **Why it is correct:** One fault with ordered timestamps lets the symptom be attributed to it.
- **Plausible wrong approach:** Injecting a second fault mid-investigation makes the causal chain ambiguous.
- **How to verify:** One fault appears, and all five timestamps are present.

## Exercise 5: Measure service and data recovery

The recovery packet must reject a serving application with the wrong restored marker. It should also state the immutable synthetic-data assumptions so the reviewer does not mistake the exercise for a transactional database recovery proof.

**Expected:** Independent service/data gates and recomputable source timestamps/hashes.

**Solution reasoning**

- **Approach:** Apply the stated RTO and RPO definitions and the missing-data negative control.
- **Why it is correct:** Separate service and data gates show when each recovered, and recorded inputs let a reviewer recompute both.
- **Plausible wrong approach:** Reporting only service recovery time hides a failed data gate.
- **How to verify:** Both values recompute from recorded timestamps and hashes, and the negative control fails as expected.

## Exercise 6: Complete cleanup and review limits

The final handoff should make the environment lifecycle auditable and retain only permitted synthetic evidence. A concise limitation statement is part of technical accuracy, because the tested platform slice is smaller than a production Kubernetes reliability or security guarantee.

**Expected:** No unrelated resources removed; missing or failed gates remain visible.

**Solution reasoning**

- **Approach:** Collect cleanup receipts with UIDs and keep failed or unknown gates in the review.
- **Why it is correct:** UID-aware cleanup removes only owned resources, and visible failures keep the review honest.
- **Plausible wrong approach:** Removing failed rows from the final report makes the release look fully qualified.
- **How to verify:** Every cleanup row has a UID, and failed or unknown rows remain.

## Boundary and troubleshooting review

Cleanup removes only resources owned by the lease and recorded operation, using UID-aware checks. Retained claims or backups need an explicit policy and protected location. The host releases its exclusive cluster only after finalizers, finite Jobs and data-retention decisions are resolved. A cleanup failure is an outcome to report, not a line to omit.

The final review distinguishes source correctness, offline examples, API acceptance, controller convergence, application/data behavior and lifecycle cleanup. It states the exact versions, architecture and finite observations. A small synthetic capstone does not prove production HA, arbitrary-code isolation, exactly-once external side effects or reliable recurring operation.

A reviewer should be able to point to the evidence for every claimed gate and identify every unavailable capability. That is the practical meaning of a defensible platform change: the conclusion is as specific as the measurements that support it.
