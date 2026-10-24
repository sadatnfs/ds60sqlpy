# docker-018: Bridge networks, service DNS and container-to-container traffic

## Level and prerequisites

Intermediate; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-017`

## Learning objectives

Draw the DNS-to-request sequence. Design an internal-only database connection. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

A bridge network connects container interfaces on one engine. A user-defined bridge provides scoped service discovery and connectivity for attached containers. Compose normally creates such a network for a project. DNS maps a service name to a current reachable address; the name is a better application dependency than a temporary container IP.

The app and client in the fixture communicate using `app:8080`. The client does not need the host’s published port. A container replacement can change its address while the service name remains the intended lookup key. Applications must reconnect and resolve names appropriately rather than retaining a dead connection forever.

Network attachment and authorization are different concerns. Sharing a network can permit connectivity, but an application still needs authentication when serving sensitive operations. Conversely, a private network is not a reason to publish every internal port on the host.

## Anatomy and a trace you can follow

The optional client uses Python’s HTTP library and a short timeout. `docker compose run --rm client` creates a short-lived container attached to the project’s network. It resolves `app`, connects to 8080 and prints the JSON response. The fixture marks that service with a tools profile so it does not remain as another server during ordinary startup.

A DNS resolution failure, a refused connection and a valid HTTP error are different observations. Diagnose from the caller’s namespace, because the host may resolve different names and use a different route.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

## Worked example / walkthrough

### Worked example 1: Request from a real peer

Run after the app is healthy in the copied fixture.

```sh
docker compose -p ds60-docker-study --profile tools run --rm client
```

**Expected observation:** The peer prints the app response using app:8080 without relying on host port 18080.

### Worked example 2: Contrast destination scopes

This diagram names the caller for each address.

```text
host browser: 127.0.0.1:18080
peer client: app:8080
app healthcheck: 127.0.0.1:8080
```

**Expected observation:** The same application is observed through three intentionally different paths.

## Six progressive exercises

### Exercise 1: Predict the name a peer uses for the app.

**Expected evidence:** The Compose service name app.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Explain why a peer should not use host loopback.

**Expected evidence:** Its loopback refers to the peer itself.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Draw the DNS-to-request sequence.

**Expected evidence:** Resolve app, connect to container port, send HTTP request, inspect body.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose DNS success with connection refusal.

**Expected evidence:** The destination resolved but no reachable listener accepted that port.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Predict a reconnect after app recreation.

**Expected evidence:** A fresh lookup and connection can reach the new instance.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Design an internal-only database connection.

**Expected evidence:** Use service DNS and container port without host publication.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose DNS success with connection refusal. Use its expected observation, The destination resolved but no reachable listener accepted that port., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/engine/network/drivers/bridge/)
- [Official reference 2](https://docs.docker.com/compose/how-tos/networking/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-018: Bridge networks, service DNS and container-to-container traffic.
Read courses/docker/guides/docker-018.md and courses/docker/lessons/docker-018.md. Direct prerequisites: `docker-017`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
