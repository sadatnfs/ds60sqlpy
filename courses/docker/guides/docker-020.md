# docker-020: Users, UID ownership and writable data paths

## Level and prerequisites

Intermediate; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-019`

## Learning objectives

Design a non-root image setup sequence. Write a permission acceptance check. Use UID, USER and file ownership accurately when you explain what you observed.

## Purpose, vocabulary and mental model

A user ID, or UID, is a numeric operating-system identity used for ownership and permission checks. A username is a label mapped to that number. The same username on the host and in a container can refer to different numbers. File access follows effective identities and mount behavior, not matching display names.

Running an application as a non-root user reduces the privileges of its ordinary process. It does not make a hostile program harmless or replace container isolation. The image must arrange readable application files and an intentionally writable data directory before switching users.

Bind mounts expose host ownership more directly than an image’s files. Broad recursive ownership changes on a host project can break unrelated files. Diagnose the exact UID, path and mount before modifying permissions. A named teaching volume can have a deliberately prepared owner without changing your repository ownership.

### Key terms

- **UID:** A numeric user ID that the kernel uses for ownership and permission checks, independent of any username label.
- **`USER`:** The Dockerfile instruction that sets the user, by name or UID, that later steps and the container process run as.
- **File ownership:** The user and group IDs recorded on a file, which together with its mode decide who can read or write it.
- **Writable data path:** A directory such as /data that the image deliberately prepares as writable for the non-root process.
- **Non-root user:** A process identity other than UID 0, which reduces the ordinary privileges of the application.

## Anatomy and a trace you can follow

The fixture creates `/data`, assigns it to UID 10001 and uses `USER 10001:10001`. Application code is readable and the root filesystem is read-only at runtime. The named volume is mounted at the intended data path. Check the actual mounted permissions rather than assuming every volume driver behaves identically.

A permission denied error is a useful boundary. Inspect identity and path. Do not respond with `chmod -R 777`, privileged mode or a blanket root user. Those changes can make the symptom disappear while invalidating the intended operating contract.

## How to use this lesson

The classroom saves `courses/docker/lessons/docker-020.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** Run worked example 2, then override the identity at run time: `docker run --rm --pull never --user 0:0 ds60-docker-study:local python -c "import os; print(os.getuid())"` prints 0. `USER` in a Dockerfile is a default, and any `docker run` caller can change it. Next, make a scratch host folder with `mkdir hostdata`, record `ls -ldn hostdata`, and try to write into it from the fixture image with `-v "$PWD/hostdata:/data"`. On a native Linux engine the write is denied because UID 10001 does not own the folder; Docker Desktop's file sharing may translate ownership and allow it. Record which you saw. Repeat with `--user "$(id -u):$(id -g)"`, which matches the folder owner without widening permissions. Remove `hostdata` when you finish.

## Worked example / walkthrough

### Worked example 1: Declare the image identity

This Dockerfile fragment runs during image construction.

```dockerfile
RUN mkdir -p /data && chown 10001:10001 /data
USER 10001:10001
```

**Expected observation:** The app defaults to the numeric unprivileged identity and has a deliberate data path.

### Worked example 2: Inspect effective identity without secrets

The process prints only numeric identity fields.

```sh
docker run --rm --pull never ds60-docker-study:local python -c "import os; print(os.getuid(), os.getgid())"
```

**Expected observation:** 10001 10001 for the maintained fixture image.

## Six progressive exercises

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

### Exercise 1: Predict whether matching usernames guarantee file access.

**Hint:** Compare numeric UIDs on both sides, not names.

### Exercise 2: Separate read-only code and writable data paths.

**Expected evidence:** /app is code, /data is retained application state.

**Hint:** Ask which paths the app must write at runtime.

### Exercise 3: Design a non-root image setup sequence.

**Expected evidence:** Create required paths, set ownership, then select the runtime user.

**Hint:** Create the directories and set ownership before the USER instruction.

### Exercise 4: Diagnose a bind-mount permission failure.

**Hint:** Compare the host directory's owner with the container's UID.

### Exercise 5: Explain why chmod 777 weakens the evidence.

**Hint:** Ask who else can write after the change.

### Exercise 6: Write a permission acceptance check.

**Expected evidence:** Non-root process can write data and cannot mutate packaged code.

**Hint:** Test one write that must succeed and one that must fail.

## Common mistakes and diagnosis

Fixing permission errors with `chmod -R 777`. Running as root because a bind mount is owned by another UID. Placing writable data under the code directory.

Exercise 4 is this chapter's boundary case: Diagnose a bind-mount permission failure. Record the effective UID and GID in the container, the owner and mode of the mounted path on the host, and the exact operation that was denied.

A related surprise is that `COPY` ignores the current `USER`. Files copied into an image are owned by root unless the instruction says `--chown`, so a Dockerfile that switches to `USER 10001` and then copies a config file leaves the app unable to rewrite that file at runtime. In the fixture this behavior is intended: `/app/server.py` stays root owned and read-only to the app. Use `COPY --chown=10001:10001` only for a path the process must change, and prefer keeping such state under `/data`, where ownership was set on purpose.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** Recall the UID and GID the fixture image runs as and which host paths it may write.

**Transfer case.** A service used to run as root and now runs as UID 10001. Its existing named volume at `/data` was filled during the root era. After the change, writes fail with `PermissionError` on `counter.next`. Why did the Dockerfile's `chown` not help, and what is the repair?

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

## Primary references

- [Dockerfile reference: USER](https://docs.docker.com/reference/dockerfile/#user)
- [User namespace remapping](https://docs.docker.com/engine/security/userns-remap/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-020: Users, UID ownership and writable data paths.
Read courses/docker/guides/docker-020.md and courses/docker/lessons/docker-020.md. Direct prerequisites: `docker-019`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
