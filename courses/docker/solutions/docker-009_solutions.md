# docker-009: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

An IP address identifies a network interface or virtual destination within a network. A port identifies a transport endpoint at that address. A server listens on an address and port inside its own network namespace. Publishing maps a host endpoint to a container endpoint; it does not change the application’s listening configuration.

Loopback refers to the local network namespace. `127.0.0.1` inside a container points back to that container, not to your laptop and not to another service. A server bound only to container loopback is normally unreachable through a mapping to its container network interface. The fixture listens on `0.0.0.0:8080` inside the container and publishes only `127.0.0.1:18080` on the host.

The wildcard address `0.0.0.0` is a listening choice, not a browser destination. Binding a published port to host loopback reduces accidental exposure to other machines. The real boundary also depends on the engine, host firewall and platform networking, so do not describe a port mapping as an authentication system.

Read `127.0.0.1:18080:8080` as host address, host port and container port. A browser on the host requests `http://127.0.0.1:18080/`. A peer container on the same Compose network requests `http://app:8080/` using service discovery. They reach the same application through different paths.

Troubleshoot in layers: application listen address, process state, container port, published mapping, host port conflict, then HTTP path and payload. A connection refused response is different from HTTP 404; the latter means an HTTP server responded but did not serve the requested path.

## Exercise 1: Label every component of the mapping.

The three values occupy different positions. Reversing the ports can create a listening mapping that still points at the wrong internal endpoint.

**Expected:** Host loopback, host port 18080 and container port 8080.

## Exercise 2: Predict whether localhost:18080 inside app reaches the host browser endpoint.

Loopback is relative to the caller namespace. A hostname that works in the browser does not automatically name the same machine from a container.

**Expected:** It refers to app container loopback and normally fails.

## Exercise 3: Draw a host browser request path.

Each hop has a separate observable condition. The drawing should show where port translation happens and which process actually handles the request.

**Expected:** Browser, host socket mapping, container interface and app listener.

## Exercise 4: Diagnose a server bound to container 127.0.0.1 only.

The mapping targets the container’s reachable interface. Changing the host port cannot fix an application that does not listen on that interface.

**Expected:** It may answer locally but not through the published mapping.

## Exercise 5: Distinguish connection refused from HTTP 404.

A 404 establishes that an HTTP exchange happened. A refused connection occurs earlier, so inspect listeners and mappings before changing application URL handlers.

**Expected:** Transport failure versus application routing result.

## Exercise 6: Choose public and internal endpoints for a two-service app.

Internal services can use Compose DNS without host publication. Avoiding unnecessary published ports simplifies the network and reduces accidental exposure.

**Expected:** Only the user-facing service gets a deliberate published port.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
