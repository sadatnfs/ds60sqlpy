# docker-031: CI builds, test layers and artifact promotion

## Level and prerequisites

Advanced; about 120 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-030`

## Learning objectives

Design a parallel test partition. Write a release gate with honest limitations. Use continuous integration, test stage and artifact promotion accurately when you explain what you observed.

## Purpose, vocabulary and mental model

Continuous integration runs repeatable checks when source changes. A container pipeline can validate source, build an image, test that image and preserve evidence. These are separate stages: passing source tests does not prove the packaged filesystem or startup command is correct.

Artifact promotion means moving an already tested immutable artifact through delivery stages rather than rebuilding slightly different bytes for each stage. Rebuilding with mutable dependencies can break the connection between the tested image and the deployed image. Record the exact source, build inputs and output identity.

Parallel test jobs can reduce elapsed time, but shared fixtures must remain isolated or intentionally serialized. A database test that resets a shared schema cannot be blindly sharded with another writer. The classroom’s grouped suites reflect this principle, while ordinary runtime groups use disposable projects.

### Key terms

- **Continuous integration:** Running repeatable checks automatically whenever source changes.
- **CI test stage:** A pipeline step that tests the built image itself, beyond the source tests that ran earlier.
- **Image promotion:** Artifact promotion for containers, moving one already tested immutable image through delivery stages instead of rebuilding different bytes for each.
- **Immutable digest:** The content identity that links the tested image to the deployed one.
- **Parallel jobs:** Pipeline jobs that run at the same time and need isolated or deliberately serialized shared fixtures.

## Anatomy and a trace you can follow

A useful pipeline has fast static checks, bounded unit tests, image build, real runtime failure/timeout checks and application acceptance. Store small structured receipts and bounded logs. Always execute cleanup for resources the job owns, including on failures, while preserving evidence needed to diagnose the failure.

For this project, images are built locally in CI for testing and are not pushed to a registry. A portable source ZIP is a different artifact from a built image. Both need their own content and integrity checks.

## How to use this lesson

The classroom saves `courses/docker/lessons/docker-031.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** Build a small receipt by hand. In your fixture copy run `shasum -a 256 Dockerfile server.py compose.yaml` and `docker image inspect --format '{{.Id}}' ds60-docker-study:local`, then perform one named check, such as the host request to `/healthz`, and write the hashes, the ID, the check and its result to `../ds60-receipt.json`. Now add a comment line to `server.py` and run `docker compose -p ds60-docker-study build app`: the source hash changes, the `COPY server.py` step rebuilds and the image ID differs, so the receipt no longer describes what you would ship. Remove the comment and build again; the original ID usually returns because the earlier layers are still cached, and the hashes match the receipt once more. Delete `../ds60-receipt.json` when you are done.

## Worked example / walkthrough

### Worked example 1: Design the evidence ladder

Each stage answers a different question.

```text
source checks -> unit tests -> image build -> startup -> reference execution
-> controlled failure -> saved-state replacement -> browser acceptance
```

**Expected observation:** No earlier stage substitutes for a later stage’s actual behavior.

### Worked example 2: Define a source-bound receipt

This is a schema sketch, not a completed test result.

```json
{
  "source_hash": "measured hash",
  "image_id": "measured image",
  "case": "named reference",
  "status": "observed result",
  "cleanup": "owned resources only"
}
```

**Expected observation:** The receipt binds a particular test to actual source and runtime identities.

## Six progressive exercises

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

### Exercise 1: Predict what a unit test cannot prove about packaging.

**Hint:** List what a unit test never touches, such as the image's files and command.

### Exercise 2: Separate source ZIP and image artifacts.

**Expected evidence:** Source input package versus built executable filesystem.

**Hint:** Ask which artifact you would run and which you would review.

### Exercise 3: Design a parallel test partition.

**Expected evidence:** Independent groups with explicit ownership for shared fixtures.

**Hint:** Group the tests so that no two groups write the same fixture.

### Exercise 4: Diagnose rebuilding between acceptance and deployment.

**Hint:** Compare the digest that passed acceptance with the one deployed.

### Exercise 5: Explain cleanup after a failed CI job.

**Hint:** Keep logs and identities, then remove only resources the job created.

### Exercise 6: Write a release gate with honest limitations.

**Expected evidence:** Named actual checks on exact artifacts, plus visible skipped surfaces.

**Hint:** Name each check, the artifact it ran on and what was skipped.

## Common mistakes and diagnosis

Rebuilding the image after tests and deploying an untested artifact. Letting parallel jobs share one fixture. Hiding skipped checks behind a green summary.

Exercise 4 is this chapter's boundary case: Diagnose rebuilding between acceptance and deployment. Compare the digest that passed acceptance with the digest being deployed; if they differ, the acceptance result does not yet apply.

Teams often add a `test` stage to the Dockerfile and assume every build runs it. BuildKit builds only the stages the requested target depends on, so `docker build .` producing the final stage silently skips a `test` stage that nothing copies from, and the build log simply never mentions it. A green build then proves only that packaging succeeded. Either build the test stage explicitly with `--target test` as its own pipeline step, or make the final stage depend on it, for example by copying a small marker file the tests write, and look in the build log for the test command's own output rather than trusting the stage's presence in the file.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** Recall the receipt fields and say which one ties the test result to the exact artifact.

**Transfer case.** Your pipeline builds on amd64 runners and the receipt passes, but production nodes are arm64 and pull a multi-platform index under the same tag. Which part of the receipt still applies to them?

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

## Primary references

- [Docker Build GitHub Actions](https://docs.docker.com/build/ci/github-actions/)
- [Test before push with GitHub Actions](https://docs.docker.com/build/ci/github-actions/test-before-push/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-031: CI builds, test layers and artifact promotion.
Read courses/docker/guides/docker-031.md and courses/docker/lessons/docker-031.md. Direct prerequisites: `docker-030`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
