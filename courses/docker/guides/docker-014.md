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

The classroom saves `courses/docker/lessons/docker-014.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** Rehearse the capstone handoff on a second copy so your main counter stays intact. Copy the fixture to `.learning/docker-study-rehearsal` with the same guard used for the first copy, change only the host side of the port to `127.0.0.1:18081`, and use `-p ds60-docker-study-rehearsal` in every command. Run validation, build, `up -d --wait`, one root request on port 18081 and two increments, then a forced recreation and a second counter read. Read the rehearsal as a beginner would and mark each step where you relied on something not written down. When the rehearsal is finished, `docker compose -p ds60-docker-study-rehearsal down -v` removes its container, network and volume. That reset is deliberate because the volume belongs to a scratch project; the main project and its volume are untouched.

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

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

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

Exercise 4 is this chapter's boundary case: Introduce and repair one wrong host port in a scratch model. Its expected observation is: Explain the first failing network hop and restore the original mapping. Change only the host side of one published port in a scratch copy, record the first failing request, then restore the mapping and confirm the original request succeeds again.

A capstone trap is evidence that cannot fail. If the counter reads 0 before a recreation and 0 after it, the record is consistent with persistence and equally consistent with a fresh empty volume, so it proves nothing. Make the test able to fail: increment to a distinctive value such as 3 before replacing the container, and write down the exact JSON. The same rule applies to the message check. Change the message to a phrase that could not appear by accident, such as one containing today's date, so a stale container returning the default text is caught instead of being read as success.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** Recall the container IDs before and after recreation and what their difference proves about replacement.

**Transfer case.** A beginner follows your handoff, runs `docker compose -p ds60-docker-study up -d` without `--wait`, immediately requests `http://127.0.0.1:18080/`, and reports `connection refused`. What do you check first, and what result would point to a real fault?

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

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
