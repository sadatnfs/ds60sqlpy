# docker-016: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

A multi-stage Dockerfile uses more than one FROM instruction. Each stage has its own filesystem and configuration. A builder stage can contain compilers and tests; a final stage can copy only the artifacts required to run. This reduces unnecessary tooling in the shipped image and makes the build-to-runtime boundary inspectable.

Copying a binary is not proof that it is self-contained. Dynamically linked programs require compatible libraries and an appropriate loader. Language runtimes, certificates, timezone data and user identity can also be necessary. A tiny image that fails at startup is not an improvement over a larger correct one.

Multi-stage design is about an explicit artifact contract. Define what the build produces, what tests validate it, what the final image needs and how the final image is exercised. The runtime test must execute the final stage, because tests in the builder can pass using files or tools absent from the shipped stage.

Name stages with `AS build`, then use `COPY --from=build /path /destination`. The source path refers to that stage’s filesystem, not the local host. `--target` deliberately stops at a named stage for debugging or testing. Do not accidentally distribute a debug stage containing credentials or development-only files.

The following Python example demonstrates stage selection with a text artifact; compiled-language lessons apply the same pattern to actual build output. It does not claim to reduce Python runtime size. A real optimized build requires measuring the resulting image and testing its runtime assumptions.

## Exercise 1: Locate the filesystem used by COPY --from.

It is not a host path. This distinction lets the final stage copy exactly the artifact created by the build without relying on a developer’s local output directory.

**Expected:** The named build stage.

## Exercise 2: Predict failure when a shared library is omitted.

The loader and dependencies are part of runtime requirements. A successful compile does not prove the executable can start in a different filesystem.

**Expected:** The final process fails even if builder tests passed.

## Exercise 3: Design a builder-to-runtime artifact list.

Include certificates or configuration defaults only when needed. The list should be small enough to review and broad enough to run correctly.

**Expected:** Executable or package plus explicit required runtime assets.

## Exercise 4: Diagnose an accidentally shipped debug target.

A named target changes what is built. Verify the release command and artifact rather than assuming the last intended stage was selected.

**Expected:** Inspect final stage selection and image contents.

## Exercise 5: Explain why a smaller image is not automatically safer.

Size is one useful measurement, but security also depends on what executes, what it can access and how its dependencies are maintained.

**Expected:** Correct dependencies, patching and privileges still matter.

## Exercise 6: Specify final-image acceptance.

This exposes missing libraries, permissions and files that builder tests can hide. Preserve the exact tested image identity for delivery.

**Expected:** Run the exact final image under intended user, mounts and network.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
