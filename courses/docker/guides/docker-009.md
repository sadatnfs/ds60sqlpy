# docker-009: Ports, loopback and the first browser request

## Level and prerequisites

Beginner; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-008`

## Learning objectives

Draw a host browser request path. Choose public and internal endpoints for a two-service app. Use port publishing, loopback address and bind address accurately when you explain what you observed.

## Purpose, vocabulary and mental model

An IP address identifies a network interface or virtual destination within a network. A port identifies a transport endpoint at that address. A server listens on an address and port inside its own network namespace. Publishing maps a host endpoint to a container endpoint; it does not change the application’s listening configuration.

Loopback refers to the local network namespace. `127.0.0.1` inside a container points back to that container, not to your laptop and not to another service. A server bound only to container loopback is normally unreachable through a mapping to its container network interface. The fixture listens on `0.0.0.0:8080` inside the container and publishes only `127.0.0.1:18080` on the host.

The wildcard address `0.0.0.0` is a listening choice, not a browser destination. Binding a published port to host loopback reduces accidental exposure to other machines. The real boundary also depends on the engine, host firewall and platform networking, so do not describe a port mapping as an authentication system.

### Key terms

- **Port publishing:** Mapping a host address and port to a container port so host traffic can reach a container listener.
- **Loopback address:** An address such as 127.0.0.1 that points back to the same network namespace, so inside a container it means that container.
- **Bind address:** The address a server listens on; 0.0.0.0 accepts connections on every interface in its own namespace.
- **Host port:** The host side of a mapping, such as port 18080 bound to 127.0.0.1 for the fixture.
- **Container port:** The port the application listens on inside its container, such as 8080 for the fixture.

## Anatomy and a trace you can follow

Read `127.0.0.1:18080:8080` as host address, host port and container port. A browser on the host requests `http://127.0.0.1:18080/`. A peer container on the same Compose network requests `http://app:8080/` using service discovery. They reach the same application through different paths.

Troubleshoot in layers: application listen address, process state, container port, published mapping, host port conflict, then HTTP path and payload. A connection refused response is different from HTTP 404; the latter means an HTTP server responded but did not serve the requested path.

## How to use this lesson

The classroom saves `courses/docker/lessons/docker-009.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** With the project running, request `http://127.0.0.1:18080/` from the host and then run `docker compose -p ds60-docker-study port app 8080`, which should print `127.0.0.1:18080`. Next, try the same URL from inside the app container: `docker compose -p ds60-docker-study exec app python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:18080/', timeout=2)"`. It fails, because inside the container 127.0.0.1 is the container's own loopback, where nothing listens on 18080. Change the URL to port 8080 and it succeeds. Then run the tools-profile client from the fixture README, which reaches `app:8080` by name. Three requests, three scopes. Nothing new is created except the short-lived client container, which `--rm` removes.

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

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

### Exercise 1: Label every component of the mapping.

**Expected evidence:** Host loopback, host port 18080 and container port 8080.

**Hint:** Read 127.0.0.1:18080:8080 from left to right as host address, host port and container port.

### Exercise 2: Predict whether `localhost:18080` inside app reaches the host browser endpoint.

**Hint:** Ask whose loopback interface localhost means inside the container.

### Exercise 3: Draw a host browser request path.

**Hint:** Follow the request from the browser to the published socket to the app's listener.

### Exercise 4: Diagnose a server bound to container 127.0.0.1 only.

**Hint:** Check the address the server listens on inside the container.

### Exercise 5: Distinguish connection refused from HTTP 404.

**Hint:** Ask whether any HTTP response came back at all.

### Exercise 6: Choose public and internal endpoints for a two-service app.

**Hint:** Publish only what a person outside the project must reach.

## Common mistakes and diagnosis

Binding the server to 127.0.0.1 inside the container, so the published port cannot reach it. Publishing on all host interfaces when loopback is enough. Using `localhost` in one container to reach another.

Exercise 4 is this chapter's boundary case: Diagnose a server bound to container 127.0.0.1 only. Check which address the server binds inside the container, `127.0.0.1` or `0.0.0.0`, before editing the published mapping or the browser URL.

Learners on Linux sometimes assume a host firewall such as `ufw` protects a published port. The engine installs its own packet-filtering rules for published ports, and depending on the setup those rules can take effect before the host firewall's own chains, so `ports: - "8080:8080"` can be reachable from the network even when the firewall appears to deny 8080. The reliable control is the bind address in the mapping: publish to `127.0.0.1` when only the host needs access, as the fixture does, and check with `docker compose port` or `ss -ltn` on the host which address is actually listening.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** Trace a host request to `127.0.0.1:18080` and a peer request to `app:8080` without looking at the diagram.

**Transfer case.** A second service in the same project needs to call the app, and a teammate configures it with `http://localhost:18080/`. It fails. Give the URL it should use, and explain why the host's URL does not work from there.

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

## Primary references

- [Port publishing and mapping](https://docs.docker.com/engine/network/port-publishing/)
- [Networking overview](https://docs.docker.com/engine/network/)

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
