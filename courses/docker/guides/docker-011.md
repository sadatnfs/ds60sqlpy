# docker-011: Compose services, projects and a complete application

## Level and prerequisites

Beginner; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-010`

## Learning objectives

Write the project lifecycle command sequence. Design a two-copy experiment without interference. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

Compose describes a related set of services, networks and volumes in one application model. A service describes how to create containers with a common role. A project groups their owned resources so commands can target the application rather than every container on the engine.

The YAML model is declarative input, but running Compose is still an operation against a particular engine. Two copies of the same file can create different projects. Conversely, reusing the same project name can act on existing resources from an earlier invocation. Explicit project identity makes a teaching lab safer and its cleanup understandable.

A service name is also a useful DNS name on its Compose network. The default network enables peers to find each other without fixed IPs. Named volumes remain separate storage resources. An application can therefore be recreated while preserving its data, provided the same intended volume remains mounted.

## Anatomy and a trace you can follow

Use `docker compose -p ds60-docker-study ...` from the copied fixture directory. The explicit `-p` sets the project name consistently for build, up, logs and down. The fixture has `app` and an optional tools-profile `client`; the client uses the same local image but runs a short request command instead of the server.

`config --quiet` validates and renders the model without printing its values or starting services. `up -d --wait` creates or updates services and waits according to readiness behavior. `down` removes the project’s containers and ordinary networks while retaining named volumes unless explicit volume deletion is requested.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

## Worked example / walkthrough

### Worked example 1: Validate before creating

This checks the copied Compose file only.

```sh
docker compose -p ds60-docker-study config --quiet
```

**Expected observation:** Exit zero for a valid model; no containers are created by this command.

### Worked example 2: Start and inspect the project

The first build downloads its base if necessary; no image is pushed.

```sh
docker compose --progress plain -p ds60-docker-study build
docker compose -p ds60-docker-study up -d --wait
docker compose -p ds60-docker-study ps
```

**Expected observation:** The app becomes healthy and its host loopback endpoint is available.

## Six progressive exercises

### Exercise 1: Identify the project and service names.

**Expected evidence:** Project ds60-docker-study and service app.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Predict what config --quiet changes.

**Expected evidence:** It validates the model without creating runtime resources.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Write the project lifecycle command sequence.

**Expected evidence:** Validate, build, up with readiness, inspect, then down.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose an unexpected resource collision.

**Expected evidence:** Inspect project identity and existing owned resources before changes.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Explain why down preserves user data by default.

**Expected evidence:** Named volume removal is a separate explicit operation.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Design a two-copy experiment without interference.

**Expected evidence:** Distinct project names and distinct published host ports.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose an unexpected resource collision. Use its expected observation, Inspect project identity and existing owned resources before changes., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/compose/intro/compose-application-model/)
- [Official reference 2](https://docs.docker.com/compose/how-tos/project-name/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-011: Compose services, projects and a complete application.
Read courses/docker/guides/docker-011.md and courses/docker/lessons/docker-011.md. Direct prerequisites: `docker-010`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
