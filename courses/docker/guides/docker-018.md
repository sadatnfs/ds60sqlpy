# docker-018: Bridge networks, service DNS and container-to-container traffic

## Level and prerequisites

Intermediate; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-017`

## Learning objectives

Draw the DNS-to-request sequence. Design an internal-only database connection. Use bridge network, service DNS and container port accurately when you explain what you observed.

## Purpose, vocabulary and mental model

A bridge network connects container interfaces on one engine. A user-defined bridge provides scoped service discovery and connectivity for attached containers. Compose normally creates such a network for a project. DNS maps a service name to a current reachable address; the name is a better application dependency than a temporary container IP.

The app and client in the fixture communicate using `app:8080`. The client does not need the host’s published port. A container replacement can change its address while the service name remains the intended lookup key. Applications must reconnect and resolve names appropriately rather than retaining a dead connection forever.

Network attachment and authorization are different concerns. Sharing a network can permit connectivity, but an application still needs authentication when serving sensitive operations. Conversely, a private network is not a reason to publish every internal port on the host.

### Key terms

- **Bridge network:** A virtual network on one engine that connects container interfaces; Compose creates a user-defined one per project.
- **Service DNS:** Name resolution that maps a Compose service name such as `app` to a current container address on the network.
- **Container-to-container traffic:** Requests between peers on a shared network, such as client to `app:8080`, that never use the host's published port.
- **Network vantage point:** The namespace a request starts from, which decides what names and addresses such as localhost mean.

## Anatomy and a trace you can follow

The optional client uses Python’s HTTP library and a short timeout. `docker compose run --rm client` creates a short-lived container attached to the project’s network. It resolves `app`, connects to 8080 and prints the JSON response. The fixture marks that service with a tools profile so it does not remain as another server during ordinary startup.

A DNS resolution failure, a refused connection and a valid HTTP error are different observations. Diagnose from the caller’s namespace, because the host may resolve different names and use a different route.

## How to use this lesson

The classroom saves `courses/docker/lessons/docker-018.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** With the project running, resolve the service name from inside the app container: `docker compose -p ds60-docker-study exec app python -c "import socket; print(socket.gethostbyname('app'))"`. Compare the address with the container entry in `docker network inspect ds60-docker-study_default`; they match. Now connect to a port nothing listens on, replacing the lookup with `socket.create_connection(('app', 9999), timeout=2)`: the name resolves but the connection is refused, which separates naming from listening. Finally, force a recreation with `up -d --force-recreate --wait app` and repeat the lookup. The address may change, and the name still works. Print `/etc/resolv.conf` from the same container with Python and note the nameserver `127.0.0.11`: that is the engine's embedded resolver, present only on user-defined networks. Write the before and after addresses in the worksheet; nothing new needs cleaning up.

## Worked example / walkthrough

### Worked example 1: Request from a real peer

Run after the app is healthy in the copied fixture.

```sh
docker compose -p ds60-docker-study --profile tools run --rm client
```

**Expected observation:** The peer prints the app response using `app:8080` without relying on host port 18080.

### Worked example 2: Contrast destination scopes

This diagram names the caller for each address.

```text
host browser: 127.0.0.1:18080
peer client: app:8080
app healthcheck: 127.0.0.1:8080
```

**Expected observation:** The same application is observed through three intentionally different paths.

## Six progressive exercises

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

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

Exercise 4 is this chapter's boundary case: Diagnose DNS success with connection refusal. Record the resolved address, then test whether anything listens on that address and port inside the target container before touching DNS settings.

A misleading experiment is testing service names with two plain `docker run` containers. Without `--network`, both join the engine's default bridge network, which does not provide name resolution between containers, so one cannot resolve the other by name and the learner concludes that container DNS is broken. Compose creates a user-defined network for each project, and user-defined networks do include the embedded DNS service. To reproduce Compose behavior by hand, create a network with `docker network create`, attach both containers with `--network`, and give the target a `--name` or `--network-alias` to resolve.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** Recall which destination the host browser, a peer client and the app healthcheck each use, and why they differ.

**Transfer case.** A second Compose project for monitoring runs a probe that must request `app:8080` in the study project. Both projects are up, and the probe fails with a name resolution error. Explain why and propose the smallest model change.

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

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
