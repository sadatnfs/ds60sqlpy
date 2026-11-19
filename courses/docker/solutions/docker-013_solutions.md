# docker-013: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-013.md`.

## Exercise 1: Predict data retention after app recreation.

**Expected answer:** Named-volume data remains if the same volume is mounted.

**Why:** The container object changes, but the volume is separate. A changed project name can select a different volume, so identity matters as much as the mount path.

## Exercise 2: Compare named volume and bind mount ownership.

**Expected answer:** Engine-managed storage versus an explicit host directory.

**Why:** Bind mounts are convenient for editing and exports but can expose private or sensitive host paths. Volumes are easier to keep independent of a host directory layout.

## Exercise 3: Build a persistence evidence table.

**Expected evidence:** Before value, old/new container IDs, volume identity and after value.

**Why:** A value alone can be ambiguous if a seed coincidentally matches. Recording both storage and container identities makes the replacement experiment stronger.

## Exercise 4: Diagnose missing code after mounting over /app.

**Expected answer:** The mount hides packaged content at that path.

**Why:** A mount presents another filesystem view. It does not automatically copy all image files into an arbitrary bind directory, so mount code and data intentionally.

## Exercise 5: Explain why changing project names may look like data loss.

**Expected answer:** The new project can create a different named volume.

**Why:** The original data may still exist under the original project. Inspect ownership and volume names before declaring corruption or deleting apparently unused storage.

## Exercise 6: Choose a safe cleanup policy for progress.

**Expected answer:** Stop containers routinely; delete data only after an explicit reset decision.

**Why:** Learner progress has a longer intended lifetime than runtime processes. Cleanup should preserve it and provide a backup/export route before any irreversible deletion.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
