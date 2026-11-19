# docker-023: Read-only filesystems, capabilities and least privilege

## Level and prerequisites

Intermediate; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-022`

## Learning objectives

Write a least-privilege acceptance pair. Review a hardening change without overstating security. Use Linux capabilities, cap_drop and read-only filesystem accurately when you explain what you observed.

## Purpose, vocabulary and mental model

Linux capabilities divide some traditional root privileges into named permissions. A process can run without unnecessary capabilities even when an image was built by root. A read-only root filesystem limits writes to packaged paths, while explicit mounts provide the few writable locations the application requires.

`no-new-privileges` prevents a process from gaining privileges through mechanisms such as set-user-ID execution. A process-ID limit bounds process creation. These controls address different mechanisms. Combining them intentionally is more useful than copying a hardening block without understanding which operation each setting permits or refuses.

The local classroom executes trusted learner code and is not a public hostile-code hosting boundary. The Docker study fixture still demonstrates least privilege: no engine socket, no privileged mode, non-root identity, dropped capabilities, read-only root and bounded temporary storage. These settings must be tested against actual functionality.

## Anatomy and a trace you can follow

In Compose, `cap_drop: [ALL]` drops the default capability set. `read_only: true` changes the root mount. `tmpfs` gives a small temporary path. The app listens on an unprivileged port and writes retained data only to its declared volume. No control should be disabled merely to hide a missing permission contract.

A useful hardening test has two halves: intended behavior still works, and an unintended operation fails. The fixture should answer health and preserve its counter, while writing a new file under `/app` should fail. A control that silently prevents all useful work is not a successful configuration.

## How to use this lesson

The classroom displays this guide and saves your worksheet, `courses/docker/lessons/docker-023.md`. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example. **How to use the lessons** in the [subject README](../README.md) collects these rules in one place.

## Worked example / walkthrough

### Worked example 1: Inspect the fixture hardening model

These settings belong to the app service.

```yaml
read_only: true
cap_drop: [ALL]
security_opt:
  - no-new-privileges:true
tmpfs:
  - /tmp:rw,noexec,nosuid,size=16m
```

**Expected observation:** The app has narrow writable locations and no requested Linux capabilities.

### Worked example 2: Separate positive and negative acceptance

This is the intended evidence pair.

```text
positive: GET /healthz succeeds; counter persists
negative: writing /app/unexpected.txt fails
```

**Expected observation:** Least privilege retains the app contract while denying unrelated writes.

## Six progressive exercises

For each exercise, name the object involved and the phase of its lifetime before changing anything, then vary only the condition the task names. Exercises that ask you to predict, explain, compare or diagnose keep their answers in the solutions file; the others show the evidence to look for.

### Exercise 1: Map each hardening setting to its mechanism.

**Expected evidence:** Mount writes, capabilities, privilege gain and temporary storage.

**Hint:** Take each security line in compose.yaml and name the kernel feature behind it.

### Exercise 2: Predict whether read-only root prevents volume writes.

**Hint:** List the container's mounts and the write policy of each.

### Exercise 3: Write a least-privilege acceptance pair.

**Expected evidence:** One required action succeeds and one forbidden action fails.

**Hint:** Pick one action the app needs and one it must never do, and test both.

### Exercise 4: Diagnose an app that needs an undocumented cache directory.

**Hint:** Find the path in the error message before adding any mount.

### Exercise 5: Explain why privileged mode is inappropriate here.

**Hint:** List what --privileged grants and compare it with what the HTTP server needs.

### Exercise 6: Review a hardening change without overstating security.

**Expected evidence:** State controls tested and the trusted-local-code boundary.

**Hint:** Name the settings you tested and the threats they do not address.

## Common mistakes and diagnosis

Adding capabilities or `--privileged` until an error disappears. Removing `read_only` instead of mounting the one path the app must write. Calling the container secure because it runs as non-root.

Exercise 4 is this chapter's boundary case: Diagnose an app that needs an undocumented cache directory. Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status; an application request adds another layer, and a healthy container can still serve the wrong result. Preserve the original failure and the exact changed field before retrying. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here, using Linux capabilities, cap_drop, read-only filesystem, no-new-privileges and least privilege. Reconstruct worked example 2 (Separate positive and negative acceptance) with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild, or why none of those operations applies to this mechanism.

When a host session ends, run `docker compose -p ds60-docker-study down` from your fixture copy. It removes the project's containers and network but keeps named volumes; deleting a volume is a separate, deliberate reset described in the fixture README.

## Primary references

- [Docker Engine security](https://docs.docker.com/engine/security/)
- [Compose file reference: cap_drop](https://docs.docker.com/reference/compose-file/services/#cap_drop)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-023: Read-only filesystems, capabilities and least privilege.
Read courses/docker/guides/docker-023.md and courses/docker/lessons/docker-023.md. Direct prerequisites: `docker-022`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
