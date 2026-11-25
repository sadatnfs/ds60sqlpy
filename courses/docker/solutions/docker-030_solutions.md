# docker-030: explanatory solutions

These answers explain teaching fixtures, not engine results; the mechanism is in [the guide](../guides/docker-030.md).

## Exercise 1: Separate vulnerability presence and exploitability.

**Expected evidence:** A matched affected component versus a demonstrated reachable exploit condition.

**Why:** Both matter, but neither should be fabricated. A finding needs triage even when immediate exploitability is uncertain.

**Approach:** Read the synthetic finding: example-library 1.0 is installed and 1.1 is fixed, which shows a version match, not an attack path.

**Why this is correct:** Exploitability depends on whether the app reaches the flawed code under real inputs, which the record does not show.

**A plausible wrong approach:** Ignoring the finding until someone shows an exploit leaves a known affected version waiting for triage.

**How to verify:** The triage note states whether the component is used by server.py, and the status stays requires review until decided.

## Exercise 2: Predict why an interactive patch disappears.

**Expected answer:** Container recreation returns to the packaged image inputs.

**Why:** The writable layer is not the source of truth for a reproducible release. Capture the change in the build recipe and rebuild.

**Approach:** Trace what recreation starts from: the image built from the Dockerfile, not the old container's writable layer.

**Why this is correct:** A package installed with docker exec lives in that layer and disappears when Compose recreates the container.

**A plausible wrong approach:** Patching the running container and closing the finding leaves the next deployment unpatched.

**How to verify:** Recreate the container and check the package version; it is back to the old one until the Dockerfile changes.

## Exercise 3: Design a minimal base-image update.

**Expected evidence:** Change the resolved base deliberately and rerun relevant acceptance.

**Why:** Keep other changes small so failures can be attributed. Record both old and new identities for rollback and comparison.

**Approach:** Change only the resolved base, such as a new digest for `python:3.12-slim` passed through DS60_PYTHON_IMAGE, and rerun acceptance.

**Why this is correct:** With one change, a new failure points to the base and not to unrelated edits.

**A plausible wrong approach:** Bumping the base, server.py and the compose file together makes a regression hard to trace.

**How to verify:** The record lists old and new base digests, and acceptance passes on the new image.

## Exercise 4: Diagnose a scan report attached only to a mutable tag.

**Expected answer:** Resolve the exact scanned artifact before using the result.

**Why:** The current tag may refer to different bytes. Evidence must be tied to immutable identity and the scanner’s knowledge date.

**Approach:** Find which digest the scanner examined, and compare it with what the tag resolves to now.

**Why this is correct:** A mutable tag may have moved since the scan, so the findings may describe other content.

**A plausible wrong approach:** Using the tag's scan to close or open findings on today's image applies results to bytes the scanner never read.

**How to verify:** The scan record names a digest and database date; rescan the current digest if they differ.

## Exercise 5: Explain why zero findings is not a universal security proof.

**Expected answer:** Scanners have scope and knowledge limitations.

**Why:** Application flaws, configuration issues and unknown vulnerabilities may be outside the scanner’s matching rules. State the actual tool result and limits.

**Approach:** List what the scanner checks: known identifiers matched to recognized package versions, as of its database date.

**Why this is correct:** Flaws in server.py, weak compose settings and unpublished vulnerabilities fall outside those rules.

**A plausible wrong approach:** Reporting zero findings as the image is secure claims coverage the tool does not provide.

**How to verify:** The report names the tool, its database date and the scope, and lists configuration review as a separate check.

## Exercise 6: Write a patch decision record.

**Expected evidence:** Finding, affected artifact, chosen action, tests and residual risk.

**Why:** The record should make the operational decision reviewable. It should not replace evidence with an unqualified claim that everything is now safe.

**Approach:** Record the finding, the affected digest, the action chosen, the tests rerun and any risk remaining.

**Why this is correct:** A reviewer can follow the decision and see that the new image passed the same acceptance.

**A plausible wrong approach:** Writing just patched, all safe hides which image changed and what was left unresolved.

**How to verify:** Each field links to the scan output, the rebuild and a test receipt for the new digest.

## Check your transfer

Presence is established; reachability is weak, because `server.py` opens no TLS and the healthcheck uses HTTP. Since a base refresh is cheap and reversible here, a reasonable decision is to rebuild from a refreshed base, rerun the health, peer and counter checks, and record the old and new image IDs with the version printed by `ssl.OPENSSL_VERSION`. The record states the residual risk if no fixed version exists yet. If the rebuilt image still prints the old OpenSSL version, the refresh did not take effect and the finding stays open.
