# docker-038: explanatory solutions

These answers explain teaching fixtures, not engine results; the mechanism is in [the guide](../guides/docker-038.md).

## Exercise 1: Classify disk usage by resource type.

**Expected answer:** Images, cache, writable layers, logs and volumes.

**Why:** Each category has a different owner and retention policy. A single aggregate number does not identify safe deletions.

**Approach:** Run docker system df and split the total into images, build cache, container writable layers and volumes, then check log sizes.

**Why this is correct:** Each type has its own owner and retention rule, so the safe removals differ per type.

**A plausible wrong approach:** Deleting whatever is largest based on the total risks removing a volume that holds data.

**How to verify:** The breakdown names a category and owner for each large item before any removal is chosen.

## Exercise 2: Predict the effect of ordinary Compose down.

**Expected answer:** It preserves named volumes unless explicit volume deletion is requested.

**Why:** The stop path should not erase learner state. Verify the exact command and project identity before execution.

**Approach:** Read down without -v: it stops and removes the project's containers and network but leaves named volumes.

**Why this is correct:** study-data survives, so a later up sees the same counter.

**A plausible wrong approach:** Adding -v by habit when stopping deletes the learner's counter with the containers.

**How to verify:** After down and up, GET /counter returns the earlier value, and docker volume ls still lists the volume.

## Exercise 3: Design an incident evidence packet.

**Expected evidence:** Failure symptom, time, resource inventory and bounded relevant logs.

**Why:** Preserve the original condition before changing the engine. This makes the repair explainable and helps distinguish recovery from coincidental disappearance.

**Approach:** Before changing anything, capture the symptom, the time, the df output, the project's ps -a output and a bounded slice of logs.

**Why this is correct:** This preserves the state that explains the failure, so a later fix can be tied to its cause.

**A plausible wrong approach:** Pruning first and checking afterward makes the disk pressure vanish along with its explanation.

**How to verify:** The packet has each item with a timestamp, and the repair note refers to it.

## Exercise 4: Diagnose a detached volume labeled unused.

**Expected answer:** Determine its owner and retained data purpose before deletion.

**Why:** A volume can be temporarily unattached between container runs. Tool reachability is not the same as user intent to discard data.

**Approach:** Read the volume's labels and name to find its project, then ask whether its data is still wanted.

**Why this is correct:** A volume with no container attached may be between runs, as study-data is after down.

**A plausible wrong approach:** Deleting every dangling volume because the tool says unused can remove the only copy of learner data.

**How to verify:** The project label points to an owner, who confirms keep or delete before removal.

## Exercise 5: Explain why broad engine pruning is out of scope.

**Expected answer:** It can affect unrelated workloads and recoverable state.

**Why:** The study project owns only its own resources. Cleanup authorization should remain as narrow as the task that created them.

**Approach:** Compare the scope of the study task, one project's resources, with what system prune touches, everything on the engine.

**Why this is correct:** Pruning can remove other projects' images, caches and volumes that this task never created.

**A plausible wrong approach:** Running a broad prune because the study app is done reaches beyond what the task may remove.

**How to verify:** Cleanup commands filter by the project label, and the engine's other resources remain afterward.

## Exercise 6: Write a scoped recovery and cleanup plan.

**Expected evidence:** Explicit targets, retained data, repair check and final ownership readback.

**Why:** A good plan makes every destructive action reviewable and verifies the intended outcome without claiming unrelated resources were safe to remove.

**Approach:** List each target by name, what data stays, the check that shows recovery, and a final listing of the project's resources.

**Why this is correct:** Naming each destructive step lets someone review it, and the final listing shows exactly what remains.

**A plausible wrong approach:** A plan that says clean up Docker gives no target to review and no way to confirm the result.

**How to verify:** After the plan runs, the project-filtered listing matches the plan's expected remaining resources.

## Check your transfer

Build cache is regenerable, so clearing it costs rebuild time rather than data, which makes it a reasonable target once the evidence packet exists. On a shared host it also slows other people's builds, so prefer a bounded command such as `docker builder prune --filter until=24h`, announce it, and record what was freed. Rerun `docker system df` to confirm the reclaimed space and check that the app is still healthy. If disk use barely drops, the pressure lies elsewhere, often in logs or volumes.
