# docker-038: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-038.md`.

## Exercise 1: Classify disk usage by resource type.

**Expected answer:** Images, cache, writable layers, logs and volumes.

**Why:** Each category has a different owner and retention policy. A single aggregate number does not identify safe deletions.

## Exercise 2: Predict the effect of ordinary Compose down.

**Expected answer:** It preserves named volumes unless explicit volume deletion is requested.

**Why:** The stop path should not erase learner state. Verify the exact command and project identity before execution.

## Exercise 3: Design an incident evidence packet.

**Expected evidence:** Failure symptom, time, resource inventory and bounded relevant logs.

**Why:** Preserve the original condition before changing the engine. This makes the repair explainable and helps distinguish recovery from coincidental disappearance.

## Exercise 4: Diagnose a detached volume labeled unused.

**Expected answer:** Determine its owner and retained data purpose before deletion.

**Why:** A volume can be temporarily unattached between container runs. Tool reachability is not the same as user intent to discard data.

## Exercise 5: Explain why broad engine pruning is out of scope.

**Expected answer:** It can affect unrelated workloads and recoverable state.

**Why:** The study project owns only its own resources. Cleanup authorization should remain as narrow as the task that created them.

## Exercise 6: Write a scoped recovery and cleanup plan.

**Expected evidence:** Explicit targets, retained data, repair check and final ownership readback.

**Why:** A good plan makes every destructive action reviewable and verifies the intended outcome without claiming unrelated resources were safe to remove.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
