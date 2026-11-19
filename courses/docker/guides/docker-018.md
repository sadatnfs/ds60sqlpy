# docker-018: Bridge networks, service DNS and container-to-container traffic

## Level and prerequisites

Intermediate; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-017`

## Learning objectives

Draw the DNS-to-request sequence. Design an internal-only database connection. Use bridge network, service DNS and container port accurately when you explain what you observed.

## Purpose, vocabulary and mental model

A bridge network connects container interfaces on one engine. A user-defined bridge provides scoped service discovery and connectivity for attached containers. Compose normally creates such a network for a project. DNS maps a service name to a current reachable address; the name is a better application dependency than a temporary container IP.

The app and client in the fixture communicate using `app:8080`. The client does not need the host’s published port. A container replacement can change its address while the service name remains the intended lookup key. Applications must reconnect and resolve names appropriately rather than retaining a dead connection forever.

Network attachment and authorization are different concerns. Sharing a network can permit connectivity, but an application still needs authentication when serving sensitive operations. Conversely, a private network is not a reason to publish every internal port on the host.

## Anatomy and a trace you can follow

The optional client uses Python’s HTTP library and a short timeout. `docker compose run --rm client` creates a short-lived container attached to the project’s network. It resolves `app`, connects to 8080 and prints the JSON response. The fixture marks that service with a tools profile so it does not remain as another server during ordinary startup.

A DNS resolution failure, a refused connection and a valid HTTP error are different observations. Diagnose from the caller’s namespace, because the host may resolve different names and use a different route.

## How to use this lesson

The classroom displays this guide and saves your worksheet, `courses/docker/lessons/docker-018.md`. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example. **How to use the lessons** in the [subject README](../README.md) collects these rules in one place.

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

For each exercise, name the object involved and the phase of its lifetime before changing anything, then vary only the condition the task names. Exercises that ask you to predict, explain, compare or diagnose keep their answers in the solutions file; the others show the evidence to look for.

### Exercise 1: Predict the name a peer uses for the app.

**Hint:** Look at the service keys in compose.yaml.

### Exercise 2: Explain why a peer should not use host loopback.

**Hint:** Ask whose loopback 127.0.0.1 is inside the peer.

### Exercise 3: Draw the DNS-to-request sequence.

**Hint:** Separate name resolution, the connection and the HTTP exchange.

### Exercise 4: Diagnose DNS success with connection refusal.

**Hint:** Check the port the app listens on inside its container.

### Exercise 5: Predict a reconnect after app recreation.

**Hint:** Ask whether the service name or the IP address stays stable.

### Exercise 6: Design an internal-only database connection.

**Expected evidence:** Use service DNS and container port without host publication.

**Hint:** Decide whether a person on the host needs to reach the database at all.

## Common mistakes and diagnosis

Connecting from one container to another through `localhost`. Using the host port instead of the container port between services. Hard-coding a container IP that changes when the service is recreated.

Exercise 4 is this chapter's boundary case: Diagnose DNS success with connection refusal. Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status; an application request adds another layer, and a healthy container can still serve the wrong result. Preserve the original failure and the exact changed field before retrying. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here, using bridge network, service DNS, container port and network vantage point. Reconstruct worked example 2 (Contrast destination scopes) with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild, or why none of those operations applies to this mechanism.

When a host session ends, run `docker compose -p ds60-docker-study down` from your fixture copy. It removes the project's containers and network but keeps named volumes; deleting a volume is a separate, deliberate reset described in the fixture README.

## Primary references

- [Bridge network driver](https://docs.docker.com/engine/network/drivers/bridge/)
- [Networking in Compose](https://docs.docker.com/compose/how-tos/networking/)

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
