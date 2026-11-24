# docker-020: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-020.md`.

## Exercise 1: Predict whether matching usernames guarantee file access.

**Expected answer:** No; numeric identity and permission bits matter.

**Why:** Names are lookup labels. Compare numeric IDs and the actual mount ownership before diagnosing a cross-environment permission mismatch.

**Approach:** Compare numeric IDs, not names: the fixture runs as 10001:10001, while a host user named app might be 1000.

**Why this is correct:** The kernel checks numeric UIDs against owners and mode bits. Matching names on two systems can map to different numbers.

**A plausible wrong approach:** Creating a host user with the same name and expecting access fails when the numbers differ.

**How to verify:** Worked example 2 prints 10001 10001; compare with ls -n on the mount source, which shows numeric owners.

## Exercise 2: Separate read-only code and writable data paths.

**Expected evidence:** /app is code, /data is retained application state.

**Why:** This layout limits accidental code mutation while allowing the app’s intended state changes. Do not make the entire filesystem writable to support one data directory.

**Approach:** Assign each path a role: /app holds server.py from COPY and stays read-only; /data is the chown'd directory for state.

**Why this is correct:** server.py writes only to /data, and read_only: true in compose keeps /app and everything else from changing.

**A plausible wrong approach:** Dropping read_only so the app can write anywhere hides a mistake that would write state into the wrong path.

**How to verify:** In the running fixture, a write to /data succeeds and a write to /app fails with a read-only error.

## Exercise 3: Design a non-root image setup sequence.

**Expected evidence:** Create required paths, set ownership, then select the runtime user.

**Why:** The sequence makes startup deterministic. Deferring broad permission changes to every launch can hide incorrect packaging and require unnecessary privilege.

**Approach:** Follow the fixture's order: RUN mkdir -p /data, chown 10001:10001 /data, then USER 10001:10001 before CMD.

**Why this is correct:** Ownership is set once, as root, at build time; the process then starts without needing root.

**A plausible wrong approach:** Running as root and calling chown at every startup needs extra privilege and hides packaging errors.

**How to verify:** docker image inspect shows Config.User 10001:10001, and /data is listed as owned by 10001 in the image.

## Exercise 4: Diagnose a bind-mount permission failure.

**Expected answer:** Identify mount path, effective UID and exact denied operation.

**Why:** A targeted observation narrows the repair. Recursive host ownership changes can damage a developer checkout and are not a general container fix.

**Approach:** Record three facts: the mount source on the host, the UID inside the container, and the denied call with its path.

**Why this is correct:** A bind mount keeps the host's numeric owner, so a host directory owned by 1000 refuses writes from UID 10001.

**A plausible wrong approach:** Running sudo chown -R across the checkout fixes this mount but changes ownership of unrelated developer files.

**How to verify:** ls -n on the source shows the owner; changing only that directory, or using the named volume, makes the write succeed.

## Exercise 5: Explain why chmod 777 weakens the evidence.

**Expected answer:** It allows more writers instead of proving intended ownership.

**Why:** The repaired system no longer tests the same access contract. Prefer the smallest permission change that grants the required operation to the intended identity.

**Approach:** Ask what 777 proves afterward: that anyone can write, not that UID 10001 was meant to write.

**Why this is correct:** The fixture's contract is that only the app's UID owns /data. Mode 777 lets any process in any container sharing the path modify the counter.

**A plausible wrong approach:** Applying 777 to stop errors fixes the symptom while removing the ownership rule the lesson is testing.

**How to verify:** After a targeted fix, ls -n /data shows owner 10001 and mode without world-write.

## Exercise 6: Write a permission acceptance check.

**Expected evidence:** Non-root process can write data and cannot mutate packaged code.

**Why:** Both positive and negative checks matter. Successful persistence alone does not prove that code paths remain protected from accidental writes.

**Approach:** Write one positive and one negative check: POST /increment updates /data, and a write to /app as the same user fails.

**Why this is correct:** Both are needed: the first proves the data path works, the second that code is protected.

**A plausible wrong approach:** Checking only that the counter increments passes even if /app were writable.

**How to verify:** The increment returns the next value, and python -c writing /app/x reports a permission or read-only error.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
