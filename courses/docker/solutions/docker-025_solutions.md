# docker-025: explanatory solutions

These answers explain teaching fixtures, not engine results; the mechanism is in [the guide](../guides/docker-025.md).

## Exercise 1: Compare tag and digest identity.

**Expected answer:** A movable label versus content identity.

**Why:** A tag can resolve to new bytes later. Preserve immutable identity when you need to tie execution evidence to a specific artifact.

**Approach:** Treat ds60-docker-study:local as a label that points to an image, and the image ID or digest as the content's identity.

**Why this is correct:** A rebuild can move the label to new content, while a digest always names the same content.

**A plausible wrong approach:** Recording only the tag in test evidence lets a later rebuild silently replace what was tested.

**How to verify:** docker image inspect before and after a changed rebuild shows the same tag with a different ID.

## Exercise 2: Predict whether docker build uploads an image.

**Expected answer:** It does not push merely because a tag was assigned.

**Why:** Building and publishing are separate operations. The course intentionally stays local so learners can inspect output without registry credentials.

**Approach:** Trace what the build does with the tag: it names the result in the local store and talks to no registry.

**Why this is correct:** Uploading needs a separate docker push to a registry reference, which the course never runs.

**A plausible wrong approach:** Worrying that tagging the fixture published it confuses naming with distribution.

**How to verify:** No registry login is needed to build, and the image is listed only in the local docker image ls output.

## Exercise 3: Design an offline handoff record.

**Expected evidence:** Archive checksum, image identity, platform and expected command.

**Why:** The receiver needs enough context to verify both bytes and compatibility. A filename alone does not establish which program or architecture the archive contains.

**Approach:** Send study-image.tar with its checksum, the image ID, its platform and the exact command the receiver should run.

**Why this is correct:** The checksum confirms the bytes arrived intact; the ID and platform confirm which program and architecture they hold.

**A plausible wrong approach:** Sending only the archive file name leaves the receiver unable to tell an older or wrong-platform archive from the right one.

**How to verify:** The receiver recomputes the checksum, loads the archive, and compares the image ID and architecture with the record.

## Exercise 4: Diagnose a missing image with --pull never.

**Expected answer:** The run fails rather than silently downloading.

**Why:** This is useful evidence of an incomplete prepared environment. Repair the preparation deliberately instead of hiding the dependency with an implicit pull.

**Approach:** Read --pull never as a rule: if the image is not already local, the run stops instead of fetching it.

**Why this is correct:** The failure reveals that the load step was skipped or used a different tag, which is the fact the handoff needs.

**A plausible wrong approach:** Removing --pull never to make the run work quietly downloads an image and hides the incomplete preparation.

**How to verify:** Load study-image.tar, confirm docker image ls lists ds60-docker-study:local, and rerun to see offline ready.

## Exercise 5: Explain checksum integrity versus authenticity.

**Expected answer:** Matching bytes do not identify a trustworthy publisher by themselves.

**Why:** An attacker could supply both a modified archive and its hash. Trust requires an independent source or a signature verification policy.

**Approach:** Separate two questions: did the bytes change in transit, and who produced them?

**Why this is correct:** A matching hash answers only the first; anyone who swaps the archive can publish a matching hash beside it.

**A plausible wrong approach:** Trusting an archive because its hash matches the one in the same download folder accepts an attacker's pair.

**How to verify:** Get the expected hash through a separate trusted channel, or check a signature against a known key.

## Exercise 6: Define offline acceptance for the study app.

**Expected evidence:** Imported image starts with local data and no required external services.

**Why:** The test should exercise the app behavior you plan to teach. A trivial arithmetic command proves the runtime is present but not every feature of a network-dependent application.

**Approach:** Start the loaded image under --network none with the study data and run the app's own checks, not just a print command.

**Why this is correct:** The print command proves the interpreter is present; GET /healthz and GET /counter prove the app starts and reads its data.

**A plausible wrong approach:** Accepting the transfer after offline ready alone says nothing about whether server.py runs without the network.

**How to verify:** In the offline container, the health and counter routes respond over loopback with the expected JSON.

## Check your transfer

The archive carries the image for the platform it was built on, linux/amd64. On an arm64 engine the run either goes through emulation, with a warning that the requested platform does not match the host, or fails with `exec format error` where no emulator is installed. `docker image inspect --format '{{.Os}}/{{.Architecture}}' ds60-docker-study:local` shows the mismatch. The handoff record needs a platform field, and a build for linux/arm64 when that is the target. If inspect already reports arm64 and the run still fails, the cause lies elsewhere.
