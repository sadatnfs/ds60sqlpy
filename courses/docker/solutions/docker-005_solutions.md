# docker-005: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-005.md`.

## Exercise 1: Sort RUN and CMD into lifecycle phases.

**Expected evidence:** RUN executes at build time; CMD describes later startup.

**Why:** Putting a long-running server in RUN can hang a build and does not preserve a running process inside the finished image. An image contains files and configuration, not a saved live server.

**Approach:** Label each instruction with when it executes: RUN mkdir -p /data runs during docker build, while CMD only stores the default command in image configuration.

**Why this is correct:** The builder executes RUN in a temporary container and snapshots the filesystem. CMD changes metadata and runs only later, when a container starts.

**A plausible wrong approach:** Writing RUN python server.py to start the app blocks the build forever, because serve_forever never returns and no layer is committed.

**How to verify:** docker image inspect shows Config.Cmd as python server.py, while the build log lists the RUN step and its completion, not the server starting.

## Exercise 2: Explain the final context dot.

**Expected answer:** It selects the current directory as build input.

**Why:** COPY paths are evaluated against the context. Running the same command from a different directory can change available files, so record both the Dockerfile and context location.

**Approach:** Read the trailing dot in docker build -t ds60-docker-study:local . as the context path, the directory whose files the builder may read.

**Why this is correct:** COPY server.py resolves against that context, so the command must run from the fixture copy where server.py and the Dockerfile sit side by side.

**A plausible wrong approach:** Running the same command from the repository root sends a much larger context and fails to find the Dockerfile, which is only in the fixture directory.

**How to verify:** Run the build from the fixture copy and check that the build log reports a small context transfer and that the COPY step succeeds.

## Exercise 3: Write a minimal Dockerfile for a single file app.

**Expected evidence:** Base, workdir, explicit source copy and foreground command.

**Why:** The minimal file should have no unrelated tools or hidden host dependencies. Each instruction should have a clear effect you can verify in the resulting image.

**Approach:** Choose a base with Python, set WORKDIR /app, copy only server.py, and set an exec-form CMD that runs it in the foreground.

**Why this is correct:** Those four instructions match worked example 1 and need nothing from the host except the file. The server uses only the standard library, so no install step is required.

**A plausible wrong approach:** Adding RUN pip install of unrelated packages makes the image larger and the build dependent on a package index without changing what server.py can do.

**How to verify:** Build the image, then run python -c to check that /app/server.py exists and that Config.Cmd and WorkingDir match the recipe.

## Exercise 4: Diagnose COPY failure when a file is outside context.

**Expected answer:** Change the owned project layout or explicit context intentionally.

**Why:** Docker cannot copy arbitrary parent files through a relative escape. Expanding the context carelessly can send private material to the builder, so narrow the project layout instead.

**Approach:** Read the error as a context boundary problem: COPY ../shared/config.txt names a path outside the context directory sent to the builder.

**Why this is correct:** The builder only receives the context; relative paths cannot climb out of it. Either move the needed file into the project or choose a narrower, deliberate context.

**A plausible wrong approach:** Running docker build from / so the parent is inside the context ships every file on the host to the builder, including private material.

**How to verify:** After the layout change, the build log shows a context of the expected size and the COPY step completes without a not found error.

## Exercise 5: Explain why EXPOSE does not make `localhost:8080` work.

**Expected answer:** It is metadata; port publishing is a runtime configuration.

**Why:** The container process must listen on the correct interface and a host mapping must exist. An EXPOSE instruction alone establishes neither of those operational facts.

**Approach:** Separate image metadata from runtime wiring. EXPOSE 8080 records intent; the compose port mapping 127.0.0.1:18080:8080 actually forwards host traffic.

**Why this is correct:** server.py binds 0.0.0.0:8080 inside the container, and only a -p or ports entry creates the host side. Without it, nothing on the host listens.

**A plausible wrong approach:** Requesting `localhost:8080` after docker run without -p fails, and adding a second EXPOSE line cannot help because metadata never opens a socket.

**How to verify:** docker compose port app 8080 prints 127.0.0.1:18080, and a request to that address returns the JSON greeting.

## Exercise 6: Define build and runtime acceptance separately.

**Expected evidence:** Build succeeds, then endpoint and writable data behavior pass.

**Why:** Image creation is one stage. Running the exact image with intended user, mounts and network verifies the conditions a learner or operator will actually use.

**Approach:** Write two lists: build acceptance covers the tag existing with the intended Cmd and User; runtime acceptance covers the endpoint, the user and /data writes.

**Why this is correct:** The image declares USER 10001:10001 and a /data owned by that user, so the runtime check must confirm a counter increment succeeds under those settings.

**A plausible wrong approach:** Stopping at a green build misses errors that appear only at runtime, such as a permission failure when the non-root user writes to a mounted volume.

**How to verify:** After compose up, POST /increment returns a counter of 1 on a fresh volume, and GET /healthz returns status ready.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
