# docker-032: explanatory solutions

These answers explain teaching fixtures, not engine results; the mechanism is in [the guide](../guides/docker-032.md).

## Exercise 1: Predict a missing-shell error in a minimal image.

**Expected answer:** It may be expected image content, not an app crash.

**Why:** The diagnostic command needs its own dependency. Do not conclude that the application is broken merely because a familiar tool is absent.

**Approach:** Check whether the image provides sh or bash before reading the error as an app failure.

**Why this is correct:** A minimal image may ship without a shell; exec fails at lookup while server.py keeps serving.

**A plausible wrong approach:** Restarting the app or adding a shell to the release image to fix the error changes the image to suit the diagnostic.

**How to verify:** The health request still succeeds while the shell exec fails, which shows the two are unrelated.

## Exercise 2: Choose a prepared tool for one HTTP request.

**Expected answer:** Use Python already present in the fixture.

**Why:** Adding a new package is unnecessary for this bounded observation. Reuse a declared runtime while keeping timeout and output limits explicit.

**Approach:** Use the Python interpreter that CMD already relies on to send one request with a 2 second timeout, as in worked example 1.

**Why this is correct:** The fixture's base already includes python, so the probe adds nothing and still observes the app's own loopback.

**A plausible wrong approach:** Installing curl in the running container adds a package and fails anyway because the root is read-only.

**How to verify:** The command prints the healthz JSON and exits; nothing new appears in the image.

## Exercise 3: Create a vantage-point diagnosis table.

**Expected evidence:** Host, peer and app observations with distinct address scopes.

**Why:** The table helps explain why one request works and another fails. It prevents applying a host-network fix to a container-loopback problem.

**Approach:** Fill three rows, host, peer and app, with the address each uses and the result it saw.

**Why this is correct:** Each vantage point has its own address scope, so a pattern such as only peer failing points to DNS or the network.

**A plausible wrong approach:** Changing the host port mapping when only the peer request fails fixes a part that was already working.

**How to verify:** The row that differs points to one layer, and fixing that layer makes all three rows agree.

## Exercise 4: Diagnose an interactive repair that cannot survive recreation.

**Expected answer:** The maintained image was never changed.

**Why:** Record the useful finding, then implement the repair in source and rebuild. Treat the altered live container as diagnostic state, not a release artifact.

**Approach:** Write down what the live fix revealed, then make the same change in the Dockerfile or source and rebuild.

**Why this is correct:** Recreation starts from the image, so a live edit is lost; only the rebuilt image carries the fix.

**A plausible wrong approach:** Leaving the hand-fixed container running as the release hides that the image is still broken.

**How to verify:** Recreate from the rebuilt image and confirm the symptom stays gone.

## Exercise 5: Explain why host filesystem mounts are excessive for this lab.

**Expected answer:** They expose data unrelated to the app diagnosis.

**Why:** The fixture can be inspected through its own image, logs and volume. Broader mounts change authority without adding necessary evidence.

**Approach:** List what the diagnosis needs: logs, the image's files and the study-data volume, all reachable without host mounts.

**Why this is correct:** Mounting the host root or home directory gives the container access unrelated to the app.

**A plausible wrong approach:** Bind-mounting / to look around turns a debugging session into broad host access.

**How to verify:** The diagnosis completes using logs, exec probes and the volume only.

## Exercise 6: Write a repeatable minimal-image incident procedure.

**Expected evidence:** Preserve artifact, inspect state, run bounded prepared probes and test a source repair.

**Why:** A repeatable procedure works for another learner and preserves the original symptom. It should not depend on tools installed manually during a previous incident.

**Approach:** Write the steps in order: save the image ID and logs, inspect state, run bounded prepared probes, then test a source fix.

**Why this is correct:** Saving evidence first keeps the original symptom, and prepared probes work on any learner's machine.

**A plausible wrong approach:** A procedure that begins with installing your favorite tools assumes network access and changes what you inspect.

**How to verify:** Another learner follows it on a fresh copy and reaches the same diagnosis.

## Check your transfer

The app, its listener and the project network work, so the fault sits on the published path between the host and the container. Start with `docker compose -p ds60-docker-study port app 8080`, which should print `127.0.0.1:18080`; then check whether another host process holds 18080, and on Docker Desktop whether its port forwarding is running. A repair is confirmed when the host request returns the health JSON. If `port` reports no mapping at all, the container was created without its `ports` entry, which points back to the effective Compose model.
