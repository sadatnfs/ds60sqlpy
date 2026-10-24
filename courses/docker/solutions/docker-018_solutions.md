# docker-018: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

A bridge network connects container interfaces on one engine. A user-defined bridge provides scoped service discovery and connectivity for attached containers. Compose normally creates such a network for a project. DNS maps a service name to a current reachable address; the name is a better application dependency than a temporary container IP.

The app and client in the fixture communicate using `app:8080`. The client does not need the host’s published port. A container replacement can change its address while the service name remains the intended lookup key. Applications must reconnect and resolve names appropriately rather than retaining a dead connection forever.

Network attachment and authorization are different concerns. Sharing a network can permit connectivity, but an application still needs authentication when serving sensitive operations. Conversely, a private network is not a reason to publish every internal port on the host.

The optional client uses Python’s HTTP library and a short timeout. `docker compose run --rm client` creates a short-lived container attached to the project’s network. It resolves `app`, connects to 8080 and prints the JSON response. The fixture marks that service with a tools profile so it does not remain as another server during ordinary startup.

A DNS resolution failure, a refused connection and a valid HTTP error are different observations. Diagnose from the caller’s namespace, because the host may resolve different names and use a different route.

## Exercise 1: Predict the name a peer uses for the app.

The project network’s discovery maps that name to current service endpoints. A hardcoded IP creates unnecessary coupling to a container instance.

**Expected:** The Compose service name app.

## Exercise 2: Explain why a peer should not use host loopback.

Network namespace scope applies consistently. A copied browser URL is not a universal address for every caller.

**Expected:** Its loopback refers to the peer itself.

## Exercise 3: Draw the DNS-to-request sequence.

Separate name resolution from transport and application processing so each failure has a minimal next observation.

**Expected:** Resolve app, connect to container port, send HTTP request, inspect body.

## Exercise 4: Diagnose DNS success with connection refusal.

Check app state, listen address and target port. Replacing DNS configuration is not justified by a successful resolution.

**Expected:** The destination resolved but no reachable listener accepted that port.

## Exercise 5: Predict a reconnect after app recreation.

An established connection can fail when its old backend disappears. Client recovery must match operation safety rather than blindly replay every request.

**Expected:** A fresh lookup and connection can reach the new instance.

## Exercise 6: Design an internal-only database connection.

Internal peers need a network path, not necessarily a host socket. Keep publication limited to intended user entrypoints and use application credentials as needed.

**Expected:** Use service DNS and container port without host publication.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
