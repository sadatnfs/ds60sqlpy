# k8s-066: explanatory solutions

Compare after your own attempt or an explicit reveal. These explanations describe the synthetic topology and stated API contracts. They are not fabricated runtime receipts.

## Mechanism review

The final networking project asks you to explain one complete application path and its failure boundaries. The application has a Deployment, an internal Service, a deliberately prepared external routing layer, TLS where the chosen lab supports it, and a narrow network policy. Every capability must be named rather than assumed.

Start with the synthetic fixture and produce a design packet even when no advanced cluster is available. A live extension requires an explicitly owned target, installed controller support, an enforcing network implementation and a reviewed resource ledger. A source-only design is valuable, but it must not be labeled as an executed production deployment.

The strongest learning outcome is independent diagnosis. You should be able to trace a request, identify a wrong selector or port, distinguish readiness from process state, explain public versus internal addresses, and recover from one controlled failure while preserving data and cleanup ownership.

Build an acceptance matrix across source validation, API admission, controller conditions, endpoint identity, internal request, external request, allowed/denied policy flows, rollout revision and cleanup. Mark unavailable capabilities explicitly. No row is automatically implied by another.

Use the same source and object identities throughout a run. Record a fresh response from the intended revision after a repair. For stateful extensions, add independent data recovery evidence rather than assuming network success preserves records. The capstone is a bounded learning project, not a certificate of universal Kubernetes expertise.

## Exercise 1: Predict the entire request path with address and port roles.

A complete path distinguishes node, Pod, Service and public entrypoint addresses. Do not collapse them into one generic IP.

**Expected:** Every hop names its caller, destination and responsible component.

## Exercise 2: Classify available and unavailable lab capabilities.

An honest capability inventory prevents fake runtime claims and accidental installation or cloud provisioning.

**Expected:** Controllers, policy enforcement, dual-stack and external routing are explicit.

## Exercise 3: Produce a complete architecture and acceptance packet.

The packet should be usable by another learner with the documented prepared environment, without ambient credentials or hidden state.

**Expected:** Diagram, manifests, ownership ledger, checks and limitations align.

## Exercise 4: Diagnose and repair the single target-port fault.

Preserve the failure and keep other fields unchanged. This establishes causality more clearly than recreating every resource.

**Expected:** The first incorrect mapping is found and a fresh request verifies repair.

## Exercise 5: Verify isolation with both positive and negative flows.

A policy object existing or one successful request cannot establish isolation. Keep the implementation and caller identities in the record.

**Expected:** Allowed traffic succeeds and the denied owned case fails under an enforcing CNI.

## Exercise 6: Teach the system and defend its evidence limits.

Independent understanding includes recognizing what remains unqualified. A good operator can stop at a missing capability without inventing success or widening authority.

**Expected:** Explain mechanisms, current results, untested platforms and scoped cleanup.
