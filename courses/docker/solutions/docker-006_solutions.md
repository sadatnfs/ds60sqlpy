# docker-006: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-006.md`.

## Exercise 1: Predict whether .gitignore protects Docker context.

**Expected answer:** No automatic equivalence exists.

**Why:** The tools use distinct input rules. A file ignored by Git can still be available to a Docker build unless the Docker context rules or explicit copy list exclude it.

## Exercise 2: Predict whether the pattern `*.pyc` excludes `app/__pycache__/server.cpython-312.pyc`.

**Expected answer:** It does not; `*.pyc` matches only at the context root, so the nested file needs `**/*.pyc`.

**Why:** Docker matches each pattern against the path from the context root, and a single `*` never crosses a directory separator. Only `**` spans directories, which is why .gitignore habits mislead here: Git matches a slash-free pattern at any depth.

## Exercise 3: Design a context inventory for the fixture.

**Expected evidence:** A short list of necessary public build inputs.

**Why:** An inventory is easier to inspect than a large directory copied indiscriminately. It also makes a missing dependency visible rather than relying on a developer machine file.

## Exercise 4: Explain why deleting a secret in a later layer is insufficient.

**Expected answer:** The earlier layer can retain the copied bytes.

**Why:** Layered filesystems record changes; deleting a path from the merged view does not rewrite earlier layers. Prevention is safer than attempting to erase a secret after packaging it.

## Exercise 5: Check that an ignored required source produces a useful failure.

**Expected evidence:** COPY fails instead of silently borrowing a host file.

**Why:** A deterministic failure makes the missing build input visible. Repair the intended context rules without widening them to unrelated parent directories.

## Exercise 6: Describe source and image privacy acceptance.

**Expected answer:** Review inputs, build recipe and safe final file inventory.

**Why:** No one check covers every route. Input exclusion prevents accidental transfer; explicit copy rules limit layering; final inspection tests the produced artifact against the intended public inventory.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
