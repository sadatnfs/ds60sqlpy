# docker-011: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-011.md`.

## Exercise 1: Identify the project and service names.

**Expected answer:** Project ds60-docker-study and service app.

**Why:** The project groups engine resources; the service describes an application role. A container ID is a third identity that can change after recreation.

## Exercise 2: Predict what config --quiet changes.

**Expected answer:** It validates the model without creating runtime resources.

**Why:** Static model validation is valuable early evidence, but it cannot prove port availability, image execution, volume permissions or endpoint correctness.

## Exercise 3: Write the project lifecycle command sequence.

**Expected evidence:** Validate, build, up with readiness, inspect, then down.

**Why:** Each step adds evidence and has a defined effect. Keeping the project option on every command prevents a directory-name change from accidentally selecting a different project.

## Exercise 4: Diagnose an unexpected resource collision.

**Expected answer:** Inspect project identity and existing owned resources before changes.

**Why:** A reused project name or host port can collide with another copy. Renaming or deleting blindly may affect work you did not create; establish ownership first.

## Exercise 5: Explain why down preserves user data by default.

**Expected answer:** Named volume removal is a separate explicit operation.

**Why:** Containers and networks are generally disposable application infrastructure. Persistent state deserves a deliberate retention policy, so destruction is not an incidental consequence of stopping a lab.

## Exercise 6: Design a two-copy experiment without interference.

**Expected evidence:** Distinct project names and distinct published host ports.

**Why:** Both copies can use the same internal service names because each project has its own network. Host-published ports share a host namespace and must avoid conflicts.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
