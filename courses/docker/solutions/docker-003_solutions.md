# docker-003: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

A filesystem maps paths to objects such as files and directories. An image supplies initial read-only layers. A running container sees a merged view plus its own writable changes. Creating or modifying a file in that writable layer does not alter the underlying image used by other containers.

The layer belongs to that container. A restart of the same container generally retains it. Removing and recreating a container creates a different layer, even when the new process has the same name and image. Persistent application data therefore belongs on an explicit volume or other durable store, not accidentally in a disposable container’s root filesystem.

A path is meaningful inside a filesystem namespace. `/app/server.py` inside a container need not exist at that path on your laptop. A bind mount can deliberately map a host directory into a container; it also creates a path by which container processes can change host files. Later lessons treat that relationship explicitly rather than assuming all paths are interchangeable.

The fixture Dockerfile sets `WORKDIR /app` and copies `server.py` there. `docker run IMAGE python -c ...` starts in that image’s configured directory unless overridden. `--read-only` makes the container root filesystem read-only, but a separately mounted temporary filesystem or volume can still be writable. This is a property of each mount, not a promise that the process has no state.

For diagnosis, first identify whether a file came from the image, the writable layer, a bind mount, a named volume or a temporary filesystem. Then ask which lifecycle operation affects that storage. Do not test persistence by deleting the learner’s real classroom volume.

## Exercise 1: Classify /app/server.py in the fixture.

The Dockerfile COPY instruction places it into a build layer. Reading it from a container demonstrates that the image content is visible through the container filesystem view.

**Expected:** An image-provided application file.

## Exercise 2: Predict whether a sibling container sees an unmounted new file.

Both instances start from the image. Changes in one private writable layer are not broadcast into another container simply because both use the same tag.

**Expected:** It does not share the first container writable layer.

## Exercise 3: Make a restart-versus-recreate persistence table.

A restart preserves the container object. A recreate replaces it. A mounted volume is independent, so the table must name storage rather than make one blanket persistence claim.

**Expected:** Writable layer survives restart but not removal; volumes follow their own lifetime.

## Exercise 4: Diagnose a missing file after compose up recreates a service.

The service name can stay the same while the container ID changes. A familiar name is not proof that the underlying writable layer or process is the same object.

**Expected:** Check whether it was written to the old disposable layer.

## Exercise 5: Explain why read-only plus tmpfs permits temporary writes.

Read-only is evaluated for the target mount. A bounded tmpfs intentionally supplies volatile writable storage without making the application directory writable.

**Expected:** The root mount and tmpfs have different write policies.

## Exercise 6: Choose storage for user progress and transient scratch data.

The choice should follow retention and recovery requirements. Keeping every file forever increases cleanup and privacy costs; discarding user progress on replacement violates the product contract.

**Expected:** A named volume for progress and bounded temporary storage for scratch.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
