# docker-020: Users, UID ownership and writable data paths

## Level and prerequisites

Intermediate; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-019`

## Learning objectives

Design a non-root image setup sequence. Write a permission acceptance check. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

A user ID, or UID, is a numeric operating-system identity used for ownership and permission checks. A username is a label mapped to that number. The same username on the host and in a container can refer to different numbers. File access follows effective identities and mount behavior, not matching display names.

Running an application as a non-root user reduces the privileges of its ordinary process. It does not make a hostile program harmless or replace container isolation. The image must arrange readable application files and an intentionally writable data directory before switching users.

Bind mounts expose host ownership more directly than an image’s files. Broad recursive ownership changes on a host project can break unrelated files. Diagnose the exact UID, path and mount before modifying permissions. A named teaching volume can have a deliberately prepared owner without changing your repository ownership.

## Anatomy and a trace you can follow

The fixture creates `/data`, assigns it to UID 10001 and uses `USER 10001:10001`. Application code is readable and the root filesystem is read-only at runtime. The named volume is mounted at the intended data path. Check the actual mounted permissions rather than assuming every volume driver behaves identically.

A permission denied error is a useful boundary. Inspect identity and path. Do not respond with `chmod -R 777`, privileged mode or a blanket root user. Those changes can make the symptom disappear while invalidating the intended operating contract.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

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

### Exercise 1: Predict whether matching usernames guarantee file access.

**Expected evidence:** No; numeric identity and permission bits matter.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Separate read-only code and writable data paths.

**Expected evidence:** /app is code, /data is retained application state.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Design a non-root image setup sequence.

**Expected evidence:** Create required paths, set ownership, then select the runtime user.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose a bind-mount permission failure.

**Expected evidence:** Identify mount path, effective UID and exact denied operation.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Explain why chmod 777 weakens the evidence.

**Expected evidence:** It allows more writers instead of proving intended ownership.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Write a permission acceptance check.

**Expected evidence:** Non-root process can write data and cannot mutate packaged code.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose a bind-mount permission failure. Use its expected observation, Identify mount path, effective UID and exact denied operation., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/reference/dockerfile/#user)
- [Official reference 2](https://docs.docker.com/engine/security/userns-remap/)

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
