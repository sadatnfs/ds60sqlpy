# docker-029: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

A software bill of materials, or SBOM, lists components included in an artifact. Provenance records how an artifact was built, including inputs and builder information according to its format. Neither document by itself proves that every component is safe or that the claimed builder was trustworthy.

These records become useful when tied to an immutable artifact identity and a verification policy. An SBOM for yesterday’s tag is not necessarily an SBOM for today’s bytes. A provenance claim needs a trustworthy issuer and integrity verification before it can support a release decision.

The teaching image has a deliberately small application surface but still inherits a base operating system and Python runtime. Supply-chain review includes those dependencies. Copying only one server file does not mean the final image contains only one software component.

BuildKit can produce attestations in supported workflows and exporters. Storage and publication behavior depend on the builder and image store, so do not promise that every local load preserves every attestation identically. Keep metadata generation, artifact delivery and verification as separate steps.

For an offline exercise, create a small component inventory from the Dockerfile and compare it with an actual image inspection or a prepared SBOM. Note what the source recipe cannot reveal without resolving the base image. Do not fabricate a signed result or claim a scanner passed when it was not run.

## Exercise 1: Distinguish SBOM and provenance.

They answer complementary questions. An inventory does not explain who built the artifact; a build statement does not enumerate every vulnerability.

**Expected:** Component inventory versus build-origin evidence.

## Exercise 2: Predict what a source-only inventory misses.

A Dockerfile tag is an input reference, not a full final filesystem inventory. Resolve and inspect the actual artifact for stronger evidence.

**Expected:** Resolved base packages and exact inherited versions.

## Exercise 3: Design an evidence linkage table.

This prevents acceptance, inventory and provenance from drifting across mutable tags or architecture-specific artifacts.

**Expected:** Every record names the same image digest and platform scope.

## Exercise 4: Diagnose an unsigned provenance statement from an unknown source.

Structured metadata is easy to produce. Trust depends on issuer identity, integrity and the permitted build process, not the presence of JSON fields.

**Expected:** It is an untrusted claim until verified under a policy.

## Exercise 5: Explain exporter limitations honestly.

Test the actual output route. A feature flag in a build command does not prove a downstream registry or local archive retains the expected metadata.

**Expected:** Attestation generation and preservation depend on the selected workflow.

## Exercise 6: Write a supply-chain review for the fixture.

Keep unknowns visible. A small educational artifact deserves clear provenance without pretending it has passed a production assurance program.

**Expected:** Known source, resolved base, component record and actual acceptance limits.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
