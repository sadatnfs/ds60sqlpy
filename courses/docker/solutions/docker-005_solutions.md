# docker-005: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-005.md`.

## Exercise 1: Sort RUN and CMD into lifecycle phases.

**Expected evidence:** RUN executes at build time; CMD describes later startup.

**Why:** Putting a long-running server in RUN can hang a build and does not preserve a running process inside the finished image. An image contains files and configuration, not a saved live server.

## Exercise 2: Explain the final context dot.

**Expected answer:** It selects the current directory as build input.

**Why:** COPY paths are evaluated against the context. Running the same command from a different directory can change available files, so record both the Dockerfile and context location.

## Exercise 3: Write a minimal Dockerfile for a single file app.

**Expected evidence:** Base, workdir, explicit source copy and foreground command.

**Why:** The minimal file should have no unrelated tools or hidden host dependencies. Each instruction should have a clear effect you can verify in the resulting image.

## Exercise 4: Diagnose COPY failure when a file is outside context.

**Expected answer:** Change the owned project layout or explicit context intentionally.

**Why:** Docker cannot copy arbitrary parent files through a relative escape. Expanding the context carelessly can send private material to the builder, so narrow the project layout instead.

## Exercise 5: Explain why EXPOSE does not make localhost:8080 work.

**Expected answer:** It is metadata; port publishing is a runtime configuration.

**Why:** The container process must listen on the correct interface and a host mapping must exist. An EXPOSE instruction alone establishes neither of those operational facts.

## Exercise 6: Define build and runtime acceptance separately.

**Expected evidence:** Build succeeds, then endpoint and writable data behavior pass.

**Why:** Image creation is one stage. Running the exact image with intended user, mounts and network verifies the conditions a learner or operator will actually use.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
