# docker-013: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

A named volume is storage managed by the engine and mounted into containers. A bind mount maps an explicitly chosen host path into a container. A temporary filesystem is volatile storage usually backed by memory. The choice determines ownership, portability, backup and what survives container replacement.

The fixture stores its counter in a named volume mounted at `/data`. Its application code is in the image. This separation lets the app container be replaced without losing the counter. A bind mount is useful for editing a local project, but it gives container processes direct access to the chosen host files with the mount’s permissions.

Mounting a directory over an image path hides the image content at that location while the mount is present. A bind mount hides the packaged directory without copying its files into the host directory. Docker-managed volumes have an important initialization exception: when an empty volume is mounted over existing image content, Docker copies that content into it by default unless volume-nocopy is selected. A nonempty mounted volume hides the packaged content. Distinguish those cases before diagnosing missing or unexpectedly seeded files.

A Compose service can mount `study-data:/data`, with `study-data` declared in the top-level `volumes` section. Compose assigns a project-scoped volume name unless configured otherwise. The fixture’s app treats an absent counter.json as an initial count of zero and updates that file through an atomic replace under a process-local lock. It does not create an exclusive marker file. The separate restore command uses exclusive file creation to refuse overwriting an existing restore target.

Use POST `/increment` only within the disposable lab to intentionally change the teaching counter; GET `/counter` reads it without mutation. Record a value, recreate only the app container, and verify that the value did not reset. Rebuilding an image is unnecessary for this test, because the question concerns storage lifetime.

## Exercise 1: Predict data retention after app recreation.

The container object changes, but the volume is separate. A changed project name can select a different volume, so identity matters as much as the mount path.

**Expected:** Named-volume data remains if the same volume is mounted.

## Exercise 2: Compare named volume and bind mount ownership.

Bind mounts are convenient for editing and exports but can expose private or sensitive host paths. Volumes are easier to keep independent of a host directory layout.

**Expected:** Engine-managed storage versus an explicit host directory.

## Exercise 3: Build a persistence evidence table.

A value alone can be ambiguous if a seed coincidentally matches. Recording both storage and container identities makes the replacement experiment stronger.

**Expected:** Before value, old/new container IDs, volume identity and after value.

## Exercise 4: Diagnose missing code after mounting over /app.

A mount presents another filesystem view. It does not automatically copy all image files into an arbitrary bind directory, so mount code and data intentionally.

**Expected:** The mount hides packaged content at that path.

## Exercise 5: Explain why changing project names may look like data loss.

The original data may still exist under the original project. Inspect ownership and volume names before declaring corruption or deleting apparently unused storage.

**Expected:** The new project can create a different named volume.

## Exercise 6: Choose a safe cleanup policy for progress.

Learner progress has a longer intended lifetime than runtime processes. Cleanup should preserve it and provide a backup/export route before any irreversible deletion.

**Expected:** Stop containers routinely; delete data only after an explicit reset decision.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
