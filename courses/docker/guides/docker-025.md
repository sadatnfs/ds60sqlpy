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

The classroom saves `courses/docker/lessons/docker-025.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** Stop the study project with `docker compose -p ds60-docker-study down` so no container holds the image, then record its identity with `docker image inspect --format '{{.Id}}' ds60-docker-study:local`. Save it outside your fixture copy with `docker image save -o ../study-image.tar ds60-docker-study:local` and record `shasum -a 256 ../study-image.tar` (`sha256sum` on Linux). Remove the name with `docker image rm ds60-docker-study:local`, then try the offline run from worked example 2: it fails at once with a no-such-image error, and nothing is downloaded. Load the archive with `docker image load -i ../study-image.tar`; the engine prints `Loaded image: ds60-docker-study:local`. Inspect the ID again, compare it with your first note, and rerun the offline command to see `offline ready`. Delete `../study-image.tar` when you finish. The volume was never touched, so `up -d --wait` brings the app back with its counter.

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

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

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

Exercise 4 is this chapter's boundary case: Diagnose a missing image with --pull never. Run `docker image ls` for the exact repository and tag before the run; with `--pull never` an absent image is reported as an error rather than downloaded.

Saving by image ID instead of by name looks equivalent, because the layers are the same. It is not: `docker image save -o handoff.tar <image-id>` writes an archive whose manifest carries no repository or tag, so on the receiving engine `docker image load` reports `Loaded image ID:` followed by a digest rather than `Loaded image: ds60-docker-study:local`, and `docker image ls` shows the image without a name. Every command that names `ds60-docker-study:local` with `--pull never` then fails as if the transfer never happened. Save by reference so the name travels with the bytes, or, on the receiving side, attach the name deliberately with `docker image tag <loaded-id> ds60-docker-study:local` after checking that the loaded ID matches your handoff record.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** Recall the commands that move an image offline and the flag that proves no download happened.

**Transfer case.** A colleague on an Apple silicon laptop loads your archive, which you built on an amd64 Linux host, and the offline run prints a platform warning or fails with `exec format error`. What happened, and which handoff field would have prevented the surprise?

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

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
