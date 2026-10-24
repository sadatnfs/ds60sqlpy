# docker-006: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

The build context is the set of files a builder may use. A `.dockerignore` file removes matching paths from that input. This reduces transfer size and prevents accidental inclusion of caches, learner data, credentials and repository history. It is a packaging boundary, not a substitute for reviewing the Dockerfile and resulting image.

A Dockerfile can accidentally copy too much with `COPY . .`. Even if a later instruction deletes a secret, the earlier image layer may retain it. The safe design is to avoid supplying sensitive data as ordinary layer input at all. Build secrets use a separate mechanism covered later; runtime secrets use another lifecycle again.

The fixture keeps its context tiny: server source, Dockerfile, Compose definition and ignore rules. Learner notes and progress live outside the source image. Different builders can run remotely, so context minimization also makes it easier to know which files leave your machine when building against a selected endpoint.

Ignore patterns are evaluated relative to the build context. Negated patterns can include an otherwise ignored path, and ordering can matter. Use a simple allowlist or a short reviewed exclude list for a small teaching project. Do not assume `.gitignore` automatically controls Docker build inputs.

Inspect the actual image after a representative build. A source manifest can assert intended exclusions, while an image file listing demonstrates what was packaged. Avoid printing secret content while verifying absence; inspect names or expected safe inventory instead.

## Exercise 1: Predict whether .gitignore protects Docker context.

The tools use distinct input rules. A file ignored by Git can still be available to a Docker build unless the Docker context rules or explicit copy list exclude it.

**Expected:** No automatic equivalence exists.

## Exercise 2: Identify three private paths to exclude.

These have different reasons for exclusion: secrets, private progress and historical metadata. A source release should make all three decisions explicit.

**Expected:** Environment files, learner data and repository history.

## Exercise 3: Design a context inventory for the fixture.

An inventory is easier to inspect than a large directory copied indiscriminately. It also makes a missing dependency visible rather than relying on a developer machine file.

**Expected:** A short list of necessary public build inputs.

## Exercise 4: Explain why deleting a secret in a later layer is insufficient.

Layered filesystems record changes; deleting a path from the merged view does not rewrite earlier layers. Prevention is safer than attempting to erase a secret after packaging it.

**Expected:** The earlier layer can retain the copied bytes.

## Exercise 5: Check that an ignored required source produces a useful failure.

A deterministic failure makes the missing build input visible. Repair the intended context rules without widening them to unrelated parent directories.

**Expected:** COPY fails instead of silently borrowing a host file.

## Exercise 6: Describe source and image privacy acceptance.

No one check covers every route. Input exclusion prevents accidental transfer; explicit copy rules limit layering; final inspection tests the produced artifact against the intended public inventory.

**Expected:** Review inputs, build recipe and safe final file inventory.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
