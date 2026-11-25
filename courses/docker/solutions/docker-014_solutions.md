# docker-014: explanatory solutions

These answers explain teaching fixtures, not engine results; the mechanism is in [the guide](../guides/docker-014.md).

## Exercise 1: Predict every resource the project creates.

**Expected answer:** A local image, app container, project network and named data volume.

**Why:** The optional client is created only for its explicit run. Listing resource types before execution makes ownership and later cleanup easier to verify.

**Approach:** Read compose.yaml for each object it implies: the image ds60-docker-study:local, an app container, a default project network and the study-data volume.

**Why this is correct:** The client service has profiles: [tools], so a plain up does not create it. The other four objects come from the model.

**A plausible wrong approach:** Listing the client container among the resources fails, because profile-gated services start only with --profile tools or an explicit run.

**How to verify:** After up, docker compose ps -a shows only app, while docker network ls and docker volume ls show the project's network and volume.

## Exercise 2: Change the public message in the learner copy.

**Expected evidence:** The observed response matches the deliberate runtime configuration.

**Why:** Keep the source image unchanged for this experiment. It demonstrates that configuration and application packaging are separable inputs.

**Approach:** Edit APP_MESSAGE in your copy of compose.yaml, run up -d --wait, and leave server.py and the image untouched.

**Why this is correct:** server.py reads the variable at request time, and Compose recreates the container for the new environment, so the response changes without a rebuild.

**A plausible wrong approach:** Editing the default string inside server.py also changes the output, but it mixes a code change into what should test configuration.

**How to verify:** The image ID is the same before and after, while GET / returns the new message.

## Exercise 3: Produce the complete build-and-request evidence packet.

**Expected evidence:** Build logs, model validation, health state and exact JSON response.

**Why:** Each item covers a different layer. Together they make it less likely that a stale browser page or old image is mistaken for the new build.

**Approach:** Assemble the build log, config --quiet exit status, the health state from ps, and the exact JSON body from GET /.

**Why this is correct:** Each piece covers a stage: model, packaging, process readiness and application output. Together they rule out a stale image or browser cache.

**A plausible wrong approach:** Submitting only a browser screenshot cannot show whether the build ran or whether the page came from cache.

**How to verify:** Every item carries a timestamp from the same session, and the JSON message matches the value in compose.yaml.

## Exercise 4: Introduce and repair one wrong host port in a scratch model.

**Expected evidence:** Explain the first failing network hop and restore the original mapping.

**Why:** Avoid unrelated changes. A single deliberate configuration fault gives a clean causal explanation and a regression case for the working mapping.

**Approach:** Change only the container port in a scratch copy, for example "127.0.0.1:18080:8081", predict the failing hop, then restore it.

**Why this is correct:** The host listener still exists, but traffic goes to container port 8081, where nothing listens, so health stays green while host requests fail.

**A plausible wrong approach:** Changing the host port, the listener and the healthcheck together leaves no clear cause and no clean regression case.

**How to verify:** The broken copy fails at the host request while health passes; restoring the original line makes the request return the JSON again.

## Exercise 5: Verify replacement without resetting the counter.

**Expected evidence:** Different container ID, same intended volume and nonreset counter.

**Why:** This is the central persistence invariant. An image rebuild or browser refresh alone does not test container replacement, so record the actual object change.

**Approach:** Increment the counter, note the value and container ID, run up --force-recreate --wait app, then note both again.

**Why this is correct:** The invariant requires a new container ID, the same study-data volume and an unchanged counter. All three are needed.

**A plausible wrong approach:** Rebuilding the image or refreshing the browser does not replace the container, so the test passes without testing persistence.

**How to verify:** ps -q app prints different IDs and GET /counter returns the value recorded before the recreate.

## Exercise 6: Teach the project to a beginner without using hidden host state.

**Expected evidence:** A fresh-copy procedure with prerequisites, expected outputs and scoped cleanup.

**Why:** A reproducible explanation should name what must already be installed and which downloads occur. It must not depend on a private image tag or an unmentioned file on the author’s laptop.

**Approach:** Write a fresh-copy procedure: prerequisites, copying the fixture, the commands from worked examples 1 and 2, expected observations, and the down step.

**Why this is correct:** The `python:3.12-slim` base is the only download, and pull_policy: never shows that the local tag must be built first.

**A plausible wrong approach:** Writing up -d without the build step works on the author's laptop only because the tag already exists there.

**How to verify:** Follow the procedure on a machine or engine without the local tag; it completes and ends with down leaving only the volume.

## Check your transfer

Check the project state with `docker compose -p ds60-docker-study ps`. Without `--wait`, `up -d` returns once the container has started, which can be before the server is listening, so the health column may still say `starting`. Retry after it reports `healthy`; the expected result is the configured JSON. A real fault is indicated if the service is healthy and the request is still refused: then `docker compose port app 8080` shows whether the beginner is using a different host port, for example from a rehearsal copy on 18081.
