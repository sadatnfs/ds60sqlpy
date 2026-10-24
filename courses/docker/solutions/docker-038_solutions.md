# docker-038: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

An incident is an observed deviation from expected behavior that requires diagnosis or recovery. Disk pressure can arise from images, build cache, container writable layers, logs or volumes. These categories have different retention and ownership, so one global delete command is a poor first response.

Pruning means removing resources considered unused by a tool’s rules. Unused does not always mean unimportant to a learner. A stopped container may retain an investigation, and a detached volume may hold progress awaiting the next container. Identify the resource and intended retention before deletion.

A useful incident sequence preserves evidence, assesses current state, identifies the failing layer, applies a scoped repair and verifies recovery. If an engine VM needs restart, that can interrupt unrelated workloads. A course lesson does not authorize such a host-wide action.

Use read-only inventory first. `docker system df` summarizes storage categories; project-scoped ps, image and volume inspection add ownership. Capture small results privately. Remove only resources you created and have decided to discard, using explicit names or labels checked against the project.

Routine course cleanup uses Compose down without volume deletion. A full disposable-lab reset is separately documented and should name the exact study project and volume. Build cache deletion changes performance and can affect other projects, so it is not hidden in the learner shutdown command.

## Exercise 1: Classify disk usage by resource type.

Each category has a different owner and retention policy. A single aggregate number does not identify safe deletions.

**Expected:** Images, cache, writable layers, logs and volumes.

## Exercise 2: Predict the effect of ordinary Compose down.

The stop path should not erase learner state. Verify the exact command and project identity before execution.

**Expected:** It preserves named volumes unless explicit volume deletion is requested.

## Exercise 3: Design an incident evidence packet.

Preserve the original condition before changing the engine. This makes the repair explainable and helps distinguish recovery from coincidental disappearance.

**Expected:** Failure symptom, time, resource inventory and bounded relevant logs.

## Exercise 4: Diagnose a detached volume labeled unused.

A volume can be temporarily unattached between container runs. Tool reachability is not the same as user intent to discard data.

**Expected:** Determine its owner and retained data purpose before deletion.

## Exercise 5: Explain why broad engine pruning is out of scope.

The study project owns only its own resources. Cleanup authorization should remain as narrow as the task that created them.

**Expected:** It can affect unrelated workloads and recoverable state.

## Exercise 6: Write a scoped recovery and cleanup plan.

A good plan makes every destructive action reviewable and verifies the intended outcome without claiming unrelated resources were safe to remove.

**Expected:** Explicit targets, retained data, repair check and final ownership readback.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
