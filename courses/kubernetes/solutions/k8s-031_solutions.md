# k8s-031: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

API authorization answers whether an authenticated caller may attempt an action on a resource. Schema validation asks whether the object has a permitted shape. Admission can impose additional conditions on an otherwise authorized, well-formed request before it is persisted. A policy denial is therefore different from an image pull failure in a Pod that was already accepted.

The host-only fixture uses a ValidatingAdmissionPolicy with a CEL expression and a separate binding. CEL is a constrained expression language for evaluating data such as the proposed object. The expression requires every ordinary Deployment container image to equal the preloaded fixture tag. The binding selects only namespaces carrying a host-controlled lesson label and enforces Deny. The learner cannot add that label to unrelated namespaces or install policies.

This is a deliberately small demonstration. It does not validate init containers, image signatures, every workload kind or all security fields, and a mutable tag is not a publisher identity. The normal browser parser already rejects unapproved images locally. A browser refusal cannot prove that the API admission policy ran, so the advanced host test must retain an actual server denial and an allowed control.

## Exercise 1: Map the enforcement chain

The exact server pipeline includes details beyond this sketch, but the evidence distinction is essential. A credential failure, invalid type or local parser refusal should not be counted as a successful test of an admission predicate.

**Expected:** A rejected earlier boundary cannot prove a later policy ran.

**Solution reasoning**

- **Approach:** Order authentication, authorization, admission and persistence, and stop at the first step that rejects.
- **Why it is correct:** Admission runs only for requests that were already authenticated and authorized, so an earlier refusal means the policy never evaluated.
- **Plausible wrong approach:** Citing a 403 Forbidden as proof the admission policy works confuses an RBAC denial with a policy denial.
- **How to verify:** The sequence runs in that order and ends at the first rejecting step.

## Exercise 2: Inspect policy scope

The binding is what connects this policy to the intended lesson scope. The host should inspect its own namespace identity and label, because a correct expression applied to the wrong scope can still be operationally unsafe.

**Expected:** apps/v1 Deployments on CREATE/UPDATE in the labeled owned namespace only.

**Solution reasoning**

- **Approach:** Read matchConstraints and the binding namespace selector together and list each matched value.
- **Why it is correct:** The policy matches apps/v1 deployments on CREATE and UPDATE, and the binding narrows it to namespaces carrying the owned label.
- **Plausible wrong approach:** Expecting it to cover Pods created directly ignores that resourceRules name deployments only.
- **How to verify:** The list shows apps, v1, deployments, CREATE, UPDATE and the labeled namespace.

## Exercise 3: Evaluate all-container logic

Checking only the first container would leave an obvious gap. This predicate handles every ordinary container in the named field, but it still does not imply coverage of init containers or other workload resource kinds.

**Expected:** True for approved-only and false for the mixed list.

**Solution reasoning**

- **Approach:** Evaluate the image check one container at a time and combine with all.
- **Why it is correct:** all returns true only when every element satisfies the predicate, so one unapproved image makes the whole expression false.
- **Plausible wrong approach:** Using exists instead of all would accept the mixed list because one approved image is enough.
- **How to verify:** Approved only gives true and the mixed list gives false.

## Exercise 4: Capture a real denial

Holding all other fields constant makes the result attributable to the intended policy condition. A denied request can leave the previous valid revision in place, so readback should distinguish old state from the rejected candidate.

**Expected:** Policy-specific denial and no persisted rejected revision.

**Solution reasoning**

- **Approach:** Change only the image to an unapproved one, submit through the qualified path and read the Deployment back.
- **Why it is correct:** A ValidatingAdmissionPolicy denial stops the request before persistence, so the stored revision stays the same.
- **Plausible wrong approach:** Judging success by a missing new Pod could also come from a failed rollout of an accepted change.
- **How to verify:** The message names the policy, and the readback shows the previous revision.

## Exercise 5: Restore the positive control

The positive control shows the policy is selective rather than simply blocking every request. Application checks still follow acceptance, because the policy cannot prove scheduling, startup or correct response content.

**Expected:** Allowed request accepted and its application observation recorded separately.

**Solution reasoning**

- **Approach:** Submit the approved source through the same path and record acceptance apart from any readiness result.
- **Why it is correct:** A positive control shows the policy admits valid input, so the earlier denial came from the image and not a broken path.
- **Plausible wrong approach:** Treating acceptance as application success skips the separate readiness and client checks.
- **How to verify:** Acceptance is recorded, and readiness or client results appear as separate rows.

## Exercise 6: Document gaps and teardown

The result should state the exact match scope and trusted host configuration. Cleanup is a host responsibility with object identities and ownership checks, preserving any unrelated cluster policy.

**Expected:** No claim of signature verification or universal workload enforcement.

**Solution reasoning**

- **Approach:** Name fields the policy does not inspect, such as image digest signature and securityContext, and delete only host-owned UIDs.
- **Why it is correct:** The expression reads image strings only, so signatures and other workload kinds remain outside its scope.
- **Plausible wrong approach:** Claiming that all workloads are now verified extends the policy to resources and properties it never matched.
- **How to verify:** Two uncovered fields are listed, and teardown names only the policy and binding UIDs.

## Boundary and troubleshooting review

The expression protects only the resource and container list it names. A complete production policy would need a separately reviewed threat model, workload coverage, digest/provenance semantics and rollout strategy. Do not quietly broaden this teaching policy across the cluster.

A failed admission request should not be repaired by disabling safeguards globally. Correct the intended object or report that the requested behavior is outside the lesson. The host removes only its own policy and binding after all scoped evidence is captured.
