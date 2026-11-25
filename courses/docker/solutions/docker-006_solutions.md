# docker-006: explanatory solutions

These answers explain teaching fixtures, not engine results; the mechanism is in [the guide](../guides/docker-006.md).

## Exercise 1: Predict whether .gitignore protects Docker context.

**Expected answer:** No automatic equivalence exists.

**Why:** The tools use distinct input rules. A file ignored by Git can still be available to a Docker build unless the Docker context rules or explicit copy list exclude it.

**Approach:** Compare the two rule files by their consumers: Git reads .gitignore, while the Docker builder reads only .dockerignore in the context root.

**Why this is correct:** The builder never looks at .gitignore, so an untracked .env next to the Dockerfile is still sent unless .dockerignore excludes it.

**A plausible wrong approach:** Relying on .gitignore because the file is not committed fails exactly when it matters, since local secrets are usually ignored by Git yet present on disk.

**How to verify:** Place a harmless test file covered only by .gitignore, build with COPY . /probe, and list /probe; the file is present until .dockerignore names it.

## Exercise 2: Predict whether the pattern `*.pyc` excludes `app/__pycache__/server.cpython-312.pyc`.

**Expected answer:** It does not; `*.pyc` matches only at the context root, so the nested file needs `**/*.pyc`.

**Why:** Docker matches each pattern against the path from the context root, and a single `*` never crosses a directory separator. Only `**` spans directories, which is why .gitignore habits mislead here: Git matches a slash-free pattern at any depth.

**Approach:** Evaluate *.pyc against the full path from the context root, app/__pycache__/server.cpython-312.pyc, remembering that a single star stops at a slash.

**Why this is correct:** The root-only pattern cannot match a nested path, while the fixture's **/*.pyc and **/__pycache__ entries cover any depth.

**A plausible wrong approach:** Copying the habit from .gitignore, where a slash-free pattern matches anywhere, leaves nested bytecode in the context.

**How to verify:** Add a nested .pyc file in a scratch copy, build with a broad COPY, and confirm the file is present with *.pyc and absent with **/*.pyc.

## Exercise 3: Design a context inventory for the fixture.

**Expected evidence:** A short list of necessary public build inputs.

**Why:** An inventory is easier to inspect than a large directory copied indiscriminately. It also makes a missing dependency visible rather than relying on a developer machine file.

**Approach:** List the files the Dockerfile reads: the Dockerfile itself, .dockerignore and server.py, and nothing more, given that the only COPY names server.py.

**Why this is correct:** That short inventory makes review possible and matches the fixture's .dockerignore, which also excludes .git, .learning, .env files, logs, tar archives and JSON.

**A plausible wrong approach:** Writing COPY . /app to be safe copies README.md, compose.yaml and any stray local file, so the inventory stops being something a reviewer can check.

**How to verify:** Compare the inventory to the image by running python -c to list /app; only server.py appears there.

## Exercise 4: Explain why deleting a secret in a later layer is insufficient.

**Expected answer:** The earlier layer can retain the copied bytes.

**Why:** Layered filesystems record changes; deleting a path from the merged view does not rewrite earlier layers. Prevention is safer than attempting to erase a secret after packaging it.

**Approach:** Picture the layer stack: COPY secret.txt creates one layer, and RUN rm secret.txt adds a later layer with a whiteout entry hiding that path.

**Why this is correct:** Each layer is stored and distributed separately. Hiding a path in the merged view leaves the bytes in the earlier layer, recoverable by anyone holding the image.

**A plausible wrong approach:** Adding the rm in the same Dockerfile and calling the image clean fails, because docker save or a registry pull still exposes the earlier layer.

**How to verify:** docker history shows both steps with sizes, and the secret-bearing layer is still listed; the fix is to keep the file out of the context entirely.

## Exercise 5: Check that an ignored required source produces a useful failure.

**Expected evidence:** COPY fails instead of silently borrowing a host file.

**Why:** A deterministic failure makes the missing build input visible. Repair the intended context rules without widening them to unrelated parent directories.

**Approach:** Exclude server.py in a scratch .dockerignore and predict which instruction fails and with what kind of error.

**Why this is correct:** The context no longer contains server.py, so COPY server.py /app/server.py stops the build with a not-found error instead of using a stale or host copy.

**A plausible wrong approach:** Removing the ignore rule for all Python files to fix it widens the context to nested .pyc and other files when only server.py needed restoring.

**How to verify:** The build log names the failing COPY step; after restoring the precise rule, the build passes and the image lists only /app/server.py.

## Exercise 6: Describe source and image privacy acceptance.

**Expected answer:** Review inputs, build recipe and safe final file inventory.

**Why:** No one check covers every route. Input exclusion prevents accidental transfer; explicit copy rules limit layering; final inspection tests the produced artifact against the intended public inventory.

**Approach:** Check three places in order: .dockerignore excludes private inputs, the Dockerfile copies named files only, and the finished image holds only the intended files.

**Why this is correct:** Each check catches a different leak: the context check stops transfer, explicit COPY limits layering, and image inspection catches anything that slipped through.

**A plausible wrong approach:** Trusting a single scan of the final image misses secrets that were copied and later deleted, since a merged-view listing cannot show hidden earlier layers.

**How to verify:** Record the .dockerignore entries, the COPY lines and a listing of /app and /data from the built image, and confirm each matches the public inventory.

## Check your transfer

`*.key` in `.dockerignore` matches only at the root of the build context, unlike `.gitignore`, so a nested `config/tls/server.key` is still sent and copied. The corrected rule is `**/*.key`. To prove the fix, build a throwaway stage that copies the whole context and list it with `find`, or check that a `COPY config/tls/server.key` step now fails because the file is absent. The key must also be rotated, since earlier images already contain it. Seeing `server.key` in the listing after the change would show that the rule or the context path is still wrong.
