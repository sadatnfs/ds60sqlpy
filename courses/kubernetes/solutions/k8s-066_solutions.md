# k8s-066: explanatory solutions

Attempt each exercise first, then compare ([study guide](../STUDY-GUIDE.md#solutions-and-the-ai-tutor)).

## Mechanism review

The final networking project asks you to explain one complete application path and its failure boundaries. The application has a Deployment, an internal Service, a deliberately prepared external routing layer, TLS where the chosen lab supports it, and a narrow network policy. Every capability must be named rather than assumed.

Start with the synthetic fixture and produce a design packet even when no advanced cluster is available. A live extension requires an explicitly owned target, installed controller support, an enforcing network implementation and a reviewed resource ledger. A source-only design is valuable, but it must not be labeled as an executed production deployment.

The strongest learning outcome is independent diagnosis. You should be able to trace a request, identify a wrong selector or port, distinguish readiness from process state, explain public versus internal addresses, and recover from one controlled failure while preserving data and cleanup ownership.

Build an acceptance matrix across source validation, API admission, controller conditions, endpoint identity, internal request, external request, allowed/denied policy flows, rollout revision and cleanup. Mark unavailable capabilities explicitly. No row is automatically implied by another.

Use the same source and object identities throughout a run. Record a fresh response from the intended revision after a repair. For stateful extensions, add independent data recovery evidence rather than assuming network success preserves records. The capstone is a bounded learning project, not a certificate of universal Kubernetes expertise.

## Exercise 1: Predict the entire request path with address and port roles.

A complete path distinguishes node, Pod, Service and public entrypoint addresses. Do not collapse them into one generic IP.

**Expected:** Every hop names its caller, destination and responsible component.

**Solution reasoning**

- **Approach:** Name the caller, destination address and port and responsible component at every hop.
- **Why it is correct:** Each hop can rewrite addresses or ports, so naming them shows where a mismatch would occur.
- **Plausible wrong approach:** Describing the path as client to app hides the Service, proxy and Pod hops.
- **How to verify:** Every hop has caller, destination and component.

## Exercise 2: Classify available and unavailable lab capabilities.

An honest capability inventory prevents fake runtime claims and accidental installation or cloud provisioning.

**Expected:** Controllers, policy enforcement, dual-stack and external routing are explicit.

**Solution reasoning**

- **Approach:** Mark which controllers, policy enforcement, dual-stack support and external routing the lab really has.
- **Why it is correct:** Lessons can only verify capabilities that are present, so missing ones must be labeled.
- **Plausible wrong approach:** Assuming a LoadBalancer or policy enforcer exists leads to claims nothing tested.
- **How to verify:** Each capability is marked available or unavailable.

## Exercise 3: Produce a complete architecture and acceptance packet.

The packet should be usable by another learner with the documented prepared environment, without ambient credentials or hidden state.

**Expected:** Diagram, manifests, ownership ledger, checks and limitations align.

**Solution reasoning**

- **Approach:** Assemble the diagram, manifests, ownership ledger, checks and limitations so they agree.
- **Why it is correct:** Each part must describe the same resources and ports, or the packet contradicts itself.
- **Plausible wrong approach:** Updating manifests without the diagram leaves reviewers checking a different system.
- **How to verify:** The parts are consistent with each other.

## Exercise 4: Diagnose and repair the single target-port fault.

Preserve the failure and keep other fields unchanged. This establishes causality more clearly than recreating every resource.

**Expected:** The first incorrect mapping is found and a fresh request verifies repair.

**Solution reasoning**

- **Approach:** Walk the path until the Service targetPort no longer matches the container listener, then fix that field.
- **Why it is correct:** The first incorrect mapping is the fault, and a fresh request after the fix proves repair.
- **Plausible wrong approach:** Changing the container port and the Service together can hide which side was wrong.
- **How to verify:** The fix touches one field, and a new request succeeds.

## Exercise 5: Verify isolation with both positive and negative flows.

A policy object existing or one successful request cannot establish isolation. Keep the implementation and caller identities in the record.

**Expected:** Allowed traffic succeeds and the denied owned case fails under an enforcing CNI.

**Solution reasoning**

- **Approach:** Run one flow the policy allows and one owned flow it denies, under a named enforcing CNI.
- **Why it is correct:** Only the denied result shows enforcement, since allowed traffic also passes without any policy.
- **Plausible wrong approach:** Testing only the allowed flow proves nothing on a CNI that ignores policies.
- **How to verify:** The allowed flow succeeds and the denied flow fails.

## Exercise 6: Teach the system and defend its evidence limits.

Independent understanding includes recognizing what remains unqualified. A good operator can stop at a missing capability without inventing success or widening authority.

**Expected:** Explain mechanisms, current results, untested platforms and scoped cleanup.

**Solution reasoning**

- **Approach:** Explain mechanisms, present current results, list untested platforms and describe scoped cleanup.
- **Why it is correct:** Clear limits let readers know which claims are proven here and which still need testing.
- **Plausible wrong approach:** Presenting local lab results as valid for every cloud platform overclaims.
- **How to verify:** The explanation covers mechanisms, results, untested platforms and cleanup.
