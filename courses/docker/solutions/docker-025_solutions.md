# docker-025: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-025.md`.

## Exercise 1: Compare tag and digest identity.

**Expected answer:** A movable label versus content identity.

**Why:** A tag can resolve to new bytes later. Preserve immutable identity when you need to tie execution evidence to a specific artifact.

## Exercise 2: Predict whether docker build uploads an image.

**Expected answer:** It does not push merely because a tag was assigned.

**Why:** Building and publishing are separate operations. The course intentionally stays local so learners can inspect output without registry credentials.

## Exercise 3: Design an offline handoff record.

**Expected evidence:** Archive checksum, image identity, platform and expected command.

**Why:** The receiver needs enough context to verify both bytes and compatibility. A filename alone does not establish which program or architecture the archive contains.

## Exercise 4: Diagnose a missing image with --pull never.

**Expected answer:** The run fails rather than silently downloading.

**Why:** This is useful evidence of an incomplete prepared environment. Repair the preparation deliberately instead of hiding the dependency with an implicit pull.

## Exercise 5: Explain checksum integrity versus authenticity.

**Expected answer:** Matching bytes do not identify a trustworthy publisher by themselves.

**Why:** An attacker could supply both a modified archive and its hash. Trust requires an independent source or a signature verification policy.

## Exercise 6: Define offline acceptance for the study app.

**Expected evidence:** Imported image starts with local data and no required external services.

**Why:** The test should exercise the app behavior you plan to teach. A trivial arithmetic command proves the runtime is present but not every feature of a network-dependent application.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
