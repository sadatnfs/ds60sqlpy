# docker-019: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-019.md`.

## Exercise 1: Distinguish attachment from published ports.

**Expected answer:** Joining a network and exposing a host socket are different operations.

**Why:** A service can communicate with peers without publishing anything. A published port is an additional host-facing path that deserves separate review.

**Approach:** Separate two settings in the YAML: networks lists which project networks a service joins; ports maps a host socket to the container.

**Why this is correct:** In worked example 1, database joins only backend and has no ports, so api reaches it while the host cannot.

**A plausible wrong approach:** Adding ports to database so api can connect is unnecessary, since they already share backend, and it opens a host path.

**How to verify:** docker compose config shows networks for each service and no ports on database; api can still connect to it.

## Exercise 2: Predict a pure computation with network none.

**Expected answer:** It succeeds if its files and runtime are already present.

**Why:** Network isolation does not prevent local arithmetic or file reads. It reveals undeclared dependencies when a program unexpectedly tries to download input.

**Approach:** Check whether the program needs anything outside the container: sum([2, 4, 6]) uses only the interpreter in the image.

**Why this is correct:** --network none removes all interfaces except loopback, which does not affect arithmetic, so the run prints 12.

**A plausible wrong approach:** Expecting every container to fail without a network confuses connectivity with computation.

**How to verify:** Worked example 2 prints 12; a variant that calls urllib.request.urlopen on an internet URL fails under the same flag.

## Exercise 3: Design a frontend/backend attachment table.

**Expected evidence:** Each service joins only the networks needed by its role.

**Why:** A small explicit table makes unintended paths easier to notice. Avoid putting every component on every network merely for convenience.

**Approach:** List each service with the networks it needs: api on frontend and backend, database on backend only, and backend marked internal.

**Why this is correct:** internal: true stops backend from routing outward, so database gets peers but no internet path.

**A plausible wrong approach:** Putting every service on every network makes the diagram simpler but lets the frontend reach the database directly.

**How to verify:** From a frontend-only container, resolving database fails, while api resolves it.

## Exercise 4: Diagnose host-network mode used to hide a mapping error.

**Expected answer:** Restore the intended isolation and fix the actual address or port.

**Why:** Changing the network mode can mask the symptom while broadening access. Test the original topology’s contract instead.

**Approach:** Revert network_mode: host and return to the bridge model, then locate the real fault in address or port.

**Why this is correct:** Host mode removes isolation and port mapping entirely, so things seem to work while the original fault remains.

**A plausible wrong approach:** Keeping host mode exposes every listener on all host interfaces.

**How to verify:** With the bridge restored and the ports line corrected, the loopback request works and nothing listens on other interfaces.

## Exercise 5: Explain why network isolation is not authentication.

**Expected answer:** Reachability policy and application identity answer different questions.

**Why:** An allowed caller may still be unauthorized for an operation. Sensitive services need appropriate request authentication and authorization in addition to network placement.

**Approach:** Ask two questions per request: can the caller reach the service, and is this caller allowed to perform this operation?

**Why this is correct:** Network placement answers only the first. Any process on backend could call database, including a compromised api.

**A plausible wrong approach:** Skipping database credentials because only backend can reach it leaves every backend process with full access.

**How to verify:** Connect from a backend container without credentials; a properly configured service refuses the operation.

## Exercise 6: Define outbound acceptance for an offline worker.

**Expected evidence:** Prepared local computation succeeds and no external fetch is required.

**Why:** Offline qualification is about actual inputs and behavior. Merely disconnecting the network does not prove that all future code paths are prepared.

**Approach:** Prepare inputs in the image or a mounted volume, run the worker with --network none, and compare output to the expected result.

**Why this is correct:** If the run succeeds with no network, everything it used was local. That proves this input path only.

**A plausible wrong approach:** Disconnecting once and declaring the worker offline-ready misses code paths, such as an update check, that the test never exercised.

**How to verify:** Record which inputs were tested and that each finished under --network none.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
