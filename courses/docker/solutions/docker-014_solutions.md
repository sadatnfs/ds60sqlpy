# docker-014: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

A capstone combines mechanisms into an observable delivery story. The target here is deliberately small: a local HTTP application with a visible message, a health endpoint and a persistent counter. Completing it requires understanding build inputs, image identity, container state, loopback publishing, readiness and volume lifetime.

The project is successful when a new learner can reproduce the outcome from the copied fixture and explain why each step works. A screenshot of a browser alone is insufficient: it could show an old process or cached content. Combine the visible response with the exact project, image and replacement evidence.

This lab is not a benchmark, production service or shared hosting system. Its fixed host loopback port and synthetic counter keep the exercise inspectable. If the port or project identity conflicts with existing work, choose an unused owned identity before starting rather than stopping another application.

Copy `courses/docker/fixtures/compose-lab/` into a new directory below `.learning/`. Read its README in full. Validate the model, build with plain progress, start with readiness, request the message and counter, and recreate the app with its volume intact. Preserve commands and observations in the lesson worksheet.

The request chain is host browser to published host loopback port to app listener to JSON handler to the volume-backed counter. A new image is packaging evidence. A new container ID with retained counter is persistence evidence. The distinction is the core of the exercise.

## Exercise 1: Predict every resource the project creates.

The optional client is created only for its explicit run. Listing resource types before execution makes ownership and later cleanup easier to verify.

**Expected:** A local image, app container, project network and named data volume.

## Exercise 2: Change the public message in the learner copy.

Keep the source image unchanged for this experiment. It demonstrates that configuration and application packaging are separable inputs.

**Expected:** The observed response matches the deliberate runtime configuration.

## Exercise 3: Produce the complete build-and-request evidence packet.

Each item covers a different layer. Together they make it less likely that a stale browser page or old image is mistaken for the new build.

**Expected:** Build logs, model validation, health state and exact JSON response.

## Exercise 4: Introduce and repair one wrong host port in a scratch model.

Avoid unrelated changes. A single deliberate configuration fault gives a clean causal explanation and a regression case for the working mapping.

**Expected:** Explain the first failing network hop and restore the original mapping.

## Exercise 5: Verify replacement without resetting the counter.

This is the central persistence invariant. An image rebuild or browser refresh alone does not test container replacement, so record the actual object change.

**Expected:** Different container ID, same intended volume and nonreset counter.

## Exercise 6: Teach the project to a beginner without using hidden host state.

A reproducible explanation should name what must already be installed and which downloads occur. It must not depend on a private image tag or an unmentioned file on the author’s laptop.

**Expected:** A fresh-copy procedure with prerequisites, expected outputs and scoped cleanup.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
