# docker-014: First capstone: build, serve, replace and explain

## Level and prerequisites

Beginner; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-013`

## Learning objectives

Produce the complete build-and-request evidence packet. Teach the project to a beginner without using hidden host state. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

A capstone combines mechanisms into an observable delivery story. The target here is deliberately small: a local HTTP application with a visible message, a health endpoint and a persistent counter. Completing it requires understanding build inputs, image identity, container state, loopback publishing, readiness and volume lifetime.

The project is successful when a new learner can reproduce the outcome from the copied fixture and explain why each step works. A screenshot of a browser alone is insufficient: it could show an old process or cached content. Combine the visible response with the exact project, image and replacement evidence.

This lab is not a benchmark, production service or shared hosting system. Its fixed host loopback port and synthetic counter keep the exercise inspectable. If the port or project identity conflicts with existing work, choose an unused owned identity before starting rather than stopping another application.

## Anatomy and a trace you can follow

Copy `courses/docker/fixtures/compose-lab/` into a new directory below `.learning/`. Read its README in full. Validate the model, build with plain progress, start with readiness, request the message and counter, and recreate the app with its volume intact. Preserve commands and observations in the lesson worksheet.

The request chain is host browser to published host loopback port to app listener to JSON handler to the volume-backed counter. A new image is packaging evidence. A new container ID with retained counter is persistence evidence. The distinction is the core of the exercise.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

## Worked example / walkthrough

### Worked example 1: Create the bounded application

These commands run from your own fixture copy.

```sh
docker compose -p ds60-docker-study config --quiet
docker compose --progress plain -p ds60-docker-study build
docker compose -p ds60-docker-study up -d --wait
```

**Expected observation:** The app is healthy and http://127.0.0.1:18080/ returns the configured message.

### Worked example 2: Prove replacement and stop cleanly

Record the counter and app container ID around replacement.

```sh
docker compose -p ds60-docker-study ps -q app
docker compose -p ds60-docker-study up -d --force-recreate --wait app
docker compose -p ds60-docker-study ps -q app
docker compose -p ds60-docker-study down
```

**Expected observation:** The ID changes, data persists, and final down stops only this project while retaining its named volume.

## Six progressive exercises

### Exercise 1: Predict every resource the project creates.

**Expected evidence:** A local image, app container, project network and named data volume.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Change the public message in the learner copy.

**Expected evidence:** The observed response matches the deliberate runtime configuration.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Produce the complete build-and-request evidence packet.

**Expected evidence:** Build logs, model validation, health state and exact JSON response.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Introduce and repair one wrong host port in a scratch model.

**Expected evidence:** Explain the first failing network hop and restore the original mapping.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Verify replacement without resetting the counter.

**Expected evidence:** Different container ID, same intended volume and nonreset counter.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Teach the project to a beginner without using hidden host state.

**Expected evidence:** A fresh-copy procedure with prerequisites, expected outputs and scoped cleanup.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Introduce and repair one wrong host port in a scratch model. Use its expected observation, Explain the first failing network hop and restore the original mapping., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/compose/gettingstarted/)
- [Official reference 2](https://docs.docker.com/reference/cli/docker/compose/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-014: First capstone: build, serve, replace and explain.
Read courses/docker/guides/docker-014.md and courses/docker/lessons/docker-014.md. Direct prerequisites: `docker-013`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
