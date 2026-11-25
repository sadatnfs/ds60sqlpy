# docker-023: Read-only filesystems, capabilities and least privilege

## Level and prerequisites

Intermediate; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-022`

## Learning objectives

Write a least-privilege acceptance pair. Review a hardening change without overstating security. Use Linux capabilities, cap_drop and read-only filesystem accurately when you explain what you observed.

## Purpose, vocabulary and mental model

Linux capabilities divide some traditional root privileges into named permissions. A process can run without unnecessary capabilities even when an image was built by root. A read-only root filesystem limits writes to packaged paths, while explicit mounts provide the few writable locations the application requires.

`no-new-privileges` prevents a process from gaining privileges through mechanisms such as set-user-ID execution. A process-ID limit bounds process creation. These controls address different mechanisms. Combining them intentionally is more useful than copying a hardening block without understanding which operation each setting permits or refuses.

The local classroom executes trusted learner code and is not a public hostile-code hosting boundary. The Docker study fixture still demonstrates least privilege: no engine socket, no privileged mode, non-root identity, dropped capabilities, read-only root and bounded temporary storage. These settings must be tested against actual functionality.

### Key terms

- **Linux capabilities:** Named pieces of traditional root privilege that can be granted or dropped individually.
- **`cap_drop`:** The Compose setting that removes listed capabilities, often `ALL`, from a service's processes.
- **`read_only`:** The Compose setting that makes a container's root filesystem read-only, leaving only explicit mounts writable.
- **`no-new-privileges`:** A security option that stops a process from gaining privileges through set-user-ID programs or similar mechanisms.
- **Least privilege:** Granting a process only the permissions its real work needs, then testing that the application still functions.

## Anatomy and a trace you can follow

In Compose, `cap_drop: [ALL]` drops the default capability set. `read_only: true` changes the root mount. `tmpfs` gives a small temporary path. The app listens on an unprivileged port and writes retained data only to its declared volume. No control should be disabled merely to hide a missing permission contract.

A useful hardening test has two halves: intended behavior still works, and an unintended operation fails. The fixture should answer health and preserve its counter, while writing a new file under `/app` should fail. A control that silently prevents all useful work is not a successful configuration.

## How to use this lesson

The classroom saves `courses/docker/lessons/docker-023.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** Read the effective security state of the running app rather than the YAML: `docker compose -p ds60-docker-study exec app grep -E 'CapEff|NoNewPrivs' /proc/self/status` should show `CapEff` as all zeros and `NoNewPrivs` as 1. For comparison, run a throwaway container as root without the fixture settings, `docker run --rm --pull never --user 0 ds60-docker-study:local grep CapEff /proc/self/status`, and note the nonzero default set. Then add `--cap-drop ALL` and try `python -c "import os; os.chown('/app/server.py', 1, 1)"`: even root is refused, because changing ownership needs `CAP_CHOWN`. Finish with `docker inspect` on the app container and read `HostConfig.CapDrop`, `ReadonlyRootfs` and `SecurityOpt`. Nothing here changes the project.

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

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

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

Exercise 4 is this chapter's boundary case: Diagnose an app that needs an undocumented cache directory. Read the application's error for the exact path it tried to write, then decide whether that cache is temporary, durable or avoidable before choosing a mount.

A review trap is checking hardening only in the Compose file. The file describes what Compose asks for, but the running container is what matters, and run-time flags can change it: a `docker run` of the same image with `--user 0` or `--cap-add`, or a later override file, can undo a setting the reviewed YAML still shows. Verify the live container with `docker inspect`, reading `HostConfig.CapDrop`, `HostConfig.ReadonlyRootfs` and `HostConfig.SecurityOpt`, and confirm from inside with `/proc/self/status`, so the evidence describes the process you are actually trusting.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** Name the positive and negative acceptance checks and what each would show if the root filesystem were writable.

**Transfer case.** A vendor image's documentation says it needs `CAP_NET_ADMIN` for networking. Your deployment only serves HTTP on 8080 behind a published port. How do you decide whether to grant the capability, and what evidence do you collect?

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

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
