# docker-031: CI builds, test layers and artifact promotion

## Level and prerequisites

Advanced; about 120 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-030`

## Learning objectives

Design a parallel test partition. Write a release gate with honest limitations. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

Continuous integration runs repeatable checks when source changes. A container pipeline can validate source, build an image, test that image and preserve evidence. These are separate stages: passing source tests does not prove the packaged filesystem or startup command is correct.

Artifact promotion means moving an already tested immutable artifact through delivery stages rather than rebuilding slightly different bytes for each stage. Rebuilding with mutable dependencies can break the connection between the tested image and the deployed image. Record the exact source, build inputs and output identity.

Parallel test jobs can reduce elapsed time, but shared fixtures must remain isolated or intentionally serialized. A database test that resets a shared schema cannot be blindly sharded with another writer. The classroom’s grouped suites reflect this principle, while ordinary runtime groups use disposable projects.

## Anatomy and a trace you can follow

A useful pipeline has fast static checks, bounded unit tests, image build, real runtime failure/timeout checks and application acceptance. Store small structured receipts and bounded logs. Always execute cleanup for resources the job owns, including on failures, while preserving evidence needed to diagnose the failure.

For this project, images are built locally in CI for testing and are not pushed to a registry. A portable source ZIP is a different artifact from a built image. Both need their own content and integrity checks.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

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
{"source_hash":"measured hash","image_id":"measured image","case":"named reference","status":"observed result","cleanup":"owned resources only"}
```

**Expected observation:** The receipt binds a particular test to actual source and runtime identities.

## Six progressive exercises

### Exercise 1: Predict what a unit test cannot prove about packaging.

**Expected evidence:** Missing image files or a wrong final command can remain undetected.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Separate source ZIP and image artifacts.

**Expected evidence:** Source input package versus built executable filesystem.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Design a parallel test partition.

**Expected evidence:** Independent groups with explicit ownership for shared fixtures.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose rebuilding between acceptance and deployment.

**Expected evidence:** The new artifact may not match the tested identity.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Explain cleanup after a failed CI job.

**Expected evidence:** Remove job-owned runtime resources while retaining bounded diagnostic evidence.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Write a release gate with honest limitations.

**Expected evidence:** Named actual checks on exact artifacts, plus visible skipped surfaces.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose rebuilding between acceptance and deployment. Use its expected observation, The new artifact may not match the tested identity., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/build/ci/github-actions/)
- [Official reference 2](https://docs.docker.com/build/ci/github-actions/test-before-push/)

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
