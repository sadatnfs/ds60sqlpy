# docker-030: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-030.md`.

## Exercise 1: Separate vulnerability presence and exploitability.

**Expected evidence:** A matched affected component versus a demonstrated reachable exploit condition.

**Why:** Both matter, but neither should be fabricated. A finding needs triage even when immediate exploitability is uncertain.

## Exercise 2: Predict why an interactive patch disappears.

**Expected answer:** Container recreation returns to the packaged image inputs.

**Why:** The writable layer is not the source of truth for a reproducible release. Capture the change in the build recipe and rebuild.

## Exercise 3: Design a minimal base-image update.

**Expected evidence:** Change the resolved base deliberately and rerun relevant acceptance.

**Why:** Keep other changes small so failures can be attributed. Record both old and new identities for rollback and comparison.

## Exercise 4: Diagnose a scan report attached only to a mutable tag.

**Expected answer:** Resolve the exact scanned artifact before using the result.

**Why:** The current tag may refer to different bytes. Evidence must be tied to immutable identity and the scanner’s knowledge date.

## Exercise 5: Explain why zero findings is not a universal security proof.

**Expected answer:** Scanners have scope and knowledge limitations.

**Why:** Application flaws, configuration issues and unknown vulnerabilities may be outside the scanner’s matching rules. State the actual tool result and limits.

## Exercise 6: Write a patch decision record.

**Expected evidence:** Finding, affected artifact, chosen action, tests and residual risk.

**Why:** The record should make the operational decision reviewable. It should not replace evidence with an unqualified claim that everything is now safe.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
