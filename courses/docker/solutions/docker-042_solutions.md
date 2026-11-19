# docker-042: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-042.md`.

## Exercise 1: Predict all outcomes before running the final project.

**Expected answer:** A written normal, failure, replacement and recovery expectation.

**Why:** Predictions make the experiment falsifiable. Without them it is easy to reinterpret any output as success.

## Exercise 2: Change one noncritical configuration and rebuild or recreate appropriately.

**Expected evidence:** The chosen lifecycle action matches the kind of change.

**Why:** Source changes need a new image; runtime environment changes need application of new container configuration. Explain why your selected action is sufficient.

## Exercise 3: Assemble a source-bound release packet.

**Expected evidence:** Exact source, image, platform, commands and observations.

**Why:** The packet should let another learner connect each result to the artifact actually tested. Avoid stale screenshots or reports from an earlier image.

## Exercise 4: Diagnose a deliberate single-layer failure.

**Expected answer:** Minimal evidence locates the fault and a targeted repair restores the invariant.

**Why:** Do not weaken the acceptance check. Keep the failing observation as a regression case for the repaired configuration.

## Exercise 5: Prove independent data recovery.

**Expected evidence:** A new owned target serves the preserved expected state.

**Why:** This is stronger than backup existence. Keep the original data intact until the restore has passed its application-level check.

## Exercise 6: Teach the full system and defend its limits.

**Expected evidence:** A beginner can follow the handoff and identify what it does not guarantee.

**Why:** Good engineering communication states both achieved behavior and the boundaries of evidence. Local Docker success is a foundation for further systems learning, not a blanket production certification.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
