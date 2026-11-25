# docker-006: Build context, .dockerignore and accidental data exposure

## Level and prerequisites

Beginner; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-005`

## Learning objectives

Design a context inventory for the fixture. Describe source and image privacy acceptance. Use build context, .dockerignore and ignore patterns accurately when you explain what you observed.

## Purpose, vocabulary and mental model

The build context is the set of files a builder may use. A `.dockerignore` file removes matching paths from that input. This reduces transfer size and prevents accidental inclusion of caches, learner data, credentials and repository history. It is a packaging boundary, not a substitute for reviewing the Dockerfile and resulting image.

A Dockerfile can accidentally copy too much with `COPY . .`. Even if a later instruction deletes a secret, the earlier image layer may retain it. The safe design is to avoid supplying sensitive data as ordinary layer input at all. Build secrets use a separate mechanism covered later; runtime secrets use another lifecycle again.

The fixture keeps its context tiny: server source, Dockerfile, Compose definition and ignore rules. Learner notes and progress live outside the source image. Different builders can run remotely, so context minimization also makes it easier to know which files leave your machine when building against a selected endpoint.

### Key terms

- **Build context:** The set of files a builder may read during a build, usually the directory passed to the build command.
- **.dockerignore:** A file of patterns that removes matching paths from the build context before the builder receives it.
- **Ignore pattern:** One line in .dockerignore, such as a directory name or glob, that excludes matching paths.
- **Layer history:** The stored record of each image layer, which can keep a file even after a later instruction deletes it.
- **Explicit COPY:** Copying only named files instead of the whole context, so every file in the image has a known reason to be there.

## Anatomy and a trace you can follow

Ignore patterns are evaluated relative to the build context root with Go's filepath.Match rules, where `*` never crosses a `/`. A pattern such as `.env` or `*.log` therefore excludes only files at the root; `**/.env` and `**/*.log` match at any depth because `**` spans any number of directories. Negated patterns can include an otherwise ignored path, and ordering can matter. Use a simple allowlist or a short reviewed exclude list for a small teaching project. Do not assume `.gitignore` automatically controls Docker build inputs.

Inspect the actual image after a representative build. A source manifest can assert intended exclusions, while an image file listing demonstrates what was packaged. Avoid printing secret content while verifying absence; inspect names or expected safe inventory instead.

## How to use this lesson

The classroom saves `courses/docker/lessons/docker-006.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** Make a scratch copy of the fixture and add three decoys: `.env` containing a fake value, a nested `notes/debug.log`, and `cache/__pycache__/x.pyc`. Move the fixture's `.dockerignore` aside, build once, and read the transferred context size in the plain log. Put the ignore file back and build again; the context shrinks. To prove exclusion rather than guess it, write a two-line `ctx.Dockerfile` containing `FROM ds60-docker-study:local` and `COPY . /ctx`, build it with `-f ctx.Dockerfile -t ds60-ctx-check .`, and list the result with `docker run --rm ds60-ctx-check find /ctx`. Only the files you meant to send should appear. Remove the decoys, `ctx.Dockerfile` and the `ds60-ctx-check` image when you finish, and never put a real secret in a decoy.

## Worked example / walkthrough

### Worked example 1: Define a small ignore boundary

These are illustrative rules for the learner copy.

```text
.git
.learning
**/.env
**/*.log
**/__pycache__
**/*.pyc
```

**Expected observation:** Matching paths at any depth are unavailable to COPY; without the `**/` prefix a pattern such as `*.pyc` matches only at the context root, unlike .gitignore.

### Worked example 2: Prefer explicit source copying

Explicit paths make packaging intent visible.

```dockerfile
COPY server.py /app/server.py
```

**Expected observation:** Only the named app file is copied by this instruction; unrelated project files are not implicitly included.

## Six progressive exercises

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

### Exercise 1: Predict whether .gitignore protects Docker context.

**Hint:** Ask which tool reads .gitignore and which file the Docker build client reads.

### Exercise 2: Predict whether the pattern `*.pyc` excludes `app/__pycache__/server.cpython-312.pyc`.

**Hint:** Ask whether a single `*` can match a `/` in a path.

### Exercise 3: Design a context inventory for the fixture.

**Expected evidence:** A short list of necessary public build inputs.

**Hint:** List the files the Dockerfile actually copies or reads.

### Exercise 4: Explain why deleting a secret in a later layer is insufficient.

**Hint:** Run docker history on an image and treat each line as a separately saved change.

### Exercise 5: Check that an ignored required source produces a useful failure.

**Expected evidence:** COPY fails instead of silently borrowing a host file.

**Hint:** Ignore server.py in a scratch copy and read the COPY error.

### Exercise 6: Describe source and image privacy acceptance.

**Hint:** Check three places: what enters the context, what the Dockerfile copies and what the final image contains.

## Common mistakes and diagnosis

Writing `.env` or `*.log` and expecting nested files to be excluded; only `**/` patterns match at any depth. Assuming `.gitignore` controls the build context. Using `COPY . .` and deleting a secret in a later step.

Exercise 4 is this chapter's boundary case: Explain why deleting a secret in a later layer is insufficient. Use `docker history` on the image to list every layer with its size; a later `rm` step does not remove the earlier `COPY` layer from that list.

Another misconception is that a build argument is a safe way to pass a token, as in `ARG NPM_TOKEN` followed by a RUN step that uses it. Build arguments are recorded in the image history, and `docker history --no-trunc` can show the value in the RUN line that consumed it. The correction is a BuildKit secret mount, `RUN --mount=type=secret,id=npm_token ...`, which exposes the value as a file only during that one step and keeps it out of every layer and the history. Rotating a credential that has already been built into a pushed image is still necessary, because removing it later does not recall copies already pulled.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** Name two files from the fixture directory that should never reach the build context, and the ignore rule that excludes each.

**Transfer case.** A project's `.dockerignore` contains `node_modules` and `*.key`. The build still copies `config/tls/server.key` into the image. Explain why, write the corrected rule, and say how you would prove the fix worked without trusting the build's success message.

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

## Primary references

- [Build context](https://docs.docker.com/build/concepts/context/)
- [Dockerfile reference: .dockerignore file](https://docs.docker.com/reference/dockerfile/#dockerignore-file)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-006: Build context, .dockerignore and accidental data exposure.
Read courses/docker/guides/docker-006.md and courses/docker/lessons/docker-006.md. Direct prerequisites: `docker-005`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
