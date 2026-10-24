# docker-009: Ports, loopback and the first browser request

## Level and prerequisites

Beginner; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-008`

## Learning objectives

Draw a host browser request path. Choose public and internal endpoints for a two-service app. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

An IP address identifies a network interface or virtual destination within a network. A port identifies a transport endpoint at that address. A server listens on an address and port inside its own network namespace. Publishing maps a host endpoint to a container endpoint; it does not change the application’s listening configuration.

Loopback refers to the local network namespace. `127.0.0.1` inside a container points back to that container, not to your laptop and not to another service. A server bound only to container loopback is normally unreachable through a mapping to its container network interface. The fixture listens on `0.0.0.0:8080` inside the container and publishes only `127.0.0.1:18080` on the host.

The wildcard address `0.0.0.0` is a listening choice, not a browser destination. Binding a published port to host loopback reduces accidental exposure to other machines. The real boundary also depends on the engine, host firewall and platform networking, so do not describe a port mapping as an authentication system.

## Anatomy and a trace you can follow

Read `127.0.0.1:18080:8080` as host address, host port and container port. A browser on the host requests `http://127.0.0.1:18080/`. A peer container on the same Compose network requests `http://app:8080/` using service discovery. They reach the same application through different paths.

Troubleshoot in layers: application listen address, process state, container port, published mapping, host port conflict, then HTTP path and payload. A connection refused response is different from HTTP 404; the latter means an HTTP server responded but did not serve the requested path.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

## Worked example / walkthrough

### Worked example 1: Publish only to the learner host

The fixture supplies this mapping.

```yaml
ports:
  - "127.0.0.1:18080:8080"
```

**Expected observation:** A host browser uses port 18080; the app still listens on 8080 inside its container.

### Worked example 2: Compare two destinations

Use the first in the host browser and the second only from a network peer.

```text
Host browser -> 127.0.0.1:18080 -> published mapping -> app:8080
Peer container -> DNS name app -> container address:8080
```

**Expected observation:** Loopback and the service name have different scopes; hardcoding the temporary container IP is unnecessary.

## Six progressive exercises

### Exercise 1: Label every component of the mapping.

**Expected evidence:** Host loopback, host port 18080 and container port 8080.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Predict whether localhost:18080 inside app reaches the host browser endpoint.

**Expected evidence:** It refers to app container loopback and normally fails.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Draw a host browser request path.

**Expected evidence:** Browser, host socket mapping, container interface and app listener.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose a server bound to container 127.0.0.1 only.

**Expected evidence:** It may answer locally but not through the published mapping.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Distinguish connection refused from HTTP 404.

**Expected evidence:** Transport failure versus application routing result.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Choose public and internal endpoints for a two-service app.

**Expected evidence:** Only the user-facing service gets a deliberate published port.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose a server bound to container 127.0.0.1 only. Use its expected observation, It may answer locally but not through the published mapping., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/engine/network/port-publishing/)
- [Official reference 2](https://docs.docker.com/engine/network/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-009: Ports, loopback and the first browser request.
Read courses/docker/guides/docker-009.md and courses/docker/lessons/docker-009.md. Direct prerequisites: `docker-008`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
