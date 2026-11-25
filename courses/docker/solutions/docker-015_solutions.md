# docker-015: explanatory solutions

These answers explain teaching fixtures, not engine results; the mechanism is in [the guide](../guides/docker-015.md).

## Exercise 1: Compare a cache mount and a secret mount.

**Expected answer:** Reusable acceleration versus sensitive transient input.

**Why:** The two mounts solve different problems. A cache may persist across builds; a secret should be available only to the intended step and should never become a normal artifact.

**Approach:** Compare the two RUN --mount types from the worked examples: type=cache at /root/.cache/pip and type=secret with id=demo at /run/secrets/demo.

**Why this is correct:** The cache directory persists between builds to save downloads, while the secret file exists only during its RUN step. Neither becomes part of an image layer.

**A plausible wrong approach:** Using a cache mount to hold a token because it also stays out of layers fails, since the cache persists and later builds can read it.

**How to verify:** docker history lists no layer holding /root/.cache/pip or /run/secrets/demo, and a later unrelated RUN cannot list /run/secrets.

## Exercise 2: Predict a required secret missing from the build.

**Expected answer:** The step fails before pretending to authenticate.

**Why:** Failing explicitly keeps the dependency visible. Silently using another credential would undermine both reproducibility and the learner’s understanding of which identity performed the operation.

**Approach:** Read required=true on the secret mount and predict that BuildKit stops at that RUN when no secret with id demo is supplied.

**Why this is correct:** The test -s check never runs without the file, so the build fails loudly instead of continuing with an empty or borrowed credential.

**A plausible wrong approach:** Dropping required=true so the build passes everywhere makes a missing secret look like success, and a later fetch fails with a misleading error.

**How to verify:** Build without `--secret id=demo` and note the failure at that step; rebuild with `--secret id=demo,src=` pointing at a synthetic file and the step passes.

## Exercise 3: Design a cold-build check.

**Expected evidence:** Remove reliance on cache while preserving declared public inputs.

**Why:** A cache hit should not supply an otherwise missing source file. A reproducible build can rebuild necessary artifacts from declared dependencies when acceleration state is absent.

**Approach:** Run the build with --no-cache, and also with the cache mount emptied, while keeping requirements.lock and its hashes unchanged.

**Why this is correct:** --require-hashes forces pip to fetch the exact locked wheels again, so a cold build proves the lock alone describes every dependency.

**A plausible wrong approach:** Testing only warm rebuilds can hide a wheel that exists only in the local cache and is no longer published.

**How to verify:** The cold build log shows pip downloading every locked package and completing, and the image matches the warm build's package list.

## Exercise 4: Diagnose a secret copied into an output file.

**Expected answer:** Mount isolation does not prevent the command from leaking bytes.

**Why:** The build command remains responsible for what it writes and prints. Review outputs and layers rather than treating the mount option as a universal secrecy guarantee.

**Approach:** Read the RUN command itself: a line such as cat /run/secrets/demo > /app/token writes the secret into the step's filesystem snapshot.

**Why this is correct:** The mount keeps the secret file out of the layer, but anything the command copies or prints is captured as normal output.

**A plausible wrong approach:** Concluding that type=secret guarantees secrecy, and skipping review, leaves the leaked copy in the layer and possibly in the build log.

**How to verify:** List the image's files and search the build log for the synthetic secret value; the leak appears in /app/token until the command is fixed.

## Exercise 5: Explain why ARG is unsuitable for a password.

**Expected answer:** Build metadata and history can expose values.

**Why:** Arguments are configuration inputs and can appear in provenance or logs. Use the explicit secret channel and restrict the command that reads it.

**Approach:** Trace where an ARG value goes: it is available to RUN steps and can be recorded in image history and build provenance.

**Why this is correct:** docker history can display commands that used ARG values, so a password passed with --build-arg can be read back from the image.

**A plausible wrong approach:** Passing the password as ARG and unsetting it in a later RUN still leaves the earlier history and metadata intact.

**How to verify:** Build with a synthetic --build-arg value and check docker history; then switch to a secret mount and confirm the value no longer appears.

## Exercise 6: Describe a dependency acquisition policy.

**Expected answer:** Locked inputs, deliberate network access and no default private credentials.

**Why:** Builds should state what they fetch and how its identity is verified. A learner must be able to distinguish a prepared offline run from the initial network-dependent acquisition.

**Approach:** Write a policy that names the lockfile, the package index, when network access is allowed, and which credentials, if any, a build may use.

**Why this is correct:** Hash-locked inputs make a fetch verifiable, and stating when the network is used lets a learner tell first acquisition from an offline rebuild.

**A plausible wrong approach:** Letting builds inherit whatever registry login exists on the host makes results depend on who ran them.

**How to verify:** Run the documented acquisition once, then rebuild with networking disabled for RUN steps and the cache warm; it succeeds without new fetches.

## Check your transfer

The step runs as UID 10001, so pip does not use `/root/.cache/pip`; it looks for a cache under that user's home, which is not the mounted path, and it may not be writable either, so pip works without a cache. Mount the cache where the running user's pip looks, or set `PIP_CACHE_DIR` to the mount target, and give the mount `uid=10001` so that user can write to it. The expected result is that the second build logs reused downloads. If downloads still repeat with the paths aligned, check whether `--no-cache` or a builder prune is clearing the cache between builds.
