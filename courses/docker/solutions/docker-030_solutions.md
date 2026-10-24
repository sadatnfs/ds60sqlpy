# docker-030: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

A vulnerability finding connects an affected component version to a published issue under a scanner’s knowledge and matching rules. It is evidence for investigation, not a complete exploitability assessment. False matches, missing packages, runtime exposure and available fixes all influence the response.

Patching an image generally means rebuilding from updated inputs and replacing containers with the new image. Installing packages interactively inside a running container makes an untracked difference that disappears on recreation. The maintained build recipe and lock inputs must describe the repair.

A rebuild can introduce regressions as well as fixes. Use a small update scope, preserve the old immutable artifact, run the relevant tests and verify the actual final image. Do not claim that a passing scan proves absence of all vulnerabilities or that an unfixed low-severity finding is automatically harmless.

Classify findings by component, installed version, fixed version if available, application reachability and required action. Keep the scanner database timestamp and artifact digest. A tag-based report becomes stale when the tag changes.

For this lesson, use a synthetic finding table and prepare an update plan without downloading a scanner or changing the engine. Actual scanning is an optional explicitly prepared tool workflow. The course does not invent a zero-findings badge for an unscanned image.

## Exercise 1: Separate vulnerability presence and exploitability.

Both matter, but neither should be fabricated. A finding needs triage even when immediate exploitability is uncertain.

**Expected:** A matched affected component versus a demonstrated reachable exploit condition.

## Exercise 2: Predict why an interactive patch disappears.

The writable layer is not the source of truth for a reproducible release. Capture the change in the build recipe and rebuild.

**Expected:** Container recreation returns to the packaged image inputs.

## Exercise 3: Design a minimal base-image update.

Keep other changes small so failures can be attributed. Record both old and new identities for rollback and comparison.

**Expected:** Change the resolved base deliberately and rerun relevant acceptance.

## Exercise 4: Diagnose a scan report attached only to a mutable tag.

The current tag may refer to different bytes. Evidence must be tied to immutable identity and the scanner’s knowledge date.

**Expected:** Resolve the exact scanned artifact before using the result.

## Exercise 5: Explain why zero findings is not a universal security proof.

Application flaws, configuration issues and unknown vulnerabilities may be outside the scanner’s matching rules. State the actual tool result and limits.

**Expected:** Scanners have scope and knowledge limitations.

## Exercise 6: Write a patch decision record.

The record should make the operational decision reviewable. It should not replace evidence with an unqualified claim that everything is now safe.

**Expected:** Finding, affected artifact, chosen action, tests and residual risk.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
