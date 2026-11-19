# docker-014: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-014.md`.

## Exercise 1: Predict every resource the project creates.

**Expected answer:** A local image, app container, project network and named data volume.

**Why:** The optional client is created only for its explicit run. Listing resource types before execution makes ownership and later cleanup easier to verify.

## Exercise 2: Change the public message in the learner copy.

**Expected evidence:** The observed response matches the deliberate runtime configuration.

**Why:** Keep the source image unchanged for this experiment. It demonstrates that configuration and application packaging are separable inputs.

## Exercise 3: Produce the complete build-and-request evidence packet.

**Expected evidence:** Build logs, model validation, health state and exact JSON response.

**Why:** Each item covers a different layer. Together they make it less likely that a stale browser page or old image is mistaken for the new build.

## Exercise 4: Introduce and repair one wrong host port in a scratch model.

**Expected evidence:** Explain the first failing network hop and restore the original mapping.

**Why:** Avoid unrelated changes. A single deliberate configuration fault gives a clean causal explanation and a regression case for the working mapping.

## Exercise 5: Verify replacement without resetting the counter.

**Expected evidence:** Different container ID, same intended volume and nonreset counter.

**Why:** This is the central persistence invariant. An image rebuild or browser refresh alone does not test container replacement, so record the actual object change.

## Exercise 6: Teach the project to a beginner without using hidden host state.

**Expected evidence:** A fresh-copy procedure with prerequisites, expected outputs and scoped cleanup.

**Why:** A reproducible explanation should name what must already be installed and which downloads occur. It must not depend on a private image tag or an unmentioned file on the author’s laptop.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
