# docker-020: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

A user ID, or UID, is a numeric operating-system identity used for ownership and permission checks. A username is a label mapped to that number. The same username on the host and in a container can refer to different numbers. File access follows effective identities and mount behavior, not matching display names.

Running an application as a non-root user reduces the privileges of its ordinary process. It does not make a hostile program harmless or replace container isolation. The image must arrange readable application files and an intentionally writable data directory before switching users.

Bind mounts expose host ownership more directly than an image’s files. Broad recursive ownership changes on a host project can break unrelated files. Diagnose the exact UID, path and mount before modifying permissions. A named teaching volume can have a deliberately prepared owner without changing your repository ownership.

The fixture creates `/data`, assigns it to UID 10001 and uses `USER 10001:10001`. Application code is readable and the root filesystem is read-only at runtime. The named volume is mounted at the intended data path. Check the actual mounted permissions rather than assuming every volume driver behaves identically.

A permission denied error is a useful boundary. Inspect identity and path. Do not respond with `chmod -R 777`, privileged mode or a blanket root user. Those changes can make the symptom disappear while invalidating the intended operating contract.

## Exercise 1: Predict whether matching usernames guarantee file access.

Names are lookup labels. Compare numeric IDs and the actual mount ownership before diagnosing a cross-environment permission mismatch.

**Expected:** No; numeric identity and permission bits matter.

## Exercise 2: Separate read-only code and writable data paths.

This layout limits accidental code mutation while allowing the app’s intended state changes. Do not make the entire filesystem writable to support one data directory.

**Expected:** /app is code, /data is retained application state.

## Exercise 3: Design a non-root image setup sequence.

The sequence makes startup deterministic. Deferring broad permission changes to every launch can hide incorrect packaging and require unnecessary privilege.

**Expected:** Create required paths, set ownership, then select the runtime user.

## Exercise 4: Diagnose a bind-mount permission failure.

A targeted observation narrows the repair. Recursive host ownership changes can damage a developer checkout and are not a general container fix.

**Expected:** Identify mount path, effective UID and exact denied operation.

## Exercise 5: Explain why chmod 777 weakens the evidence.

The repaired system no longer tests the same access contract. Prefer the smallest permission change that grants the required operation to the intended identity.

**Expected:** It allows more writers instead of proving intended ownership.

## Exercise 6: Write a permission acceptance check.

Both positive and negative checks matter. Successful persistence alone does not prove that code paths remain protected from accidental writes.

**Expected:** Non-root process can write data and cannot mutate packaged code.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
