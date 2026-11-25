# docker-029: explanatory solutions

These answers explain teaching fixtures, not engine results; the mechanism is in [the guide](../guides/docker-029.md).

## Exercise 1: Distinguish SBOM and provenance.

**Expected answer:** Component inventory versus build-origin evidence.

**Why:** They answer complementary questions. An inventory does not explain who built the artifact; a build statement does not enumerate every vulnerability.

**Approach:** Ask what each document answers: the SBOM lists the packages inside the image, while provenance describes the inputs and builder that produced it.

**Why this is correct:** The sbom.spdx.json from worked example 1 names Python and OS packages but says nothing about which machine ran the build.

**A plausible wrong approach:** Treating a complete SBOM as proof of a trustworthy build skips the separate question of origin.

**How to verify:** Look for builder and source fields in sbom.spdx.json; they are absent, which is why a provenance statement is needed too.

## Exercise 2: Predict what a source-only inventory misses.

**Expected answer:** Resolved base packages and exact inherited versions.

**Why:** A Dockerfile tag is an input reference, not a full final filesystem inventory. Resolve and inspect the actual artifact for stronger evidence.

**Approach:** Compare what the Dockerfile names, `python:3.12-slim` and `server.py`, with what the exported image filesystem actually contains.

**Why this is correct:** The base tag resolves to many OS and Python packages at specific versions that appear nowhere in the source.

**A plausible wrong approach:** Building the inventory by reading the Dockerfile lists two items and misses the inherited packages a scanner needs.

**How to verify:** The package list in sbom.spdx.json includes OS packages absent from the source files, as worked example 1 notes.

## Exercise 3: Design an evidence linkage table.

**Expected evidence:** Every record names the same image digest and platform scope.

**Why:** This prevents acceptance, inventory and provenance from drifting across mutable tags or architecture-specific artifacts.

**Approach:** Make one row per record, acceptance, SBOM and provenance, with columns for image digest and platform.

**Why this is correct:** If every row names the same digest and platform, the documents describe one artifact; any mismatch shows drift.

**A plausible wrong approach:** Linking records by the tag ds60-docker-study:local lets a rebuild silently change which image each record describes.

**How to verify:** Compare the digest column; every row matches, or the mismatched row is flagged before release.

## Exercise 4: Diagnose an unsigned provenance statement from an unknown source.

**Expected answer:** It is an untrusted claim until verified under a policy.

**Why:** Structured metadata is easy to produce. Trust depends on issuer identity, integrity and the permitted build process, not the presence of JSON fields.

**Approach:** Treat the unsigned statement as a claim: check who issued it and whether a signature verifies against a key your policy trusts.

**Why this is correct:** Anyone can write JSON with builder and source fields, so the fields alone show only that someone wrote them.

**A plausible wrong approach:** Accepting the provenance because its fields look complete trusts an unknown author.

**How to verify:** Run the verification your policy defines; with no signature or unknown issuer, the record stays untrusted.

## Exercise 5: Explain exporter limitations honestly.

**Expected answer:** Attestation generation and preservation depend on the selected workflow.

**Why:** Test the actual output route. A feature flag in a build command does not prove a downstream registry or local archive retains the expected metadata.

**Approach:** Follow where the attestation goes: the local output in worked example 1 writes sbom.spdx.json to a directory, while a docker load or registry route may keep it differently or drop it.

**Why this is correct:** Whether metadata survives depends on the exporter and destination, so the flag alone proves nothing downstream.

**A plausible wrong approach:** Assuming --sbom=true means every copy of the image carries an SBOM fails when a later transfer loses it.

**How to verify:** Inspect the actual destination for the attestation after each hop in the route.

## Exercise 6: Write a supply-chain review for the fixture.

**Expected evidence:** Known source, resolved base, component record and actual acceptance limits.

**Why:** Keep unknowns visible. A small educational artifact deserves clear provenance without pretending it has passed a production assurance program.

**Approach:** List the fixture's known source files, the resolved base digest, the SBOM file, and the acceptance checks that ran.

**Why this is correct:** Each item is observable, and naming what is unknown, such as the base publisher's build process, keeps the review honest.

**A plausible wrong approach:** Writing that the fixture meets supply-chain requirements claims a review program that never took place.

**How to verify:** Each line in the review points to a file or command output, and the unknowns are listed in their own section.

## Check your transfer

Most likely it does not appear as a package. The scanner finds packages through metadata such as the Debian package database and Python `dist-info` directories, and a loose file copied by `COPY server.py` has none. Its identity belongs in the source revision and build inputs that provenance records, tied to the same image digest. Searching the exported file for `server.py` settles it: if a file entry shows up, this scanner also catalogs plain files, and the review should note that coverage rather than assume it.
