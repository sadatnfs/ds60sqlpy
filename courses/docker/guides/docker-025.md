# docker-025: Image names, digests and an offline transfer

## Level and prerequisites

Intermediate; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-024`

## Learning objectives

Design an offline handoff record. Define offline acceptance for the study app. Use image reference, tag and digest accurately when you explain what you observed.

## Purpose, vocabulary and mental model

An image reference can contain a registry, repository, tag and digest. A tag is a mutable name. A digest identifies content according to its hash format. Tags are convenient for humans; immutable identities are stronger for repeatable delivery and audit.

A local image cache is not a registry. Building an image with a tag does not upload it. `docker image save` exports image data into an archive, and `docker image load` imports an archive. This can support an offline machine after deliberately preparing the correct platform and dependencies.

An archive must be treated as executable supply-chain input. Verify its source and checksum through a trustworthy channel, inspect the imported reference, and execute only the intended image. A checksum copied from the same untrusted source is an integrity hint, not independent authenticity.

### Key terms

- **Image reference:** A name made of an optional registry, a repository, and an optional tag or digest.
- **Tag:** A mutable, human-friendly name that can be moved to different image content.
- **Digest:** A content hash that identifies exact image bytes and cannot be moved to other content.
- **`docker image save`:** The command that exports local images into an archive for transfer without a registry.
- **Archive checksum:** A hash of the archive, compared with a value from a trustworthy channel, that detects altered transfers.

## Anatomy and a trace you can follow

The course uses local builds and performs no registry pushes. Save only the study image to a file in your learner copy. Record the image ID, platform and archive checksum. Load into a deliberately chosen compatible engine and use `--pull never` to ensure the next run does not silently fetch a missing dependency.

An offline application can still contain code that attempts network requests. Image presence is only one prerequisite. The lesson examples use local synthetic inputs so the default application behavior does not depend on external APIs.

## How to use this lesson

The classroom displays this guide and saves your worksheet, `courses/docker/lessons/docker-025.md`. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example. **How to use the lessons** in the [subject README](../README.md) collects these rules in one place.

## Worked example / walkthrough

### Worked example 1: Export one local teaching image

The destination is a new file in the learner copy.

```sh
docker image save -o study-image.tar ds60-docker-study:local
```

**Expected observation:** An archive containing the selected local image; no registry operation occurs.

### Worked example 2: Import and run deliberately offline

Use only your verified archive on a compatible engine.

```sh
docker image load -i study-image.tar
docker run --rm --pull never --network none ds60-docker-study:local python -c "print('offline ready')"
```

**Expected observation:** The imported local runtime prints offline ready without an external request.

## Six progressive exercises

For each exercise, name the object involved and the phase of its lifetime before changing anything, then vary only the condition the task names. Exercises that ask you to predict, explain, compare or diagnose keep their answers in the solutions file; the others show the evidence to look for.

### Exercise 1: Compare tag and digest identity.

**Hint:** Ask which of the two can point to different bytes tomorrow.

### Exercise 2: Predict whether docker build uploads an image.

**Hint:** Check whether docker build contacts a registry when it tags.

### Exercise 3: Design an offline handoff record.

**Expected evidence:** Archive checksum, image identity, platform and expected command.

**Hint:** Write down what the receiver needs to verify and run the archive.

### Exercise 4: Diagnose a missing image with --pull never.

**Hint:** Read what --pull never does when the image is missing.

### Exercise 5: Explain checksum integrity versus authenticity.

**Hint:** Ask who could have produced bytes with the same checksum.

### Exercise 6: Define offline acceptance for the study app.

**Expected evidence:** Imported image starts with local data and no required external services.

**Hint:** Disconnect from the network and start the imported image.

## Common mistakes and diagnosis

Treating a tag as an immutable identity. Expecting a tagged build to be published. Trusting a checksum without knowing who supplied it.

Exercise 4 is this chapter's boundary case: Diagnose a missing image with --pull never. Run `docker image ls` for the exact repository and tag before the run; with `--pull never` an absent image is reported as an error rather than downloaded. Preserve the original failure and the exact changed field before retrying. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations first. Recall the commands that move an image offline and the flag that proves no download happened. Then reconstruct worked example 2 (Import and run deliberately offline) with one different value, predict what changes, and name which of image reference, tag, digest, docker image save and docker image load the change touches.

When a host session ends, run `docker compose -p ds60-docker-study down` from your fixture copy. It removes the project's containers and network but keeps named volumes; deleting a volume is a separate, deliberate reset described in the fixture README.

## Primary references

- [docker image save reference](https://docs.docker.com/reference/cli/docker/image/save/)
- [docker image load reference](https://docs.docker.com/reference/cli/docker/image/load/)
- [Image digests](https://docs.docker.com/dhi/core-concepts/digests/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-025: Image names, digests and an offline transfer.
Read courses/docker/guides/docker-025.md and courses/docker/lessons/docker-025.md. Direct prerequisites: `docker-024`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
