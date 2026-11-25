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

The classroom saves `courses/docker/lessons/docker-032.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** Collect the three views without installing anything. From the host, run `curl -s http://127.0.0.1:18080/healthz`. From a peer, run the `tools` client, which reaches `app:8080` by service name. From inside, use the fixture's own Python as worked example 1 shows. Then try `docker compose -p ds60-docker-study exec app curl -s http://127.0.0.1:8080/healthz`: the slim image ships no `curl`, so the engine reports that the executable was not found, which describes the image, not the app. For process evidence, `docker compose -p ds60-docker-study top app` reads the process list from the host side, and because the service sets `init: true` it shows a small init process with `python server.py` as its child. Record each result under its vantage point. There is nothing to clean up.

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

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

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

Exercise 4 is this chapter's boundary case: Diagnose an interactive repair that cannot survive recreation. Write down what the interactive change revealed, then recreate the container from the maintained image to confirm the repair is gone.

The address `127.0.0.1` means a different machine depending on where a command runs, and debugging sessions mix these up constantly. Inside the app container it is the app's own loopback, where port 8080 answers. Inside a separate helper container on the project network it is the helper itself, so a request to `127.0.0.1:8080` there is refused even though nothing is wrong, while `app:8080` works. A helper started with `--network container:` and the app's container name shares the app's network namespace, and then its loopback is the app's again. On the host it is the host, where only the published 18080 answers. Before reading a refused connection as a fault, write down which network namespace the command ran in.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** Name one observation from each vantage point, host, peer and app, without looking back.

**Transfer case.** The host request to `127.0.0.1:18080` times out, yet the peer client and the in-container health request both succeed. Which layer is at fault, and what would you check first?

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

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
