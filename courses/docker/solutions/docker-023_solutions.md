# docker-023: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

Linux capabilities divide some traditional root privileges into named permissions. A process can run without unnecessary capabilities even when an image was built by root. A read-only root filesystem limits writes to packaged paths, while explicit mounts provide the few writable locations the application requires.

`no-new-privileges` prevents a process from gaining privileges through mechanisms such as set-user-ID execution. A process-ID limit bounds process creation. These controls address different mechanisms. Combining them intentionally is more useful than copying a hardening block without understanding which operation each setting permits or refuses.

The local classroom executes trusted learner code and is not a public hostile-code hosting boundary. The Docker study fixture still demonstrates least privilege: no engine socket, no privileged mode, non-root identity, dropped capabilities, read-only root and bounded temporary storage. These settings must be tested against actual functionality.

In Compose, `cap_drop: [ALL]` drops the default capability set. `read_only: true` changes the root mount. `tmpfs` gives a small temporary path. The app listens on an unprivileged port and writes retained data only to its declared volume. No control should be disabled merely to hide a missing permission contract.

A useful hardening test has two halves: intended behavior still works, and an unintended operation fails. The fixture should answer health and preserve its counter, while writing a new file under `/app` should fail. A control that silently prevents all useful work is not a successful configuration.

## Exercise 1: Map each hardening setting to its mechanism.

The settings are complementary rather than synonyms. A clear mapping helps diagnose which boundary rejected an unintended operation.

**Expected:** Mount writes, capabilities, privilege gain and temporary storage.

## Exercise 2: Predict whether read-only root prevents volume writes.

Permissions are applied to the mounted path involved. The design deliberately separates immutable code from intended mutable state.

**Expected:** A separately writable data mount can still allow them.

## Exercise 3: Write a least-privilege acceptance pair.

Checking only failure could describe a broken application. Checking only success could miss unnecessary access.

**Expected:** One required action succeeds and one forbidden action fails.

## Exercise 4: Diagnose an app that needs an undocumented cache directory.

Do not make the whole root filesystem writable. Determine whether the cache is temporary, durable or avoidable, then choose the smallest correct storage channel.

**Expected:** Identify the path and provide a bounded intended mount if justified.

## Exercise 5: Explain why privileged mode is inappropriate here.

A privileged container changes the trust boundary substantially. The lesson’s app has no legitimate requirement for device or host-administration capabilities.

**Expected:** It grants broad access unrelated to the HTTP fixture.

## Exercise 6: Review a hardening change without overstating security.

No finite checklist proves a universal sandbox. Report what the actual configuration restricts and which threats remain outside its supported use.

**Expected:** State controls tested and the trusted-local-code boundary.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
