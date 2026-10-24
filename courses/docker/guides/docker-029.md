# docker-029: Software bills of materials and image provenance

## Level and prerequisites

Advanced; about 120 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-028`

## Learning objectives

Design an evidence linkage table. Write a supply-chain review for the fixture. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

A software bill of materials, or SBOM, lists components included in an artifact. Provenance records how an artifact was built, including inputs and builder information according to its format. Neither document by itself proves that every component is safe or that the claimed builder was trustworthy.

These records become useful when tied to an immutable artifact identity and a verification policy. An SBOM for yesterday’s tag is not necessarily an SBOM for today’s bytes. A provenance claim needs a trustworthy issuer and integrity verification before it can support a release decision.

The teaching image has a deliberately small application surface but still inherits a base operating system and Python runtime. Supply-chain review includes those dependencies. Copying only one server file does not mean the final image contains only one software component.

## Anatomy and a trace you can follow

BuildKit can produce attestations in supported workflows and exporters. Storage and publication behavior depend on the builder and image store, so do not promise that every local load preserves every attestation identically. Keep metadata generation, artifact delivery and verification as separate steps.

For an offline exercise, create a small component inventory from the Dockerfile and compare it with an actual image inspection or a prepared SBOM. Note what the source recipe cannot reveal without resolving the base image. Do not fabricate a signed result or claim a scanner passed when it was not run.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

## Worked example / walkthrough

### Worked example 1: Inventory visible dependencies

This is a source-derived teaching inventory.

```text
application: server.py, original course source
runtime: Python from selected base image
operating-system packages: inherited from resolved base
identity: record exact image and platform
```

**Expected observation:** The source inventory has explicit unknowns until the base artifact is resolved and inspected.

### Worked example 2: Separate evidence objects

The links are conceptual relationships.

```text
source + builder inputs -> image digest
image digest -> SBOM
image digest -> provenance statement -> issuer verification policy
```

**Expected observation:** Documents must refer to the same immutable artifact to support one release claim.

## Six progressive exercises

### Exercise 1: Distinguish SBOM and provenance.

**Expected evidence:** Component inventory versus build-origin evidence.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Predict what a source-only inventory misses.

**Expected evidence:** Resolved base packages and exact inherited versions.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Design an evidence linkage table.

**Expected evidence:** Every record names the same image digest and platform scope.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose an unsigned provenance statement from an unknown source.

**Expected evidence:** It is an untrusted claim until verified under a policy.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Explain exporter limitations honestly.

**Expected evidence:** Attestation generation and preservation depend on the selected workflow.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Write a supply-chain review for the fixture.

**Expected evidence:** Known source, resolved base, component record and actual acceptance limits.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose an unsigned provenance statement from an unknown source. Use its expected observation, It is an untrusted claim until verified under a policy., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/build/metadata/attestations/)
- [Official reference 2](https://docs.docker.com/build/metadata/attestations/sbom/)

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
