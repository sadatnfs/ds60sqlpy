# docker-003: explanatory solutions

These answers explain teaching fixtures, not engine results; the mechanism is in [the guide](../guides/docker-003.md).

## Exercise 1: Classify /app/server.py in the fixture.

**Expected answer:** An image-provided application file.

**Why:** The Dockerfile COPY instruction places it into a build layer. Reading it from a container demonstrates that the image content is visible through the container filesystem view.

**Approach:** Trace /app/server.py to the Dockerfile line COPY server.py /app/server.py, which places it in a read-only image layer below every container's writable layer.

**Why this is correct:** Because the file comes from a build instruction, every container started from the tag sees it, and only a rebuild with a changed source can alter it.

**A plausible wrong approach:** Calling it a runtime file created by the server fails here, since server.py never writes into /app; it only writes counter files under /data.

**How to verify:** Worked example 1 prints True for Path('/app/server.py').is_file() even with --rm and no mounts, which only image content can explain.

## Exercise 2: Predict whether a sibling container sees an unmounted new file.

**Expected answer:** It does not share the first container writable layer.

**Why:** Both instances start from the image. Changes in one private writable layer are not broadcast into another container simply because both use the same tag.

**Approach:** Picture each container's writable layer as private copy-on-write storage over the shared image layers, then check whether any mount links the two containers.

**Why this is correct:** Without a shared volume or bind mount, a file written by one container exists only in that container's upper layer, so the sibling's view of the path is unchanged.

**A plausible wrong approach:** Assuming the shared tag means a shared filesystem fails, because the tag only names the read-only lower layers that both containers began from.

**How to verify:** Write a marker file in /tmp of one long-running container, then list the same path in a second container from the same image; the marker is absent.

## Exercise 3: Make a restart-versus-recreate persistence table.

**Expected evidence:** Writable layer survives restart but not removal; volumes follow their own lifetime.

**Why:** A restart preserves the container object. A recreate replaces it. A mounted volume is independent, so the table must name storage rather than make one blanket persistence claim.

**Approach:** Build a table with rows for the writable layer, the study-data volume and the /tmp tmpfs, and columns for restart, recreate and image rebuild.

**Why this is correct:** Restart keeps the container ID and its writable layer; recreate discards both. The volume survives both because compose.yaml mounts it by name; tmpfs is empty after either.

**A plausible wrong approach:** A single blanket rule such as data survives restarts misses that the fixture's /tmp is tmpfs, which is wiped on every restart even though the container persists.

**How to verify:** Increment the counter, restart the app service, read /counter, then recreate and read again; the value persists both times because counter.json lives in /data.

## Exercise 4: Diagnose a missing file after compose up recreates a service.

**Expected answer:** Check whether it was written to the old disposable layer.

**Why:** The service name can stay the same while the container ID changes. A familiar name is not proof that the underlying writable layer or process is the same object.

**Approach:** Compare the container ID before and after compose up, then ask where the missing file was written: the writable layer, /tmp, or the /data volume.

**Why this is correct:** Compose recreates a service when its configuration or image changes. The new container starts with a fresh writable layer, so files outside volumes disappear.

**A plausible wrong approach:** Restoring the image or reinstalling Compose fails to recover the file, because the image never held it and the old writable layer was removed with the old container.

**How to verify:** docker compose -p ds60-docker-study ps -q app prints a different ID after recreation, and a file written to /data before it is still present afterward.

## Exercise 5: Explain why read-only plus tmpfs permits temporary writes.

**Expected answer:** The root mount and tmpfs have different write policies.

**Why:** Read-only is evaluated for the target mount. A bounded tmpfs intentionally supplies volatile writable storage without making the application directory writable.

**Approach:** Look at each mount separately: compose.yaml sets read_only: true for the root filesystem and adds a tmpfs at /tmp with `rw,noexec,nosuid` and `size=16m`.

**Why this is correct:** The read-only flag applies to the root mount. The tmpfs is its own mount with its own options, so writes under /tmp succeed while writes under /app fail.

**A plausible wrong approach:** Removing read_only to silence an application write error fails the lesson goal, because it makes /app and every other path writable to a compromised process.

**How to verify:** With the stack running, a python -c write to /tmp/x succeeds through docker compose exec, while the same write to /app/x raises a read-only filesystem error.

## Exercise 6: Choose storage for user progress and transient scratch data.

**Expected answer:** A named volume for progress and bounded temporary storage for scratch.

**Why:** The choice should follow retention and recovery requirements. Keeping every file forever increases cleanup and privacy costs; discarding user progress on replacement violates the product contract.

**Approach:** Classify each kind of data by whether a learner would lose work if it vanished, and then pick a volume, tmpfs or writable layer to match.

**Why this is correct:** Progress such as counter.json must survive container replacement, which only the study-data volume guarantees. Scratch files gain from tmpfs, which is bounded and cleared automatically.

**A plausible wrong approach:** Putting everything into the volume keeps stale scratch files forever and widens what a backup or privacy review must cover, while the writable layer loses progress on recreate.

**How to verify:** Recreate the app service and check that /data/counter.json still exists and /tmp is empty, matching the retention rule you wrote for each.

## Check your transfer

`restart` stops and starts the same container, so its writable layer, including `/app/uploads`, survives. Editing the service configuration makes `up -d` recreate the service: a new container ID with a fresh, empty writable layer on top of the image, so the uploads are not there. The fix is a named volume mounted at `/app/uploads`, ideally with a read-only root and a tmpfs for scratch. Record `docker compose ps -q app` before and after `up`; different IDs confirm recreation. Seeing the same ID with the files missing would disprove this explanation and point at the application deleting them.
