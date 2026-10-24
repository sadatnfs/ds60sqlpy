# docker-005: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

A Dockerfile is a build recipe. Its instructions define a sequence of filesystem and configuration transformations. `FROM` selects the base image. `WORKDIR` selects a directory for later operations. `COPY` copies files from the build context. `RUN` executes during the build. `CMD` supplies a default command for a future container. Build-time work and runtime work are different phases.

A successful build means the build instructions completed under the builder’s inputs. It does not prove that the server starts, can write its intended volume or responds correctly. Packaging tests and runtime tests belong together. A beginner should be able to identify every file copied into the image and why it is necessary.

The maintained fixture uses only Python’s standard library, so it can teach build mechanics without a package repository. Its base image is still an external dependency during the first build. Later chapters pin immutable identities and export prepared images for disconnected use. The local tag is intentionally never pushed by a course command.

The final dot in `docker build -t NAME .` is the context directory, not punctuation to omit. Docker reads the Dockerfile relative to the command’s options and copies only eligible files from that context. The tag names the result locally. `--progress=plain` makes build steps and cache decisions visible in terminal logs.

Order instructions by dependency: runtime base, application directory, source copy, identity and command. Declare an unprivileged user after arranging readable files and writable data paths. `EXPOSE` documents an intended container port but does not publish it to your host.

## Exercise 1: Sort RUN and CMD into lifecycle phases.

Putting a long-running server in RUN can hang a build and does not preserve a running process inside the finished image. An image contains files and configuration, not a saved live server.

**Expected:** RUN executes at build time; CMD describes later startup.

## Exercise 2: Explain the final context dot.

COPY paths are evaluated against the context. Running the same command from a different directory can change available files, so record both the Dockerfile and context location.

**Expected:** It selects the current directory as build input.

## Exercise 3: Write a minimal Dockerfile for a single file app.

The minimal file should have no unrelated tools or hidden host dependencies. Each instruction should have a clear effect you can verify in the resulting image.

**Expected:** Base, workdir, explicit source copy and foreground command.

## Exercise 4: Diagnose COPY failure when a file is outside context.

Docker cannot copy arbitrary parent files through a relative escape. Expanding the context carelessly can send private material to the builder, so narrow the project layout instead.

**Expected:** Change the owned project layout or explicit context intentionally.

## Exercise 5: Explain why EXPOSE does not make localhost:8080 work.

The container process must listen on the correct interface and a host mapping must exist. An EXPOSE instruction alone establishes neither of those operational facts.

**Expected:** It is metadata; port publishing is a runtime configuration.

## Exercise 6: Define build and runtime acceptance separately.

Image creation is one stage. Running the exact image with intended user, mounts and network verifies the conditions a learner or operator will actually use.

**Expected:** Build succeeds, then endpoint and writable data behavior pass.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
