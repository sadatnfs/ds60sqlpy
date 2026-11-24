# docker-016: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-016.md`.

## Exercise 1: Locate the filesystem used by COPY --from.

**Expected evidence:** The named build stage.

**Why:** It is not a host path. This distinction lets the final stage copy exactly the artifact created by the build without relying on a developer’s local output directory.

**Approach:** Follow --from=build back to the stage declared `FROM python:3.12-slim AS build`, and its file /out/message.txt written by the RUN.

**Why this is correct:** COPY --from reads from that stage's finished filesystem, not from the host, so the final stage needs nothing from the developer's directory.

**A plausible wrong approach:** Creating out/message.txt on the host first to help the copy changes nothing, because COPY --from never looks at the context.

**How to verify:** Build the example and run the final image; it prints prepared, which can only come from the build stage.

## Exercise 2: Predict failure when a shared library is omitted.

**Expected answer:** The final process fails even if builder tests passed.

**Why:** The loader and dependencies are part of runtime requirements. A successful compile does not prove the executable can start in a different filesystem.

**Approach:** Ask what the final executable needs to start: its dynamic loader and every shared library it links, all present in the final stage.

**Why this is correct:** Builder tests run in the builder filesystem, where those libraries exist. The final stage holds only what COPY --from placed there.

**A plausible wrong approach:** Trusting the builder's passing tests and shipping fails at container start with a missing library error before main runs.

**How to verify:** Run the final image directly; a missing library shows up at once, and running ldd in a debug copy of the final stage lists what is absent.

## Exercise 3: Design a builder-to-runtime artifact list.

**Expected evidence:** Executable or package plus explicit required runtime assets.

**Why:** Include certificates or configuration defaults only when needed. The list should be small enough to review and broad enough to run correctly.

**Approach:** List each artifact the final stage needs by path: the executable or package, certificates if it makes TLS calls, and config defaults it reads.

**Why this is correct:** An explicit list keeps the final stage reviewable and makes each COPY --from line match one runtime requirement.

**A plausible wrong approach:** Copying the whole /out or the builder's /usr tree ships compilers and test files.

**How to verify:** The final image's file listing matches the artifact list, and the acceptance request passes with nothing more added.

## Exercise 4: Diagnose an accidentally shipped debug target.

**Expected answer:** Inspect final stage selection and image contents.

**Why:** A named target changes what is built. Verify the release command and artifact rather than assuming the last intended stage was selected.

**Approach:** Check which target the release build selected with --target, and inspect the resulting image's files and command.

**Why this is correct:** Without --target the last stage is built; with --target debug a debug stage is built. Either way the content shows what shipped.

**A plausible wrong approach:** Reading the Dockerfile and assuming the release stage was used fails when a CI script still passes --target debug.

**How to verify:** The CI command line names the intended target, and the image lacks debug tools when listed.

## Exercise 5: Explain why a smaller image is not automatically safer.

**Expected answer:** Correct dependencies, patching and privileges still matter.

**Why:** Size is one useful measurement, but security also depends on what executes, what it can access and how its dependencies are maintained.

**Approach:** Separate the size metric from the risks that matter: which binaries can run, what user runs them, and whether dependencies receive patches.

**Why this is correct:** A small image running as root with an unpatched library is smaller but no safer. Size cuts attack surface only when removed parts were risky.

**A plausible wrong approach:** Choosing the smallest base regardless of its update cadence can leave known vulnerabilities in place longer.

**How to verify:** Compare candidates on size, configured user, and scanner findings for the same date, and record all three.

## Exercise 6: Specify final-image acceptance.

**Expected evidence:** Run the exact final image under intended user, mounts and network.

**Why:** This exposes missing libraries, permissions and files that builder tests can hide. Preserve the exact tested image identity for delivery.

**Approach:** Run the exact final image with the user, read-only root, mounts and network it will have in use, then send the acceptance request.

**Why this is correct:** Final-stage problems such as missing files, wrong ownership or a missing library show up only in that configuration.

**A plausible wrong approach:** Accepting the release because the builder stage tests passed checks a filesystem that will never ship.

**How to verify:** Record the image ID used in the acceptance run and deploy that same ID, not a rebuilt tag.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
