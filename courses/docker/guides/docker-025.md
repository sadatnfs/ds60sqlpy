# docker-025: Image names, digests and an offline transfer

## Level and prerequisites

Intermediate; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-024`

## Learning objectives

Design an offline handoff record. Define offline acceptance for the study app. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

An image reference can contain a registry, repository, tag and digest. A tag is a mutable name. A digest identifies content according to its hash format. Tags are convenient for humans; immutable identities are stronger for repeatable delivery and audit.

A local image cache is not a registry. Building an image with a tag does not upload it. `docker image save` exports image data into an archive, and `docker image load` imports an archive. This can support an offline machine after deliberately preparing the correct platform and dependencies.

An archive must be treated as executable supply-chain input. Verify its source and checksum through a trustworthy channel, inspect the imported reference, and execute only the intended image. A checksum copied from the same untrusted source is an integrity hint, not independent authenticity.

## Anatomy and a trace you can follow

The course uses local builds and performs no registry pushes. Save only the study image to a file in your learner copy. Record the image ID, platform and archive checksum. Load into a deliberately chosen compatible engine and use `--pull never` to ensure the next run does not silently fetch a missing dependency.

An offline application can still contain code that attempts network requests. Image presence is only one prerequisite. The lesson examples use local synthetic inputs so the default application behavior does not depend on external APIs.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

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

### Exercise 1: Compare tag and digest identity.

**Expected evidence:** A movable label versus content identity.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Predict whether docker build uploads an image.

**Expected evidence:** It does not push merely because a tag was assigned.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Design an offline handoff record.

**Expected evidence:** Archive checksum, image identity, platform and expected command.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose a missing image with --pull never.

**Expected evidence:** The run fails rather than silently downloading.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Explain checksum integrity versus authenticity.

**Expected evidence:** Matching bytes do not identify a trustworthy publisher by themselves.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Define offline acceptance for the study app.

**Expected evidence:** Imported image starts with local data and no required external services.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose a missing image with --pull never. Use its expected observation, The run fails rather than silently downloading., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/reference/cli/docker/image/save/)
- [Official reference 2](https://docs.docker.com/reference/cli/docker/image/load/)
- [Official reference 3](https://docs.docker.com/dhi/core-concepts/digests/)

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
