# docker-018: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-018.md`.

## Exercise 1: Predict the name a peer uses for the app.

**Expected answer:** The Compose service name app.

**Why:** The project network’s discovery maps that name to current service endpoints. A hardcoded IP creates unnecessary coupling to a container instance.

## Exercise 2: Explain why a peer should not use host loopback.

**Expected answer:** Its loopback refers to the peer itself.

**Why:** Network namespace scope applies consistently. A copied browser URL is not a universal address for every caller.

## Exercise 3: Draw the DNS-to-request sequence.

**Expected answer:** Resolve app, connect to container port, send HTTP request, inspect body.

**Why:** Separate name resolution from transport and application processing so each failure has a minimal next observation.

## Exercise 4: Diagnose DNS success with connection refusal.

**Expected answer:** The destination resolved but no reachable listener accepted that port.

**Why:** Check app state, listen address and target port. Replacing DNS configuration is not justified by a successful resolution.

## Exercise 5: Predict a reconnect after app recreation.

**Expected answer:** A fresh lookup and connection can reach the new instance.

**Why:** An established connection can fail when its old backend disappears. Client recovery must match operation safety rather than blindly replay every request.

## Exercise 6: Design an internal-only database connection.

**Expected evidence:** Use service DNS and container port without host publication.

**Why:** Internal peers need a network path, not necessarily a host socket. Keep publication limited to intended user entrypoints and use application credentials as needed.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
