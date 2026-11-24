# docker-014: First capstone: build, serve, replace and explain

## Level and prerequisites

Beginner; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-013`

## Learning objectives

Produce the complete build-and-request evidence packet. Teach the project to a beginner without using hidden host state. Use image rebuild, container replacement and persistent data accurately when you explain what you observed.

## Purpose, vocabulary and mental model

A capstone combines mechanisms into an observable delivery story. The target here is deliberately small: a local HTTP application with a visible message, a health endpoint and a persistent counter. Completing it requires understanding build inputs, image identity, container state, loopback publishing, readiness and volume lifetime.

The project is successful when a new learner can reproduce the outcome from the copied fixture and explain why each step works. A screenshot of a browser alone is insufficient: it could show an old process or cached content. Combine the visible response with the exact project, image and replacement evidence.

This lab is not a benchmark, production service or shared hosting system. Its fixed host loopback port and synthetic counter keep the exercise inspectable. If the port or project identity conflicts with existing work, choose an unused owned identity before starting rather than stopping another application.

### Key terms

- **Image rebuild:** Running the build again from current inputs to produce a new image identity for the changed source.
- **Container replacement:** Removing the old container and starting a new one from the chosen image under the same project.
- **Persistent data:** State kept on a named volume, such as the fixture counter, that must survive container replacement.
- **Image identity:** The image ID or digest that shows which build a container actually runs, unlike a reusable tag.
- **Health endpoint:** A small HTTP path the application answers to report readiness without changing any data.

## Anatomy and a trace you can follow

Copy `courses/docker/fixtures/compose-lab/` into a new directory below `.learning/`. Read its README in full. Validate the model, build with plain progress, start with readiness, request the message and counter, and recreate the app with its volume intact. Preserve commands and observations in the lesson worksheet.

The request chain is host browser to published host loopback port to app listener to JSON handler to the volume-backed counter. A new image is packaging evidence. A new container ID with retained counter is persistence evidence. The distinction is the core of the exercise.

## How to use this lesson

The classroom displays this guide and saves your worksheet, `courses/docker/lessons/docker-014.md`. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example. **How to use the lessons** in the [subject README](../README.md) collects these rules in one place.

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

For each exercise, name the object involved and the phase of its lifetime before changing anything, then vary only the condition the task names. Exercises that ask you to predict, explain, compare or diagnose keep their answers in the solutions file; the others show the evidence to look for.

### Exercise 1: Predict every resource the project creates.

**Hint:** Read compose.yaml for the image, services, networks and volumes.

### Exercise 2: Change the public message in the learner copy.

**Expected evidence:** The observed response matches the deliberate runtime configuration.

**Hint:** Change APP_MESSAGE, recreate the app and request /.

### Exercise 3: Produce the complete build-and-request evidence packet.

**Expected evidence:** Build logs, model validation, health state and exact JSON response.

**Hint:** Follow the order build, validate, start, wait for health, then request.

### Exercise 4: Introduce and repair one wrong host port in a scratch model.

**Expected evidence:** Explain the first failing network hop and restore the original mapping.

**Hint:** Change only the host side of the mapping and test each hop.

### Exercise 5: Verify replacement without resetting the counter.

**Expected evidence:** Different container ID, same intended volume and nonreset counter.

**Hint:** Record the container ID and counter before and after recreation.

### Exercise 6: Teach the project to a beginner without using hidden host state.

**Expected evidence:** A fresh-copy procedure with prerequisites, expected outputs and scoped cleanup.

**Hint:** Start from a fresh copy and write down every prerequisite you use.

## Common mistakes and diagnosis

Editing the maintained fixture instead of a learner copy. Treating a successful build as proof that the app serves the right response. Removing the volume when only the container needed replacing.

Exercise 4 is this chapter's boundary case: Introduce and repair one wrong host port in a scratch model. Its expected observation is: Explain the first failing network hop and restore the original mapping. Use it to avoid treating a successful command as proof of the wrong claim. Change only the host side of one published port in a scratch copy, record the first failing request, then restore the mapping and confirm the original request succeeds again. Preserve the original failure and the exact changed field before retrying. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations first. Recall the container IDs before and after recreation and what their difference proves about replacement. Then reconstruct worked example 2 (Prove replacement and stop cleanly) with one different value, predict what changes, and name which of image rebuild, container replacement, persistent data and evidence record the change touches.

When a host session ends, run `docker compose -p ds60-docker-study down` from your fixture copy. It removes the project's containers and network but keeps named volumes; deleting a volume is a separate, deliberate reset described in the fixture README.

## Primary references

- [Docker Compose quickstart](https://docs.docker.com/compose/gettingstarted/)
- [docker compose reference](https://docs.docker.com/reference/cli/docker/compose/)

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
