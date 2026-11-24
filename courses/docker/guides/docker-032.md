# docker-032: Debugging minimal images without changing the contract

## Level and prerequisites

Advanced; about 120 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-031`

## Learning objectives

Create a vantage-point diagnosis table. Write a repeatable minimal-image incident procedure. Use minimal image, debug container and shared namespaces accurately when you explain what you observed.

## Purpose, vocabulary and mental model

A minimal image may omit a shell, curl, a package manager or debugging tools. Their absence can reduce image size and unnecessary functionality, but it changes how you inspect failures. An application can be correct without a shell; an attempted `docker exec ... sh` failure may describe tooling, not the application.

Debugging should preserve the original artifact and evidence. Installing tools into a live container changes its writable layer and can hide the conditions that caused the failure. Prefer structured inspection, existing runtime libraries, bounded logs and an explicitly prepared diagnostic workflow.

A separate debug image or ephemeral diagnostic container can be useful when its permissions, network access and data exposure are deliberately scoped. `docker run --rm -it --pid=container:APP --network=container:APP TOOLS_IMAGE` starts a tools container that sees the app container's processes and network stack while the app image stays unchanged. It must not become an excuse to mount the whole host or attach to unrelated production workloads.

### Key terms

- **Minimal image:** An image that omits a shell, package manager and debugging tools to reduce size and unneeded functionality.
- **Debug container:** A separate, short-lived tools container started deliberately to inspect a running application.
- **Shared namespaces:** Joining another container's process or network namespace, so a tools container sees the app's processes and network stack.
- **Diagnostic vantage point:** The namespace and permissions a diagnostic command runs with, which decide what it can actually observe.

## Anatomy and a trace you can follow

The fixture already has Python, so a short standard-library request can test HTTP without adding curl. Use container inspection for configuration and logs for application behavior. If you need a shell in a different project, verify that the selected image actually contains one.

Record whether each diagnostic ran inside the app container, a peer container or the host. The vantage point determines which DNS names, loopback address, files and permissions were observed.

## How to use this lesson

The classroom displays this guide and saves your worksheet, `courses/docker/lessons/docker-032.md`. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example. **How to use the lessons** in the [subject README](../README.md) collects these rules in one place.

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

For each exercise, name the object involved and the phase of its lifetime before changing anything, then vary only the condition the task names. Exercises that ask you to predict, explain, compare or diagnose keep their answers in the solutions file; the others show the evidence to look for.

### Exercise 1: Predict a missing-shell error in a minimal image.

**Hint:** Ask whether the image was ever meant to contain sh.

### Exercise 2: Choose a prepared tool for one HTTP request.

**Hint:** Look for a runtime the image already includes.

### Exercise 3: Create a vantage-point diagnosis table.

**Expected evidence:** Host, peer and app observations with distinct address scopes.

**Hint:** Record each probe's location: host, peer or app container.

### Exercise 4: Diagnose an interactive repair that cannot survive recreation.

**Hint:** Ask what docker compose up does to changes made with docker exec.

### Exercise 5: Explain why host filesystem mounts are excessive for this lab.

**Hint:** Ask what data a host filesystem mount would expose.

### Exercise 6: Write a repeatable minimal-image incident procedure.

**Expected evidence:** Preserve artifact, inspect state, run bounded prepared probes and test a source repair.

**Hint:** Write the order: preserve, inspect, probe, repair in source, retest.

## Common mistakes and diagnosis

Installing tools into a live container and losing the original evidence. Reading a missing shell as an application crash. Mounting the host filesystem to debug a single HTTP endpoint.

Exercise 4 is this chapter's boundary case: Diagnose an interactive repair that cannot survive recreation. Write down what the interactive change revealed, then recreate the container from the maintained image to confirm the repair is gone. Preserve the original failure and the exact changed field before retrying. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations first. Name one observation from each vantage point, host, peer and app, without looking back. Then reconstruct worked example 2 (Label observations by vantage point) with one different value, predict what changes, and name which of minimal image, debug container, shared namespaces and diagnostic vantage point the change touches.

When a host session ends, run `docker compose -p ds60-docker-study down` from your fixture copy. It removes the project's containers and network but keeps named volumes; deleting a volume is a separate, deliberate reset described in the fixture README.

## Primary references

- [docker container exec reference](https://docs.docker.com/reference/cli/docker/container/exec/)
- [Running containers](https://docs.docker.com/engine/containers/run/)

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
