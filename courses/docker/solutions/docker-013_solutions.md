# docker-013: explanatory solutions

These answers explain teaching fixtures, not engine results; the mechanism is in [the guide](../guides/docker-013.md).

## Exercise 1: Predict data retention after app recreation.

**Expected answer:** Named-volume data remains if the same volume is mounted.

**Why:** The container object changes, but the volume is separate. A changed project name can select a different volume, so identity matters as much as the mount path.

**Approach:** Look for the volume line study-data:/data and check that the recreated container mounts the same named volume.

**Why this is correct:** Recreation replaces the container and its writable layer, but study-data is a separate object, so counter.json survives.

**A plausible wrong approach:** Assuming any recreate keeps data fails when the project name changes, because Compose then creates a new prefixed volume.

**How to verify:** Read GET /counter before and after worked example 2; the value is unchanged and the container ID differs.

## Exercise 2: Compare named volume and bind mount ownership.

**Expected answer:** Engine-managed storage versus an explicit host directory.

**Why:** Bind mounts are convenient for editing and exports but can expose private or sensitive host paths. Volumes are easier to keep independent of a host directory layout.

**Approach:** Compare where the bytes live: a named volume is managed by the engine, and a bind mount is a host path you choose.

**Why this is correct:** A bind mount exposes the exact host directory and its permissions to the container, while a named volume avoids depending on host layout.

**A plausible wrong approach:** Bind-mounting a home directory to share a single file gives the container write access to everything else in it.

**How to verify:** docker volume inspect shows an engine-managed Mountpoint for study-data, while a bind mount's Source in docker inspect is the host path you chose.

## Exercise 3: Build a persistence evidence table.

**Expected evidence:** Before value, old/new container IDs, volume identity and after value.

**Why:** A value alone can be ambiguous if a seed coincidentally matches. Recording both storage and container identities makes the replacement experiment stronger.

**Approach:** Record the counter before, the old container ID, the volume name, the new container ID and the counter after.

**Why this is correct:** Matching counter values alone could be coincidence; adding both IDs and the volume name ties persistence to the replacement.

**A plausible wrong approach:** Recording only the after value of 3 cannot exclude a fresh volume seeded or incremented to the same number.

**How to verify:** The table shows two different container IDs, one unchanged volume name and a counter that continues from its previous value.

## Exercise 4: Diagnose missing code after mounting over /app.

**Expected answer:** The mount hides packaged content at that path.

**Why:** A mount presents another filesystem view. It does not automatically copy all image files into an arbitrary bind directory, so mount code and data intentionally.

**Approach:** Notice that mounting any source at /app places a different filesystem over the image directory holding server.py.

**Why this is correct:** A bind mount hides image content at the mount point; it does not merge or copy files, so python finds no server.py.

**A plausible wrong approach:** Rebuilding the image to restore the file fails, because the mount still hides whatever the image places at /app.

**How to verify:** Remove the mount or point it elsewhere, then python -c printing Path('/app/server.py').is_file() reports True again.

## Exercise 5: Explain why changing project names may look like data loss.

**Expected answer:** The new project can create a different named volume.

**Why:** The original data may still exist under the original project. Inspect ownership and volume names before declaring corruption or deleting apparently unused storage.

**Approach:** Check volume names: Compose prefixes study-data with the project name, so a new -p value refers to a different volume.

**Why this is correct:** The old volume and counter still exist under the old name. The new project simply started with an empty volume.

**A plausible wrong approach:** Deleting volumes that look unused in a panic can destroy the real progress that was never lost.

**How to verify:** docker volume ls lists both prefixed volumes; switching back to the original project shows the old counter again.

## Exercise 6: Choose a safe cleanup policy for progress.

**Expected answer:** Stop containers routinely; delete data only after an explicit reset decision.

**Why:** Learner progress has a longer intended lifetime than runtime processes. Cleanup should preserve it and provide a backup/export route before any irreversible deletion.

**Approach:** Use down without -v for routine stops, and require an explicit reset step with a backup before docker volume rm.

**Why this is correct:** Learner progress outlives containers. Separating stop from reset ensures that only a deliberate action deletes it.

**A plausible wrong approach:** Putting docker compose down -v into a convenience script turns every stop into an irreversible reset.

**How to verify:** After a routine stop and start, GET /counter returns the earlier value; only the documented reset path sets it to 0.

## Check your transfer

Yes. The volume belongs to neither container, so removing and recreating the app does not touch it, and the reporting service keeps reading the same `counter.json` through its read-only mount. The file disappears for both only when the volume itself changes: `docker compose down -v`, an explicit `docker volume rm`, or a project name change that makes Compose create and mount a new, empty volume. If the reporting service saw no file after the recreation, compare the `Mounts` section of `docker inspect` for both containers; two different volume names would disprove the shared-volume assumption.
