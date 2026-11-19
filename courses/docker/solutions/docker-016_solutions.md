# docker-016: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-016.md`.

## Exercise 1: Locate the filesystem used by COPY --from.

**Expected evidence:** The named build stage.

**Why:** It is not a host path. This distinction lets the final stage copy exactly the artifact created by the build without relying on a developer’s local output directory.

## Exercise 2: Predict failure when a shared library is omitted.

**Expected answer:** The final process fails even if builder tests passed.

**Why:** The loader and dependencies are part of runtime requirements. A successful compile does not prove the executable can start in a different filesystem.

## Exercise 3: Design a builder-to-runtime artifact list.

**Expected evidence:** Executable or package plus explicit required runtime assets.

**Why:** Include certificates or configuration defaults only when needed. The list should be small enough to review and broad enough to run correctly.

## Exercise 4: Diagnose an accidentally shipped debug target.

**Expected answer:** Inspect final stage selection and image contents.

**Why:** A named target changes what is built. Verify the release command and artifact rather than assuming the last intended stage was selected.

## Exercise 5: Explain why a smaller image is not automatically safer.

**Expected answer:** Correct dependencies, patching and privileges still matter.

**Why:** Size is one useful measurement, but security also depends on what executes, what it can access and how its dependencies are maintained.

## Exercise 6: Specify final-image acceptance.

**Expected evidence:** Run the exact final image under intended user, mounts and network.

**Why:** This exposes missing libraries, permissions and files that builder tests can hide. Preserve the exact tested image identity for delivery.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
