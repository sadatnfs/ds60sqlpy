# docker-007: explanatory solutions

These answers explain teaching fixtures, not engine results; the mechanism is in [the guide](../guides/docker-007.md).

## Exercise 1: Predict the first invalidated step after editing server.py.

**Expected answer:** The COPY using that file and dependent later steps.

**Why:** The builder tracks relevant inputs. Earlier independent operations can remain reusable while operations based on changed filesystem state require new results.

**Approach:** Walk the fixture Dockerfile top to bottom and find the first instruction whose input includes server.py: COPY server.py /app/server.py.

**Why this is correct:** FROM and WORKDIR keep their cache keys, so they reuse. COPY's checksum changes, and every later step, including RUN mkdir and the metadata steps, rebuilds after it.

**A plausible wrong approach:** Expecting only the COPY step to rebuild fails, because the builder reuses a later step only when its parent layer is unchanged.

**How to verify:** Edit a comment in server.py, rebuild with --progress=plain, and confirm the log shows CACHED up to WORKDIR and executed steps from COPY onward.

## Exercise 2: Record evidence of a real cache hit.

**Expected evidence:** A specific step labeled cached in plain build logs.

**Why:** Elapsed time alone is ambiguous because network and CPU vary. A named cached step ties the observation to the builder decision being studied.

**Approach:** Capture the plain progress output of the second identical build and look for the CACHED marker beside specific step numbers.

**Why this is correct:** A CACHED label is the builder's own record that it reused a layer, which ties the evidence to the decision rather than to timing noise.

**A plausible wrong approach:** Using a shorter wall-clock time as proof fails, because a warm disk or a quiet network can make an uncached build faster too.

**How to verify:** Save both logs and point to the step lines for COPY and RUN mkdir labeled CACHED in the second log.

## Exercise 3: Reorder dependency metadata and app source conceptually.

**Expected evidence:** Stable dependency inputs precede rapidly changing source.

**Why:** This allows source edits to reuse dependencies when lockfiles remain unchanged. It does not justify ignoring a lockfile change or copying too little to perform a correct build.

**Approach:** Place a COPY of dependency metadata such as requirements.txt and its RUN install before the COPY of application source.

**Why this is correct:** Editing source then leaves the metadata checksum unchanged, so the expensive install layer is reused and only the source copy reruns.

**A plausible wrong approach:** Copying source before installing dependencies reruns the install on every code edit, and copying too few files can make the install fail.

**How to verify:** Edit only application source and rebuild; the install step should show CACHED while the source COPY runs. Then edit the lockfile and see the install run again.

## Exercise 4: Diagnose a cached step that downloads a mutable dependency.

**Expected answer:** A cache hit can preserve old bytes even with unchanged command text.

**Why:** The command can have external inputs absent from the visible file hash. Pinning and deliberate update procedures provide a stronger reproducibility story than relying on caching behavior.

**Approach:** Note that a RUN that fetches a file by URL has a cache key built from the command text, not from the bytes at that URL.

**Why this is correct:** If the server publishes a new file under the same URL, the builder still reuses the old layer, so two machines can hold different contents.

**A plausible wrong approach:** Running --no-cache on every build to stay fresh discards all reuse and still does not pin anything, so builds stay unrepeatable.

**How to verify:** Pin the download by version and checksum and verify it in the RUN; changing either value changes the command text and forces a rebuild.

## Exercise 5: Explain no-cache versus pulling a base.

**Expected answer:** Reexecuting build steps and refreshing a base are separate choices.

**Why:** One option changes cache reuse; another changes the image resolved by the base reference. Conflating them makes debugging rebuilds needlessly expensive and hard to interpret.

**Approach:** Name the two controls: --no-cache ignores existing build cache, and --pull asks the builder to resolve and fetch the FROM image again.

**Why this is correct:** The fixture builds FROM a `python:3.12-slim` tag; --no-cache can rerun every step on the same local base, while --pull may get a newer image.

**A plausible wrong approach:** Using --no-cache to pick up a base security fix fails if the local base is stale, because no new base is fetched.

**How to verify:** Compare the base image ID before and after each option with docker image inspect; only a pull can change it, while --no-cache changes step execution.

## Exercise 6: Design a build-performance experiment.

**Expected evidence:** Same engine and context, one controlled edit, named cache observations.

**Why:** Record build identity and changed inputs so timing is interpretable. Optimize the expensive invalidated step after confirming it is actually the bottleneck.

**Approach:** Fix the engine, context and base, make one controlled edit, and record the step log and timing for a cold build and a warm rebuild.

**Why this is correct:** Holding everything else constant makes the CACHED and executed steps attributable to the single edit, so the slow step is identified by evidence.

**A plausible wrong approach:** Changing the base tag, Dockerfile order and source at once leaves no way to tell which change caused the speedup or slowdown.

**How to verify:** Present a table of step number, cached or executed, and duration for each run, and name the slowest executed step as the optimization target.

## Check your transfer

Editing `app/views.py` changes only the input to the final source COPY, so the base, the requirements COPY and the `pip install` step are all served from cache and only the source copy and later steps rerun. Adding a package changes the bytes of `requirements.txt`, which invalidates that COPY, the install that follows it, and every later step, including the source copy. In plain logs the first build shows `CACHED` on the install step and the second does not. If the install step reran after a source-only edit, the source must be copied before the requirements, which is the ordering this lesson warns against.
