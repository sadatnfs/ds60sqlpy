# docker-025: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

An image reference can contain a registry, repository, tag and digest. A tag is a mutable name. A digest identifies content according to its hash format. Tags are convenient for humans; immutable identities are stronger for repeatable delivery and audit.

A local image cache is not a registry. Building an image with a tag does not upload it. `docker image save` exports image data into an archive, and `docker image load` imports an archive. This can support an offline machine after deliberately preparing the correct platform and dependencies.

An archive must be treated as executable supply-chain input. Verify its source and checksum through a trustworthy channel, inspect the imported reference, and execute only the intended image. A checksum copied from the same untrusted source is an integrity hint, not independent authenticity.

The course uses local builds and performs no registry pushes. Save only the study image to a file in your learner copy. Record the image ID, platform and archive checksum. Load into a deliberately chosen compatible engine and use `--pull never` to ensure the next run does not silently fetch a missing dependency.

An offline application can still contain code that attempts network requests. Image presence is only one prerequisite. The lesson examples use local synthetic inputs so the default application behavior does not depend on external APIs.

## Exercise 1: Compare tag and digest identity.

A tag can resolve to new bytes later. Preserve immutable identity when you need to tie execution evidence to a specific artifact.

**Expected:** A movable label versus content identity.

## Exercise 2: Predict whether docker build uploads an image.

Building and publishing are separate operations. The course intentionally stays local so learners can inspect output without registry credentials.

**Expected:** It does not push merely because a tag was assigned.

## Exercise 3: Design an offline handoff record.

The receiver needs enough context to verify both bytes and compatibility. A filename alone does not establish which program or architecture the archive contains.

**Expected:** Archive checksum, image identity, platform and expected command.

## Exercise 4: Diagnose a missing image with --pull never.

This is useful evidence of an incomplete prepared environment. Repair the preparation deliberately instead of hiding the dependency with an implicit pull.

**Expected:** The run fails rather than silently downloading.

## Exercise 5: Explain checksum integrity versus authenticity.

An attacker could supply both a modified archive and its hash. Trust requires an independent source or a signature verification policy.

**Expected:** Matching bytes do not identify a trustworthy publisher by themselves.

## Exercise 6: Define offline acceptance for the study app.

The test should exercise the app behavior you plan to teach. A trivial arithmetic command proves the runtime is present but not every feature of a network-dependent application.

**Expected:** Imported image starts with local data and no required external services.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
