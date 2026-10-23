# k8s-031: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

API authorization answers whether an authenticated caller may attempt an action on a resource. Schema validation asks whether the object has a permitted shape. Admission can impose additional conditions on an otherwise authorized, well-formed request before it is persisted. A policy denial is therefore different from an image pull failure in a Pod that was already accepted.

The host-only fixture uses a ValidatingAdmissionPolicy with a CEL expression and a separate binding. CEL is a constrained expression language for evaluating data such as the proposed object. The expression requires every ordinary Deployment container image to equal the preloaded fixture tag. The binding selects only namespaces carrying a host-controlled lesson label and enforces Deny. The learner cannot add that label to unrelated namespaces or install policies.

This is a deliberately small demonstration. It does not validate init containers, image signatures, every workload kind or all security fields, and a mutable tag is not a publisher identity. The normal browser parser already rejects unapproved images locally. A browser refusal cannot prove that the API admission policy ran, so the advanced host test must retain an actual server denial and an allowed control.

## Exercise 1: Map the enforcement chain

The exact server pipeline includes details beyond this sketch, but the evidence distinction is essential. A credential failure, invalid type or local parser refusal should not be counted as a successful test of an admission predicate.

**Expected:** A rejected earlier boundary cannot prove a later policy ran.

## Exercise 2: Inspect policy scope

The binding is what connects this policy to the intended lesson scope. The host should inspect its own namespace identity and label, because a correct expression applied to the wrong scope can still be operationally unsafe.

**Expected:** apps/v1 Deployments on CREATE/UPDATE in the labeled owned namespace only.

## Exercise 3: Evaluate all-container logic

Checking only the first container would leave an obvious gap. This predicate handles every ordinary container in the named field, but it still does not imply coverage of init containers or other workload resource kinds.

**Expected:** True for approved-only and false for the mixed list.

## Exercise 4: Capture a real denial

Holding all other fields constant makes the result attributable to the intended policy condition. A denied request can leave the previous valid revision in place, so readback should distinguish old state from the rejected candidate.

**Expected:** Policy-specific denial and no persisted rejected revision.

## Exercise 5: Restore the positive control

The positive control shows the policy is selective rather than simply blocking every request. Application checks still follow acceptance, because the policy cannot prove scheduling, startup or correct response content.

**Expected:** Allowed request accepted and its application observation recorded separately.

## Exercise 6: Document gaps and teardown

The result should state the exact match scope and trusted host configuration. Cleanup is a host responsibility with object identities and ownership checks, preserving any unrelated cluster policy.

**Expected:** No claim of signature verification or universal workload enforcement.

## Boundary and troubleshooting review

The expression protects only the resource and container list it names. A complete production policy would need a separately reviewed threat model, workload coverage, digest/provenance semantics and rollout strategy. Do not quietly broaden this teaching policy across the cluster.

A failed admission request should not be repaired by disabling safeguards globally. Correct the intended object or report that the requested behavior is outside the lesson. The host removes only its own policy and binding after all scoped evidence is captured.
