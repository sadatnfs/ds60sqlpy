# docker-023: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-023.md`.

## Exercise 1: Map each hardening setting to its mechanism.

**Expected evidence:** Mount writes, capabilities, privilege gain and temporary storage.

**Why:** The settings are complementary rather than synonyms. A clear mapping helps diagnose which boundary rejected an unintended operation.

**Approach:** Match each line to its target: read_only to the root mount, cap_drop to kernel capabilities, no-new-privileges to setuid gains and tmpfs to /tmp scratch space.

**Why this is correct:** Each one blocks a different kind of operation, so knowing the mapping tells you which rule refused a given call.

**A plausible wrong approach:** Treating all four as general hardening and removing them together to fix one error hides which boundary was involved.

**How to verify:** Trigger one forbidden action at a time, such as writing /app or changing a file owner, and note which setting the error points to.

## Exercise 2: Predict whether read-only root prevents volume writes.

**Expected answer:** A separately writable data mount can still allow them.

**Why:** Permissions are applied to the mounted path involved. The design deliberately separates immutable code from intended mutable state.

**Approach:** Look at the mount table: the root is read-only, while study-data is a separate named volume mounted read-write at /data.

**Why this is correct:** read_only applies to the container's root filesystem; a volume brings its own mount options, so writes to /data still work.

**A plausible wrong approach:** Expecting read_only: true to protect the counter from changes assumes it covers every mount.

**How to verify:** POST /increment succeeds and changes counter.json, while a write to /app as the same process fails.

## Exercise 3: Write a least-privilege acceptance pair.

**Expected evidence:** One required action succeeds and one forbidden action fails.

**Why:** Checking only failure could describe a broken application. Checking only success could miss unnecessary access.

**Approach:** Pair a required action, GET /healthz returning ready with the counter persisting, with a forbidden one, writing /app/unexpected.txt.

**Why this is correct:** The pair rules out two different errors: a broken app that refuses everything and an open app that allows everything.

**A plausible wrong approach:** Testing only that /app is not writable passes for a container that cannot serve any request.

**How to verify:** Run both checks against the hardened compose file; the first succeeds and the second reports a read-only error.

## Exercise 4: Diagnose an app that needs an undocumented cache directory.

**Expected answer:** Identify the path and provide a bounded intended mount if justified.

**Why:** Do not make the whole root filesystem writable. Determine whether the cache is temporary, durable or avoidable, then choose the smallest correct storage channel.

**Approach:** Find the exact path from the error, then ask whether the cache must survive restarts, can live in memory, or can be disabled.

**Why this is correct:** A temporary cache fits a small tmpfs like /tmp; a durable one needs a named volume; neither needs the root to become writable.

**A plausible wrong approach:** Setting read_only: false makes the error disappear and also removes protection for /app and every other path.

**How to verify:** After adding only the chosen mount, the app starts, and a write to /app still fails.

## Exercise 5: Explain why privileged mode is inappropriate here.

**Expected answer:** It grants broad access unrelated to the HTTP fixture.

**Why:** A privileged container changes the trust boundary substantially. The lesson’s app has no legitimate requirement for device or host-administration capabilities.

**Approach:** List what privileged: true grants, including all capabilities, host devices and relaxed confinement, and compare it with what server.py does.

**Why this is correct:** The server only listens on 8080 and writes /data, so none of those grants serve the fixture.

**A plausible wrong approach:** Using privileged mode to get past a permission error trades a narrow fix for broad host access.

**How to verify:** The fixture passes its acceptance pair with cap_drop ALL, which shows no capability is needed.

## Exercise 6: Review a hardening change without overstating security.

**Expected evidence:** State controls tested and the trusted-local-code boundary.

**Why:** No finite checklist proves a universal sandbox. Report what the actual configuration restricts and which threats remain outside its supported use.

**Approach:** Describe the configuration as tested: the four settings above, checks that passed, and the assumption that the code is trusted and local.

**Why this is correct:** The settings reduce what the process can do; they do not make the container a sandbox for hostile code.

**A plausible wrong approach:** Calling the result fully secure invites running untrusted images under a configuration never tested for that.

**How to verify:** The review lists each control with its passing check and names the threats left out of scope.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
