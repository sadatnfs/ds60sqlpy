# docker-040: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-040.md`.

## Exercise 1: Compare build and runtime secrets.

**Expected answer:** Temporary build input versus application-time input.

**Why:** Their consumers and lifetimes differ. A build-only credential should not be copied into the final runtime image.

## Exercise 2: Predict whether a local secret file is automatically encrypted everywhere.

**Expected answer:** No; host storage and platform behavior require separate protection.

**Why:** The secret abstraction controls delivery, not every storage layer. Describe the actual local Compose implementation honestly.

## Exercise 3: Design a no-disclosure validation message.

**Expected evidence:** Report presence or a bounded error without the sensitive value.

**Why:** Useful diagnostics need not reveal bytes. Avoid including environment dumps, full headers or file contents in error reports.

## Exercise 4: Diagnose a secret declared but not granted to a service.

**Expected answer:** The service lacks the intended mounted input.

**Why:** Check the effective model and service access list before changing file permissions or adding a broad host mount.

## Exercise 5: Explain credential rotation beyond restarting a container.

**Expected answer:** New input must be applied and old authority revoked deliberately.

**Why:** The external service decides which credential remains valid. A process lifecycle event alone cannot establish that policy change.

## Exercise 6: Write a secret data-flow review.

**Expected evidence:** Source, host protection, service grant, read path, logs, rotation and deletion.

**Why:** Following the bytes through their lifetime reveals exposure paths that a single Compose setting cannot address.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
