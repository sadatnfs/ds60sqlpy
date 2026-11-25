# docker-017: explanatory solutions

These answers explain teaching fixtures, not engine results; the mechanism is in [the guide](../guides/docker-017.md).

## Exercise 1: Predict whether Linux implies amd64.

**Expected answer:** No; operating system and architecture are separate axes.

**Why:** Linux supports multiple instruction families. A release statement should name both dimensions rather than collapsing them into a single platform label.

**Approach:** Read a platform string as two parts: linux/amd64 and linux/arm64 share an OS but differ in instruction set.

**Why this is correct:** Worked example 1 builds the same Dockerfile for linux/arm64, and inspection reports Os linux and Architecture arm64 on any host.

**A plausible wrong approach:** Writing runs on Linux in a release note leaves arm64 users to discover that only amd64 was built.

**How to verify:** The image inspect template in worked example 1 prints both fields; a release note should name both.

## Exercise 2: Classify cross-compilation and emulation.

**Expected answer:** Producing target code versus executing foreign code.

**Why:** A cross-compiler can be native while its output is foreign. Emulation may permit execution but changes performance and cannot establish all native behavior.

**Approach:** Classify by what runs where: a cross-compiler is a native program that outputs target code, and emulation such as QEMU runs target code on another CPU.

**Why this is correct:** Cross-compiling never executes the output, while emulation does, but slowly and with emulator quirks.

**A plausible wrong approach:** Calling an emulated run on amd64 native arm64 qualification ignores timing and behavior differences.

**How to verify:** Label each matrix cell with built, emulated or native, and keep native arm64 performance claims for an arm64 host.

## Exercise 3: Design a two-platform evidence matrix.

**Expected evidence:** Separate build and execution columns for amd64 and arm64.

**Why:** Do not fill an execution cell from an index manifest alone. The matrix should make untested combinations visible.

**Approach:** Make a table with rows for linux/amd64 and linux/arm64 and columns for built, executed and acceptance passed.

**Why this is correct:** The index in worked example 2 lists one image per platform, so each row needs its own build and run evidence.

**A plausible wrong approach:** Marking arm64 as executed because the index contains an arm64 entry confuses publishing with running.

**How to verify:** Each filled cell names the host and the command used; any cell without evidence stays blank and labeled unqualified.

## Exercise 4: Diagnose exec format error.

**Expected answer:** Inspect architecture and executable format before app logic.

**Why:** A program can fail before its entry point because the kernel cannot load its format. Changing business logic or increasing memory will not fix that boundary.

**Approach:** Check the architecture first with docker image inspect and compare it to the host's uname -m before reading application code.

**Why this is correct:** exec format error comes from the kernel refusing a binary built for another architecture, before the program's first line.

**A plausible wrong approach:** Raising mem_limit or editing server.py has no effect, because the process never started.

**How to verify:** Rebuild for the host's platform or enable emulation; the same command then reaches the application.

## Exercise 5: Explain why multi-platform output is not always one --load result.

**Expected answer:** Exporter and image-store capabilities constrain output.

**Why:** Understand the selected build driver and local store rather than assuming every multi-platform result can be loaded identically on every engine.

**Approach:** Look at the build driver and image store: --load imports one image into the local store, and older stores may not hold a multi-platform index.

**Why this is correct:** A multi-platform result is an index pointing to several images, which needs an exporter and store that can represent it.

**A plausible wrong approach:** Expecting --platform linux/amd64,linux/arm64 --load to work on every engine fails on stores that keep only one platform per tag.

**How to verify:** docker buildx ls shows the driver; push to a registry or use a store that supports indexes, then inspect the index entries.

## Exercise 6: Write an honest portability claim.

**Expected evidence:** Name the tested platform and label other platforms unqualified.

**Why:** Source portability is valuable but weaker than observed execution. Architecture-specific dependencies and runtime behavior need their own evidence.

**Approach:** State the tested platform, the host used, and the acceptance result, then list other platforms as built but unqualified.

**Why this is correct:** The fixture uses only the standard library, so it likely ports, but native dependencies elsewhere can break per architecture.

**A plausible wrong approach:** Writing works everywhere from one amd64 run makes a claim nobody has observed.

**How to verify:** Each platform named as supported has a matching row of execution evidence.

## Check your transfer

The image has no arm64 entry, so the engine pulls the amd64 image. With emulation installed it starts and warns that the image platform does not match the host; it then runs translated, slower, and native extensions may behave differently. Without emulation it fails with `exec format error`. The publishing team should build and push an index with both `linux/amd64` and `linux/arm64`, then test each platform separately. If inspection on the laptop showed `linux/arm64` and the run still failed, the problem would be in the image contents, not platform selection.
