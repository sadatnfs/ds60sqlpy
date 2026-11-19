# docker-029: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-029.md`.

## Exercise 1: Distinguish SBOM and provenance.

**Expected answer:** Component inventory versus build-origin evidence.

**Why:** They answer complementary questions. An inventory does not explain who built the artifact; a build statement does not enumerate every vulnerability.

## Exercise 2: Predict what a source-only inventory misses.

**Expected answer:** Resolved base packages and exact inherited versions.

**Why:** A Dockerfile tag is an input reference, not a full final filesystem inventory. Resolve and inspect the actual artifact for stronger evidence.

## Exercise 3: Design an evidence linkage table.

**Expected evidence:** Every record names the same image digest and platform scope.

**Why:** This prevents acceptance, inventory and provenance from drifting across mutable tags or architecture-specific artifacts.

## Exercise 4: Diagnose an unsigned provenance statement from an unknown source.

**Expected answer:** It is an untrusted claim until verified under a policy.

**Why:** Structured metadata is easy to produce. Trust depends on issuer identity, integrity and the permitted build process, not the presence of JSON fields.

## Exercise 5: Explain exporter limitations honestly.

**Expected answer:** Attestation generation and preservation depend on the selected workflow.

**Why:** Test the actual output route. A feature flag in a build command does not prove a downstream registry or local archive retains the expected metadata.

## Exercise 6: Write a supply-chain review for the fixture.

**Expected evidence:** Known source, resolved base, component record and actual acceptance limits.

**Why:** Keep unknowns visible. A small educational artifact deserves clear provenance without pretending it has passed a production assurance program.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
