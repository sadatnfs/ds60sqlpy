# docker-023: Read-only filesystems, capabilities and least privilege

## Level and prerequisites

Intermediate; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-022`

## Learning objectives

Write a least-privilege acceptance pair. Review a hardening change without overstating security. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

Linux capabilities divide some traditional root privileges into named permissions. A process can run without unnecessary capabilities even when an image was built by root. A read-only root filesystem limits writes to packaged paths, while explicit mounts provide the few writable locations the application requires.

`no-new-privileges` prevents a process from gaining privileges through mechanisms such as set-user-ID execution. A process-ID limit bounds process creation. These controls address different mechanisms. Combining them intentionally is more useful than copying a hardening block without understanding which operation each setting permits or refuses.

The local classroom executes trusted learner code and is not a public hostile-code hosting boundary. The Docker study fixture still demonstrates least privilege: no engine socket, no privileged mode, non-root identity, dropped capabilities, read-only root and bounded temporary storage. These settings must be tested against actual functionality.

## Anatomy and a trace you can follow

In Compose, `cap_drop: [ALL]` drops the default capability set. `read_only: true` changes the root mount. `tmpfs` gives a small temporary path. The app listens on an unprivileged port and writes retained data only to its declared volume. No control should be disabled merely to hide a missing permission contract.

A useful hardening test has two halves: intended behavior still works, and an unintended operation fails. The fixture should answer health and preserve its counter, while writing a new file under `/app` should fail. A control that silently prevents all useful work is not a successful configuration.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

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

### Exercise 1: Map each hardening setting to its mechanism.

**Expected evidence:** Mount writes, capabilities, privilege gain and temporary storage.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Predict whether read-only root prevents volume writes.

**Expected evidence:** A separately writable data mount can still allow them.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Write a least-privilege acceptance pair.

**Expected evidence:** One required action succeeds and one forbidden action fails.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose an app that needs an undocumented cache directory.

**Expected evidence:** Identify the path and provide a bounded intended mount if justified.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Explain why privileged mode is inappropriate here.

**Expected evidence:** It grants broad access unrelated to the HTTP fixture.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Review a hardening change without overstating security.

**Expected evidence:** State controls tested and the trusted-local-code boundary.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose an app that needs an undocumented cache directory. Use its expected observation, Identify the path and provide a bounded intended mount if justified., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/engine/security/)
- [Official reference 2](https://docs.docker.com/reference/compose-file/services/#cap_drop)

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
