# docker-023: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-023.md`.

## Exercise 1: Map each hardening setting to its mechanism.

**Expected evidence:** Mount writes, capabilities, privilege gain and temporary storage.

**Why:** The settings are complementary rather than synonyms. A clear mapping helps diagnose which boundary rejected an unintended operation.

## Exercise 2: Predict whether read-only root prevents volume writes.

**Expected answer:** A separately writable data mount can still allow them.

**Why:** Permissions are applied to the mounted path involved. The design deliberately separates immutable code from intended mutable state.

## Exercise 3: Write a least-privilege acceptance pair.

**Expected evidence:** One required action succeeds and one forbidden action fails.

**Why:** Checking only failure could describe a broken application. Checking only success could miss unnecessary access.

## Exercise 4: Diagnose an app that needs an undocumented cache directory.

**Expected answer:** Identify the path and provide a bounded intended mount if justified.

**Why:** Do not make the whole root filesystem writable. Determine whether the cache is temporary, durable or avoidable, then choose the smallest correct storage channel.

## Exercise 5: Explain why privileged mode is inappropriate here.

**Expected answer:** It grants broad access unrelated to the HTTP fixture.

**Why:** A privileged container changes the trust boundary substantially. The lesson’s app has no legitimate requirement for device or host-administration capabilities.

## Exercise 6: Review a hardening change without overstating security.

**Expected evidence:** State controls tested and the trusted-local-code boundary.

**Why:** No finite checklist proves a universal sandbox. Report what the actual configuration restricts and which threats remain outside its supported use.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
