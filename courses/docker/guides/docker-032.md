# docker-032: Debugging minimal images without changing the contract

## Level and prerequisites

Advanced; about 120 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-031`

## Learning objectives

Create a vantage-point diagnosis table. Write a repeatable minimal-image incident procedure. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

A minimal image may omit a shell, curl, a package manager or debugging tools. Their absence can reduce image size and unnecessary functionality, but it changes how you inspect failures. An application can be correct without a shell; an attempted `docker exec ... sh` failure may describe tooling, not the application.

Debugging should preserve the original artifact and evidence. Installing tools into a live container changes its writable layer and can hide the conditions that caused the failure. Prefer structured inspection, existing runtime libraries, bounded logs and an explicitly prepared diagnostic workflow.

A separate debug image or ephemeral diagnostic container can be useful when its permissions, network access and data exposure are deliberately scoped. It must not become an excuse to mount the whole host or attach to unrelated production workloads.

## Anatomy and a trace you can follow

The fixture already has Python, so a short standard-library request can test HTTP without adding curl. Use container inspection for configuration and logs for application behavior. If you need a shell in a different project, verify that the selected image actually contains one.

Record whether each diagnostic ran inside the app container, a peer container or the host. The vantage point determines which DNS names, loopback address, files and permissions were observed.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

## Worked example / walkthrough

### Worked example 1: Use a prepared runtime as a diagnostic

This uses the app’s existing Python standard library.

```sh
docker compose -p ds60-docker-study exec app python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=2).read().decode())"
```

**Expected observation:** A bounded internal health response, with no package installation.

### Worked example 2: Label observations by vantage point

A compact incident table should preserve this distinction.

```text
host: published mapping and browser request
peer: service DNS and internal network
app: local listener, filesystem and effective UID
```

**Expected observation:** Different results can localize a failure rather than contradict one another.

## Six progressive exercises

### Exercise 1: Predict a missing-shell error in a minimal image.

**Expected evidence:** It may be expected image content, not an app crash.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Choose a prepared tool for one HTTP request.

**Expected evidence:** Use Python already present in the fixture.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Create a vantage-point diagnosis table.

**Expected evidence:** Host, peer and app observations with distinct address scopes.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose an interactive repair that cannot survive recreation.

**Expected evidence:** The maintained image was never changed.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Explain why host filesystem mounts are excessive for this lab.

**Expected evidence:** They expose data unrelated to the app diagnosis.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Write a repeatable minimal-image incident procedure.

**Expected evidence:** Preserve artifact, inspect state, run bounded prepared probes and test a source repair.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose an interactive repair that cannot survive recreation. Use its expected observation, The maintained image was never changed., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/reference/cli/docker/container/exec/)
- [Official reference 2](https://docs.docker.com/engine/containers/run/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-032: Debugging minimal images without changing the contract.
Read courses/docker/guides/docker-032.md and courses/docker/lessons/docker-032.md. Direct prerequisites: `docker-031`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
