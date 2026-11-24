# docker-031: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-031.md`.

## Exercise 1: Predict what a unit test cannot prove about packaging.

**Expected answer:** Missing image files or a wrong final command can remain undetected.

**Why:** Unit tests may run in a richer host environment. Execute the final image to observe its real dependency and filesystem contract.

**Approach:** Ask where unit tests run: often on the CI host with its own Python, not inside the final image.

**Why this is correct:** A Dockerfile that forgets COPY server.py, or sets the wrong CMD, still passes tests that import the code from the checkout.

**A plausible wrong approach:** Gating release on unit tests alone ships an image that may not start.

**How to verify:** Add a step that runs the built image and requests /healthz; it fails when the image is missing a file.

## Exercise 2: Separate source ZIP and image artifacts.

**Expected evidence:** Source input package versus built executable filesystem.

**Why:** They have different consumers and validation requirements. A clean archive does not establish that the image starts.

**Approach:** Separate the source archive, which developers and builders read, from the image, which an engine runs.

**Why this is correct:** The archive's checks cover files and formatting; the image's checks cover startup, user and runtime files.

**A plausible wrong approach:** Treating a clean source ZIP as proof the image works skips the stage where packaging errors show up.

**How to verify:** Each artifact has its own receipt: archive hash and checks, image ID and startup results.

## Exercise 3: Design a parallel test partition.

**Expected evidence:** Independent groups with explicit ownership for shared fixtures.

**Why:** Parallelism is valuable only when tests do not corrupt one another’s state. Preserve required serialization for shared resources.

**Approach:** Group tests so that groups share no project name, volume or port, and keep tests that share state in one group.

**Why this is correct:** Independent groups can run together safely; groups that share study-data or port 18080 would interfere.

**A plausible wrong approach:** Running every test in parallel to save time makes counter assertions fail at random.

**How to verify:** Each group's resources carry a unique project name, and repeated parallel runs give the same results.

## Exercise 4: Diagnose rebuilding between acceptance and deployment.

**Expected answer:** The new artifact may not match the tested identity.

**Why:** Mutable dependencies and timestamps can change output. Promote the tested artifact or qualify the newly built one explicitly.

**Approach:** Compare the image ID that passed acceptance with the one deployed after the rebuild.

**Why this is correct:** Unpinned base images or dependencies can change between builds, so the rebuild may differ from what was tested.

**A plausible wrong approach:** Assuming the same source always gives the same image deploys untested content.

**How to verify:** Promote the tested ID directly, or run acceptance again on the rebuilt ID before deploying it.

## Exercise 5: Explain cleanup after a failed CI job.

**Expected answer:** Remove job-owned runtime resources while retaining bounded diagnostic evidence.

**Why:** Failure should not leave a cluster or volume consuming resources indefinitely. Cleanup must not erase the only failure receipt or affect unrelated projects.

**Approach:** After a failure, save logs and the receipt first, then remove only resources labeled with the job's project name.

**Why this is correct:** This keeps the evidence while freeing containers and volumes the job created.

**A plausible wrong approach:** Running a broad prune after each failure deletes the evidence and can remove other projects' resources.

**How to verify:** The job's resources are gone, the logs remain in artifacts, and other projects' containers are untouched.

## Exercise 6: Write a release gate with honest limitations.

**Expected evidence:** Named actual checks on exact artifacts, plus visible skipped surfaces.

**Why:** A gate should report what ran, not infer broad acceptance from static configuration. Different engines and architectures may still require separate qualification.

**Approach:** List each check that ran, the exact image ID it ran on, and the surfaces skipped, such as arm64 or other engines.

**Why this is correct:** Visible skips let readers see what the gate does not cover.

**A plausible wrong approach:** Marking the release fully tested because the config defines many checks conflates defined with executed.

**How to verify:** The gate output shows ran, passed or skipped for each check, with the image ID.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
