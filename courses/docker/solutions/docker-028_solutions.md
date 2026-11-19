# docker-028: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-028.md`.

## Exercise 1: Parse the components of an image reference.

**Expected evidence:** Registry, repository, optional tag and optional digest.

**Why:** The registry location and image identity should be unambiguous before any authenticated operation. A familiar short tag can hide a different destination.

## Exercise 2: Predict whether adding a local tag uploads bytes.

**Expected answer:** No; local naming and registry publication are separate.

**Why:** This separation lets you prepare and inspect an artifact without distributing it. Publication requires its own intentional command and authorization.

## Exercise 3: Design a release identity record.

**Expected evidence:** Source revision, immutable image identity, platform and tested behavior.

**Why:** The record should join source and runtime evidence. A tag alone cannot preserve that relationship if it is later moved.

## Exercise 4: Diagnose an overwritten mutable release tag.

**Expected answer:** Compare recorded digest with the currently resolved artifact.

**Why:** The same label can name different content. Resolve the exact identity before concluding that earlier acceptance evidence applies.

## Exercise 5: Explain why credentials do not belong in the build context.

**Expected answer:** They can be transferred, layered or logged beyond the intended lifetime.

**Why:** Registry access is an operation credential, not application source. Use a reviewed credential channel and avoid printing values during diagnostics.

## Exercise 6: Describe a safe publication review without performing it.

**Expected answer:** Explicit destination, visibility, immutable artifact and rollback plan.

**Why:** A reviewable proposal is concrete enough to approve. It should not upload a different artifact later or silently change repository visibility.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
