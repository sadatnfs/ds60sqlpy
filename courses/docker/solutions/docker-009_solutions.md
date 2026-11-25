# docker-009: explanatory solutions

These answers explain teaching fixtures, not engine results; the mechanism is in [the guide](../guides/docker-009.md).

## Exercise 1: Label every component of the mapping.

**Expected evidence:** Host loopback, host port 18080 and container port 8080.

**Why:** The three values occupy different positions. Reversing the ports can create a listening mapping that still points at the wrong internal endpoint.

**Approach:** Split "127.0.0.1:18080:8080" at its colons from left to right: host IP, host port, then container port.

**Why this is correct:** The fixture's server binds port 8080 inside the container, and the host side is fixed to loopback on 18080, so a browser on the same machine is the only intended client.

**A plausible wrong approach:** Writing "127.0.0.1:8080:18080" still opens a host listener but forwards traffic to container port 18080, where nothing listens.

**How to verify:** docker compose port app 8080 prints 127.0.0.1:18080, and a request to that host address returns the fixture JSON.

## Exercise 2: Predict whether `localhost:18080` inside app reaches the host browser endpoint.

**Expected answer:** It refers to app container loopback and normally fails.

**Why:** Loopback is relative to the caller namespace. A hostname that works in the browser does not automatically name the same machine from a container.

**Approach:** Locate the caller: a command run through docker compose exec app has its own network namespace and its own loopback interface.

**Why this is correct:** Inside app, 127.0.0.1 is the container itself, where only port 8080 listens. Port 18080 exists only on the host side of the mapping.

**A plausible wrong approach:** Copying the browser URL into a health probe or a sibling client produces connection refused and looks like a broken server.

**How to verify:** From inside app, a python urllib request to 127.0.0.1:8080/healthz succeeds while 127.0.0.1:18080 is refused.

## Exercise 3: Draw a host browser request path.

**Expected answer:** Browser, host socket mapping, container interface and app listener.

**Why:** Each hop has a separate observable condition. The drawing should show where port translation happens and which process actually handles the request.

**Approach:** Draw four hops: the browser connects to 127.0.0.1:18080, the engine forwards it to the container, and server.py's listener on 0.0.0.0:8080 handles it.

**Why this is correct:** Port translation happens once, at the published mapping. After that the request reaches the container interface and the Handler class chooses the response.

**A plausible wrong approach:** Drawing the browser connecting straight to container port 8080 hides the mapping, so a missing ports: entry would be impossible to locate on the diagram.

**How to verify:** Annotate each hop with its check: the port listing, container state, the app logs showing the request line, and the JSON body.

## Exercise 4: Diagnose a server bound to container 127.0.0.1 only.

**Expected answer:** It may answer locally but not through the published mapping.

**Why:** The mapping targets the container’s reachable interface. Changing the host port cannot fix an application that does not listen on that interface.

**Approach:** Compare the listener address with the mapping target: a server that binds 127.0.0.1:8080 inside the container listens only on the container's loopback.

**Why this is correct:** Published traffic arrives on the container's network interface, not on its loopback. The fixture avoids this by binding 0.0.0.0 in LocalServer.

**A plausible wrong approach:** Changing 18080 to another host port cannot help, because every mapping delivers traffic to the same interface where the app is absent.

**How to verify:** A probe from inside the container to 127.0.0.1:8080 works while the host request fails; after binding 0.0.0.0, both succeed.

## Exercise 5: Distinguish connection refused from HTTP 404.

**Expected answer:** Transport failure versus application routing result.

**Why:** A 404 establishes that an HTTP exchange happened. A refused connection occurs earlier, so inspect listeners and mappings before changing application URL handlers.

**Approach:** Ask whether an HTTP response came back at all. A refused connection fails at TCP; a 404 is a complete response from the server.

**Why this is correct:** The fixture returns {"error": "unknown route"} with status 404 for unknown paths, which proves the mapping and listener worked.

**A plausible wrong approach:** Rewriting URL handlers after connection refused changes code the request never reached, while the real fault is a missing mapping or listener.

**How to verify:** curl -i http://127.0.0.1:18080/nope prints an HTTP/1.0 404 status line, while a request to an unmapped port reports connection refused.

## Exercise 6: Choose public and internal endpoints for a two-service app.

**Expected answer:** Only the user-facing service gets a deliberate published port.

**Why:** Internal services can use Compose DNS without host publication. Avoiding unnecessary published ports simplifies the network and reduces accidental exposure.

**Approach:** Publish only the user-facing web service on loopback and let the internal service talk over the project network by its service name.

**Why this is correct:** Compose DNS resolves service names on the project network, as the client service does with `http://app:8080/`, so internal traffic needs no host port.

**A plausible wrong approach:** Publishing the database on 0.0.0.0 to make debugging easy exposes it to anyone who can reach the host on that port.

**How to verify:** docker compose ps shows a port column only for the web service, and the web service still reaches the internal one by name.

## Check your transfer

It should use `http://app:8080/`. Inside the second container, `localhost` is that container's own loopback interface, and port 18080 exists only as a mapping on the host, so nothing listens there. Compose puts both services on a project network where the service name `app` resolves to the app container, and the app listens on its container port 8080. The expected result is the same JSON the browser receives. If `app:8080` also failed while the host URL worked, the services would likely be on different networks, which `docker network inspect` would show.
