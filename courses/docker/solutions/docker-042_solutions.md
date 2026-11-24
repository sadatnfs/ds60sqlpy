# docker-042: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-042.md`.

## Exercise 1: Predict all outcomes before running the final project.

**Expected answer:** A written normal, failure, replacement and recovery expectation.

**Why:** Predictions make the experiment falsifiable. Without them it is easy to reinterpret any output as success.

**Approach:** Before running, write expected results for normal requests, a chosen failure, container replacement and restore.

**Why this is correct:** With written expectations, each result either matches or does not, and a mismatch cannot be reinterpreted as success.

**A plausible wrong approach:** Running first and describing whatever happened as expected makes any outcome look correct.

**How to verify:** Compare each observed result with its prediction and record matches and differences.

## Exercise 2: Change one noncritical configuration and rebuild or recreate appropriately.

**Expected evidence:** The chosen lifecycle action matches the kind of change.

**Why:** Source changes need a new image; runtime environment changes need application of new container configuration. Explain why your selected action is sufficient.

**Approach:** Classify the change: editing server.py needs a rebuild; changing APP_MESSAGE in compose.yaml needs only recreation.

**Why this is correct:** Recreating picks up new container settings; only a rebuild puts new source into the image.

**A plausible wrong approach:** Restarting the container after editing server.py keeps running the old image's code.

**How to verify:** After the chosen action, GET / or the changed route shows the new behavior, and the image ID changes only after a rebuild.

## Exercise 3: Assemble a source-bound release packet.

**Expected evidence:** Exact source, image, platform, commands and observations.

**Why:** The packet should let another learner connect each result to the artifact actually tested. Avoid stale screenshots or reports from an earlier image.

**Approach:** Collect the source revision, image ID, platform, exact commands and their observed outputs for the same run.

**Why this is correct:** Each result is tied to the artifact that produced it, so another learner can repeat it.

**A plausible wrong approach:** Reusing screenshots from an earlier image makes the packet describe something not released.

**How to verify:** Every entry shows the same image ID, matching the one deployed.

## Exercise 4: Diagnose a deliberate single-layer failure.

**Expected answer:** Minimal evidence locates the fault and a targeted repair restores the invariant.

**Why:** Do not weaken the acceptance check. Keep the failing observation as a regression case for the repaired configuration.

**Approach:** Introduce one fault, such as a wrong client port, and collect only the evidence needed to find its layer.

**Why this is correct:** One fault and minimal evidence point to one cause; the repair should restore that check's passing result.

**A plausible wrong approach:** Loosening the acceptance check until it passes hides the fault.

**How to verify:** Keep the failing case as a regression test; it fails before the repair and passes after.

## Exercise 5: Prove independent data recovery.

**Expected evidence:** A new owned target serves the preserved expected state.

**Why:** This is stronger than backup existence. Keep the original data intact until the restore has passed its application-level check.

**Approach:** Restore the backup into a new volume, start a reader on it, and request GET /counter.

**Why this is correct:** A response with the expected value proves the data is usable, which a stored archive alone does not.

**A plausible wrong approach:** Restoring over the original volume before the check risks losing the only good copy.

**How to verify:** The restored reader shows the expected counter while the original volume still holds its own value.

## Exercise 6: Teach the full system and defend its limits.

**Expected evidence:** A beginner can follow the handoff and identify what it does not guarantee.

**Why:** Good engineering communication states both achieved behavior and the boundaries of evidence. Local Docker success is a foundation for further systems learning, not a blanket production certification.

**Approach:** Explain the request path from the worked example, then list what the system does not guarantee, such as host loss or replicas.

**Why this is correct:** A beginner can operate the system and knows where its guarantees stop.

**A plausible wrong approach:** Presenting local success as production readiness sends the next learner into unsupported use.

**How to verify:** A new reader follows the handoff, gets the same results, and can name two limits it states.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
