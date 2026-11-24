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

The classroom displays this guide and saves your worksheet, `courses/docker/lessons/docker-020.md`. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example. **How to use the lessons** in the [subject README](../README.md) collects these rules in one place.

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

For each exercise, name the object involved and the phase of its lifetime before changing anything, then vary only the condition the task names. Exercises that ask you to predict, explain, compare or diagnose keep their answers in the solutions file; the others show the evidence to look for.

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

Exercise 4 is this chapter's boundary case: Diagnose a bind-mount permission failure. Record the effective UID and GID in the container, the owner and mode of the mounted path on the host, and the exact operation that was denied. Preserve the original failure and the exact changed field before retrying. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations first. Recall the UID and GID the fixture image runs as and which host paths it may write. Then reconstruct worked example 2 (Inspect effective identity without secrets) with one different value, predict what changes, and name which of UID, USER, file ownership and writable data path the change touches.

When a host session ends, run `docker compose -p ds60-docker-study down` from your fixture copy. It removes the project's containers and network but keeps named volumes; deleting a volume is a separate, deliberate reset described in the fixture README.

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
