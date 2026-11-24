# docker-028: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-028.md`.

## Exercise 1: Parse the components of an image reference.

**Expected evidence:** Registry, repository, optional tag and optional digest.

**Why:** The registry location and image identity should be unambiguous before any authenticated operation. A familiar short tag can hide a different destination.

**Approach:** Split a reference into registry host, repository path, optional tag after a colon and optional digest after @sha256.

**Why this is correct:** A short name like ds60-docker-study:local has no registry part, and the client fills in a default when talking to one.

**A plausible wrong approach:** Pushing a short name assuming it goes to your own registry may target the default public registry.

**How to verify:** Write out the fully qualified reference before any push and compare it with the intended destination.

## Exercise 2: Predict whether adding a local tag uploads bytes.

**Expected answer:** No; local naming and registry publication are separate.

**Why:** This separation lets you prepare and inspect an artifact without distributing it. Publication requires its own intentional command and authorization.

**Approach:** Trace docker tag: it adds another name for the same image ID in the local store.

**Why this is correct:** No network call happens; publishing needs a separate docker push, with credentials, to a registry.

**A plausible wrong approach:** Avoiding tags out of worry about publishing loses a useful way to name a candidate for inspection.

**How to verify:** The image inspect command in worked example 1 shows the new name, and the registry has no copy until a push.

## Exercise 3: Design a release identity record.

**Expected evidence:** Source revision, immutable image identity, platform and tested behavior.

**Why:** The record should join source and runtime evidence. A tag alone cannot preserve that relationship if it is later moved.

**Approach:** Fill each field from a separate source: the revision from version control, the digest from the registry, the platform from inspect and acceptance from a test receipt.

**Why this is correct:** Linking these fields shows which source produced which image and that this image passed which test.

**A plausible wrong approach:** Recording only a release tag cannot tie evidence to content once the tag moves.

**How to verify:** Each field in the JSON record can be checked independently, and placeholder values mark it unqualified.

## Exercise 4: Diagnose an overwritten mutable release tag.

**Expected answer:** Compare recorded digest with the currently resolved artifact.

**Why:** The same label can name different content. Resolve the exact identity before concluding that earlier acceptance evidence applies.

**Approach:** Resolve the tag's current digest and compare it with the one recorded at acceptance.

**Why this is correct:** If they differ, the tag now names other content and the earlier test results do not apply to it.

**A plausible wrong approach:** Trusting the tag because the name matches applies evidence to an image that was never tested.

**How to verify:** Deploy by the recorded digest; it pulls the accepted content regardless of where the tag points now.

## Exercise 5: Explain why credentials do not belong in the build context.

**Expected answer:** They can be transferred, layered or logged beyond the intended lifetime.

**Why:** Registry access is an operation credential, not application source. Use a reviewed credential channel and avoid printing values during diagnostics.

**Approach:** Keep registry credentials in the client's credential store or a secret mount, never in files under the build context.

**Why this is correct:** Files in the context are sent to the builder and can be copied into layers or printed in logs.

**A plausible wrong approach:** Relying on .dockerignore alone fails if a COPY . line or a renamed file slips past the pattern.

**How to verify:** Search the context and the image's files for credential files; none appear, and pushes still authenticate.

## Exercise 6: Describe a safe publication review without performing it.

**Expected answer:** Explicit destination, visibility, immutable artifact and rollback plan.

**Why:** A reviewable proposal is concrete enough to approve. It should not upload a different artifact later or silently change repository visibility.

**Approach:** Write the proposal with the full registry destination, visibility, the digest to push and how to revert.

**Why this is correct:** Naming the digest ensures what is published equals what was reviewed, not whatever the tag points to later.

**A plausible wrong approach:** Approving publish the latest build lets a different image ship than the one reviewed.

**How to verify:** A reviewer can match the digest in the proposal with the accepted record before any push is approved.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
