# docker-009: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-009.md`.

## Exercise 1: Label every component of the mapping.

**Expected evidence:** Host loopback, host port 18080 and container port 8080.

**Why:** The three values occupy different positions. Reversing the ports can create a listening mapping that still points at the wrong internal endpoint.

## Exercise 2: Predict whether localhost:18080 inside app reaches the host browser endpoint.

**Expected answer:** It refers to app container loopback and normally fails.

**Why:** Loopback is relative to the caller namespace. A hostname that works in the browser does not automatically name the same machine from a container.

## Exercise 3: Draw a host browser request path.

**Expected answer:** Browser, host socket mapping, container interface and app listener.

**Why:** Each hop has a separate observable condition. The drawing should show where port translation happens and which process actually handles the request.

## Exercise 4: Diagnose a server bound to container 127.0.0.1 only.

**Expected answer:** It may answer locally but not through the published mapping.

**Why:** The mapping targets the container’s reachable interface. Changing the host port cannot fix an application that does not listen on that interface.

## Exercise 5: Distinguish connection refused from HTTP 404.

**Expected answer:** Transport failure versus application routing result.

**Why:** A 404 establishes that an HTTP exchange happened. A refused connection occurs earlier, so inspect listeners and mappings before changing application URL handlers.

## Exercise 6: Choose public and internal endpoints for a two-service app.

**Expected answer:** Only the user-facing service gets a deliberate published port.

**Why:** Internal services can use Compose DNS without host publication. Avoiding unnecessary published ports simplifies the network and reduces accidental exposure.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
