# k8s-037: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

A Kubernetes upgrade is a compatibility and state-transition problem, not merely a change to a version string. The API server, kubelet, kubectl, controllers, networking and storage components have supported version relationships. The Kubernetes version-skew policy describes bounds for core components, while a deployment tool or extension can impose additional restrictions.

This course uses a replacement-cluster rehearsal: the host prepares two separately owned, pinned clusters, called source and destination in the evidence packet. Synthetic manifests and data are rendered and tested against each. The exercise does not perform an in-place production upgrade and does not demonstrate high-availability control-plane maintenance. A small kind environment is useful for API and fixture compatibility, but its results have that explicit scope.

The normal runtime currently qualifies one pinned stack. A second stack is unavailable until the host supplies its exact node-image digest, tool versions and compatibility receipt. Never invent a destination version or download one during a lesson. The offline matrix uses symbolic versions A and B so that a teaching trace cannot be confused with a tested release pair.

## Exercise 1: List exact version inputs

The core skew policy is only one part of the environment. A reproducible rehearsal identifies the actual components and immutable artifacts so another host can understand what was tested and what remains outside scope.

**Expected:** A concrete pinned stack rather than a generic latest label.

## Exercise 2: Audit API usage

This inventory exposes removed APIs and feature fields before application testing. A simple textual version replacement can miss changed schemas or semantics, so validation needs the actual destination API contract.

**Expected:** Every used API/feature has a server acceptance row.

## Exercise 3: Evaluate the incomplete matrix

The matrix prevents an early check from being inflated into overall readiness. A missing controller is explicit work for the host qualification process, not an excuse to invent its effects in a worksheet.

**Expected:** Destination not accepted; controller capability remains missing.

## Exercise 4: Compare synthetic data

The application can run with empty or wrong storage. The marker is a small but concrete data contract that catches this class of migration defect without pretending to represent a full database migration.

**Expected:** Mismatch blocks promotion even when /version succeeds.

## Exercise 5: Design a rollback boundary

The controlled example has a fixed marker, so rollback reasoning is simple. A real write-producing workload requires a plan for divergence and data compatibility, which cannot be solved by keeping an old cluster name alone.

**Expected:** Source retained through the stated window; mutable-data rollback is outside this immutable fixture.

## Exercise 6: Write the qualification conclusion

The conclusion should be useful without exaggeration: it can establish specific API and application compatibility, expose missing capabilities and preserve a repeatable packet, while leaving broader production upgrade design to its own procedure.

**Expected:** Only the exact tested stack and synthetic workload gates are claimed.

## Boundary and troubleshooting review

The example matrix is a method for organizing evidence, not a certification for arbitrary Kubernetes releases. A passed A/B marker test says nothing about untested plugins, workload APIs or production failure domains.

Do not treat replacement as a universal substitute for an upgrade procedure. Production systems require their own maintenance order, availability, storage, rollback and support decisions. Here the deliverable is a concrete compatibility packet for a bounded synthetic workload and exact host-qualified versions.
