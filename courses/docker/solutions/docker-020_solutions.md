# docker-020: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-020.md`.

## Exercise 1: Predict whether matching usernames guarantee file access.

**Expected answer:** No; numeric identity and permission bits matter.

**Why:** Names are lookup labels. Compare numeric IDs and the actual mount ownership before diagnosing a cross-environment permission mismatch.

## Exercise 2: Separate read-only code and writable data paths.

**Expected evidence:** /app is code, /data is retained application state.

**Why:** This layout limits accidental code mutation while allowing the app’s intended state changes. Do not make the entire filesystem writable to support one data directory.

## Exercise 3: Design a non-root image setup sequence.

**Expected evidence:** Create required paths, set ownership, then select the runtime user.

**Why:** The sequence makes startup deterministic. Deferring broad permission changes to every launch can hide incorrect packaging and require unnecessary privilege.

## Exercise 4: Diagnose a bind-mount permission failure.

**Expected answer:** Identify mount path, effective UID and exact denied operation.

**Why:** A targeted observation narrows the repair. Recursive host ownership changes can damage a developer checkout and are not a general container fix.

## Exercise 5: Explain why chmod 777 weakens the evidence.

**Expected answer:** It allows more writers instead of proving intended ownership.

**Why:** The repaired system no longer tests the same access contract. Prefer the smallest permission change that grants the required operation to the intended identity.

## Exercise 6: Write a permission acceptance check.

**Expected evidence:** Non-root process can write data and cannot mutate packaged code.

**Why:** Both positive and negative checks matter. Successful persistence alone does not prove that code paths remain protected from accidental writes.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
