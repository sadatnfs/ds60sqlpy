# docker-003: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-003.md`.

## Exercise 1: Classify /app/server.py in the fixture.

**Expected answer:** An image-provided application file.

**Why:** The Dockerfile COPY instruction places it into a build layer. Reading it from a container demonstrates that the image content is visible through the container filesystem view.

## Exercise 2: Predict whether a sibling container sees an unmounted new file.

**Expected answer:** It does not share the first container writable layer.

**Why:** Both instances start from the image. Changes in one private writable layer are not broadcast into another container simply because both use the same tag.

## Exercise 3: Make a restart-versus-recreate persistence table.

**Expected evidence:** Writable layer survives restart but not removal; volumes follow their own lifetime.

**Why:** A restart preserves the container object. A recreate replaces it. A mounted volume is independent, so the table must name storage rather than make one blanket persistence claim.

## Exercise 4: Diagnose a missing file after compose up recreates a service.

**Expected answer:** Check whether it was written to the old disposable layer.

**Why:** The service name can stay the same while the container ID changes. A familiar name is not proof that the underlying writable layer or process is the same object.

## Exercise 5: Explain why read-only plus tmpfs permits temporary writes.

**Expected answer:** The root mount and tmpfs have different write policies.

**Why:** Read-only is evaluated for the target mount. A bounded tmpfs intentionally supplies volatile writable storage without making the application directory writable.

## Exercise 6: Choose storage for user progress and transient scratch data.

**Expected answer:** A named volume for progress and bounded temporary storage for scratch.

**Why:** The choice should follow retention and recovery requirements. Keeping every file forever increases cleanup and privacy costs; discarding user progress on replacement violates the product contract.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
