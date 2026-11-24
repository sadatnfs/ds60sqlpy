# docker-018: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-018.md`.

## Exercise 1: Predict the name a peer uses for the app.

**Expected answer:** The Compose service name app.

**Why:** The project network’s discovery maps that name to current service endpoints. A hardcoded IP creates unnecessary coupling to a container instance.

**Approach:** Read the client's command in compose.yaml: it requests `http://app:8080/` using the service name.

**Why this is correct:** Compose registers app on the project network's DNS, which resolves to whatever container serves app now.

**A plausible wrong approach:** Hardcoding the IP from docker inspect works until the container is recreated and receives a new address.

**How to verify:** Worked example 1 prints the app's greeting from inside client without any IP in the model.

## Exercise 2: Explain why a peer should not use host loopback.

**Expected answer:** Its loopback refers to the peer itself.

**Why:** Network namespace scope applies consistently. A copied browser URL is not a universal address for every caller.

**Approach:** Ask whose loopback 127.0.0.1 means: for the client container, it is the client's own namespace.

**Why this is correct:** Nothing listens on 18080 or 8080 inside client, so a request to its loopback fails even with app healthy.

**A plausible wrong approach:** Pointing client at http://127.0.0.1:18080/ because it works in the browser produces connection refused.

**How to verify:** Run the client command with the loopback URL and observe refusal, then with `app:8080` and observe the greeting.

## Exercise 3: Draw the DNS-to-request sequence.

**Expected answer:** Resolve app, connect to container port, send HTTP request, inspect body.

**Why:** Separate name resolution from transport and application processing so each failure has a minimal next observation.

**Approach:** Draw four steps: resolve app via project DNS, open TCP to that address on 8080, send GET /, read the JSON body.

**Why this is correct:** Each step fails differently: name not found, connection refused or timeout, HTTP error, or a wrong body.

**A plausible wrong approach:** Lumping every failure into network broken skips the step-specific check that would shorten diagnosis.

**How to verify:** Inside a peer, python socket.gethostbyname('app') returns an address, and the request then returns the body.

## Exercise 4: Diagnose DNS success with connection refusal.

**Expected answer:** The destination resolved but no reachable listener accepted that port.

**Why:** Check app state, listen address and target port. Replacing DNS configuration is not justified by a successful resolution.

**Approach:** Separate the two facts: a resolved name proves DNS works; refused means nothing accepted on that address and port.

**Why this is correct:** Likely causes are app stopped, app listening on loopback only, or the wrong port. DNS settings are not among them.

**A plausible wrong approach:** Editing DNS settings or adding hosts entries changes the part that already succeeded.

**How to verify:** Check docker compose ps for app, then the listener address, then the port in the client URL; one shows the mismatch.

## Exercise 5: Predict a reconnect after app recreation.

**Expected answer:** A fresh lookup and connection can reach the new instance.

**Why:** An established connection can fail when its old backend disappears. Client recovery must match operation safety rather than blindly replay every request.

**Approach:** Separate new connections from existing ones: after recreation, a fresh lookup of app returns the new container's address.

**Why this is correct:** An established connection pointed at the old container breaks when it is removed; a new connection reaches the replacement.

**A plausible wrong approach:** Retrying every failed request blindly can repeat a non-idempotent POST /increment.

**How to verify:** Run client after recreating app; it succeeds without changes because it resolves app again.

## Exercise 6: Design an internal-only database connection.

**Expected evidence:** Use service DNS and container port without host publication.

**Why:** Internal peers need a network path, not necessarily a host socket. Keep publication limited to intended user entrypoints and use application credentials as needed.

**Approach:** Give the database service no ports entry and have the app connect to it by service name and container port on the shared network.

**Why this is correct:** The app needs only a network path. Leaving out a host mapping removes an exposure without affecting the app.

**A plausible wrong approach:** Publishing the database on the host just in case lets any local process, or a remote one if bound widely, reach it.

**How to verify:** docker compose ps shows no published port for the database, and the app's queries still succeed.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
