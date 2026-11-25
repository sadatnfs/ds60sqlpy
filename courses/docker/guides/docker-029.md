# docker-029: Software bills of materials and image provenance

## Level and prerequisites

Advanced; about 120 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-028`

## Learning objectives

Design an evidence linkage table. Write a supply-chain review for the fixture. Use SBOM, provenance and attestation accurately when you explain what you observed.

## Purpose, vocabulary and mental model

A software bill of materials, or SBOM, lists components included in an artifact. Provenance records how an artifact was built, including inputs and builder information according to its format. Neither document by itself proves that every component is safe or that the claimed builder was trustworthy.

These records become useful when tied to an immutable artifact identity and a verification policy. An SBOM for yesterday’s tag is not necessarily an SBOM for today’s bytes. A provenance claim needs a trustworthy issuer and integrity verification before it can support a release decision.

The teaching image has a deliberately small application surface but still inherits a base operating system and Python runtime. Supply-chain review includes those dependencies. Copying only one server file does not mean the final image contains only one software component.

### Key terms

- **SBOM:** A software bill of materials listing the components included in an artifact.
- **Provenance:** A record of how an artifact was built, including its inputs and builder information.
- **Attestation:** A build statement, such as an SBOM or provenance record, stored with a specific image in its image index.
- **SPDX:** A standard format for exchanging SBOM data about packages, files and licenses.
- **Image digest:** The immutable identity an SBOM or provenance record must be tied to before it supports a release decision.

## Anatomy and a trace you can follow

BuildKit creates attestations at build time and attaches them to the image index as in-toto JSON. Minimal provenance (`mode=min`) is added by default; `--sbom=true` adds an SPDX SBOM produced by a scanner plugin, and `--provenance=mode=max` records a detailed build statement. Attestations need a builder that can store an image index: the default docker driver requires the containerd image store, a docker-container builder works with either store, and `--push` keeps them in the registry. The `local` and `tar` exporters write them as JSON files, such as `sbom.spdx.json`, in the root of the export. For a pushed image, `docker buildx imagetools inspect IMAGE --format "{{ json .SBOM.SPDX }}"` prints the SBOM without pulling the image.

The scanner itself runs as an image that is downloaded on first use, so treat SBOM generation as a deliberate online step. Compare the exported SBOM with a component inventory derived from the Dockerfile, and note what the source recipe cannot reveal without resolving the base image. Keep metadata generation, artifact delivery and verification as separate steps, and do not fabricate a signed result or claim a scanner passed when it was not run.

## How to use this lesson

The classroom saves `courses/docker/lessons/docker-029.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** From your fixture copy, run worked example 1 to export the build result with its SBOM into `../ds60-sbom-out`. If the engine answers that the current builder driver cannot produce attestations, record that message as your finding and stop there; switching builders is a separate decision. Otherwise open the file with `python3 -c "import json; d=json.load(open('../ds60-sbom-out/sbom.spdx.json')); doc=d.get('predicate', d); print(doc['spdxVersion'], len(doc['packages']))"`. The wrapper is an in-toto statement whose `predicate` holds the SPDX document. Search the package names for `python` and for a Debian library whose name starts with `libssl`, then note which ones your Dockerfile never mentions: they arrived with `python:3.12-slim`. Delete `../ds60-sbom-out` afterward, since it also holds a full copy of the image filesystem.

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

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

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

Exercise 4 is this chapter's boundary case: Diagnose an unsigned provenance statement from an unknown source. Identify who issued the provenance statement and whether a verification policy accepts that issuer before reading any of its fields as fact.

A clean SBOM for the shipped image says nothing about tools used only while building it. BuildKit scans the final stage by default, so in a multi-stage Dockerfile a compiler, a package manager cache or a downloaded binary used in an earlier stage never appears, even though it shaped the output. The fixture is single-stage, which hides the issue here, but a project that later adds a `builder` stage will see its SBOM stay just as short. When build stages matter to the review, set the build argument `BUILDKIT_SBOM_SCAN_STAGE=true`, globally or in the stages concerned, so they are scanned too, and state in the review which stages each inventory covers.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** Explain what an SBOM describes, what a provenance statement claims and which object both refer to.

**Transfer case.** An auditor asks whether `server.py` appears in the SBOM you exported. Predict the answer, explain it, and say where the application's own identity should be recorded instead.

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

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
