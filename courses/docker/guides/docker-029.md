# docker-029: Software bills of materials and image provenance

## Level and prerequisites

Advanced; about 120 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-028`

## Learning objectives

Design an evidence linkage table. Write a supply-chain review for the fixture. Use SBOM, provenance and attestation accurately when you explain what you observed.

## Purpose, vocabulary and mental model

A software bill of materials, or SBOM, lists components included in an artifact. Provenance records how an artifact was built, including inputs and builder information according to its format. Neither document by itself proves that every component is safe or that the claimed builder was trustworthy.

These records become useful when tied to an immutable artifact identity and a verification policy. An SBOM for yesterday’s tag is not necessarily an SBOM for today’s bytes. A provenance claim needs a trustworthy issuer and integrity verification before it can support a release decision.

The teaching image has a deliberately small application surface but still inherits a base operating system and Python runtime. Supply-chain review includes those dependencies. Copying only one server file does not mean the final image contains only one software component.

## Anatomy and a trace you can follow

BuildKit creates attestations at build time and attaches them to the image index as in-toto JSON. Minimal provenance (`mode=min`) is added by default; `--sbom=true` adds an SPDX SBOM produced by a scanner plugin, and `--provenance=mode=max` records a detailed build statement. Attestations need a builder that can store an image index: the default docker driver requires the containerd image store, a docker-container builder works with either store, and `--push` keeps them in the registry. The `local` and `tar` exporters write them as JSON files, such as `sbom.spdx.json`, in the root of the export. For a pushed image, `docker buildx imagetools inspect IMAGE --format "{{ json .SBOM.SPDX }}"` prints the SBOM without pulling the image.

The scanner itself runs as an image that is downloaded on first use, so treat SBOM generation as a deliberate online step. Compare the exported SBOM with a component inventory derived from the Dockerfile, and note what the source recipe cannot reveal without resolving the base image. Keep metadata generation, artifact delivery and verification as separate steps, and do not fabricate a signed result or claim a scanner passed when it was not run.

## How to use this lesson

The classroom displays this guide and saves your worksheet, `courses/docker/lessons/docker-029.md`. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example. **How to use the lessons** in the [subject README](../README.md) collects these rules in one place.

## Worked example / walkthrough

### Worked example 1: Export an SBOM next to the build result

Run this deliberately from your fixture copy; the scanner and base images may be downloaded on first use.

```sh
docker buildx build --sbom=true --output type=local,dest=../ds60-sbom-out .
ls ../ds60-sbom-out/sbom.spdx.json
```

**Expected observation:** The export directory holds the image filesystem with sbom.spdx.json at its root; its package list includes the inherited Python runtime and operating-system packages, not only server.py.

### Worked example 2: Separate evidence objects

The links are conceptual relationships.

```text
source + builder inputs -> image digest
image digest -> SBOM
image digest -> provenance statement -> issuer verification policy
```

**Expected observation:** Documents must refer to the same immutable artifact to support one release claim.

## Six progressive exercises

For each exercise, name the object involved and the phase of its lifetime before changing anything, then vary only the condition the task names. Exercises that ask you to predict, explain, compare or diagnose keep their answers in the solutions file; the others show the evidence to look for.

### Exercise 1: Distinguish SBOM and provenance.

**Hint:** Ask which document lists contents and which describes the build.

### Exercise 2: Predict what a source-only inventory misses.

**Hint:** Compare the Dockerfile's FROM line with what the base image actually contains.

### Exercise 3: Design an evidence linkage table.

**Expected evidence:** Every record names the same image digest and platform scope.

**Hint:** Make every row refer to the same digest and platform.

### Exercise 4: Diagnose an unsigned provenance statement from an unknown source.

**Hint:** Ask who signed the statement and how you would verify it.

### Exercise 5: Explain exporter limitations honestly.

**Hint:** Check whether your builder driver and image store keep attestations.

### Exercise 6: Write a supply-chain review for the fixture.

**Expected evidence:** Known source, resolved base, component record and actual acceptance limits.

**Hint:** Separate what you know, what you resolved and what remains untested.

## Common mistakes and diagnosis

Generating an SBOM for a tag instead of the exact digest you ship. Trusting provenance JSON without verifying its issuer. Expecting attestations to survive a `--load` into the classic image store.

Exercise 4 is this chapter's boundary case: Diagnose an unsigned provenance statement from an unknown source. Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status; an application request adds another layer, and a healthy container can still serve the wrong result. Preserve the original failure and the exact changed field before retrying. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here, using SBOM, provenance, attestation, SPDX and image digest. Reconstruct worked example 2 (Separate evidence objects) with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild, or why none of those operations applies to this mechanism.

When a host session ends, run `docker compose -p ds60-docker-study down` from your fixture copy. It removes the project's containers and network but keeps named volumes; deleting a volume is a separate, deliberate reset described in the fixture README.

## Primary references

- [Build attestations](https://docs.docker.com/build/metadata/attestations/)
- [SBOM attestations](https://docs.docker.com/build/metadata/attestations/sbom/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-029: Software bills of materials and image provenance.
Read courses/docker/guides/docker-029.md and courses/docker/lessons/docker-029.md. Direct prerequisites: `docker-028`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
