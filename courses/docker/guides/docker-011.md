# docker-011: Compose services, projects and a complete application

## Level and prerequisites

Beginner; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-010`

## Learning objectives

Write the project lifecycle command sequence. Design a two-copy experiment without interference. Use Compose service, Compose project and compose.yaml accurately when you explain what you observed.

## Purpose, vocabulary and mental model

Compose describes a related set of services, networks and volumes in one application model. A service describes how to create containers with a common role. A project groups their owned resources so commands can target the application rather than every container on the engine.

The YAML model is declarative input, but running Compose is still an operation against a particular engine. Two copies of the same file can create different projects. Conversely, reusing the same project name can act on existing resources from an earlier invocation. Explicit project identity makes a teaching lab safer and its cleanup understandable.

A service name is also a useful DNS name on its Compose network. The default network enables peers to find each other without fixed IPs. Named volumes remain separate storage resources. An application can therefore be recreated while preserving its data, provided the same intended volume remains mounted.

### Key terms

- **Compose service:** A named definition of how to create containers that share one role, such as `app` or `client`.
- **Compose project:** The group of containers, networks and volumes that Compose creates and owns for one application.
- **`compose.yaml`:** The declarative file that describes an application's services, networks and volumes.
- **Project name:** The explicit identity Compose uses to label and find a project's resources, which keeps commands and cleanup scoped.
- **Service name:** The key under `services` that also acts as a DNS name for peers on the project's network.

## Anatomy and a trace you can follow

Use `docker compose -p ds60-docker-study ...` from the copied fixture directory. The explicit `-p` sets the project name consistently for build, up, logs and down. The fixture has `app` and an optional tools-profile `client`; the client uses the same local image but runs a short request command instead of the server.

`config --quiet` validates and renders the model without printing its values or starting services. `up -d --wait` creates or updates services and waits according to readiness behavior. `down` removes the project’s containers and ordinary networks while retaining named volumes unless explicit volume deletion is requested.

## How to use this lesson

The classroom displays this guide and saves your worksheet, `courses/docker/lessons/docker-011.md`. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example. **How to use the lessons** in the [subject README](../README.md) collects these rules in one place.

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

For each exercise, name the object involved and the phase of its lifetime before changing anything, then vary only the condition the task names. Exercises that ask you to predict, explain, compare or diagnose keep their answers in the solutions file; the others show the evidence to look for.

### Exercise 1: Identify the project and service names.

**Hint:** Find the -p value and the keys under services in compose.yaml.

### Exercise 2: Predict what config --quiet changes.

**Hint:** Ask whether config creates containers, networks or volumes.

### Exercise 3: Write the project lifecycle command sequence.

**Expected evidence:** Validate, build, up with readiness, inspect, then down.

**Hint:** Order the commands from validating the model to removing the project's containers.

### Exercise 4: Diagnose an unexpected resource collision.

**Hint:** List the containers, networks and volumes that carry the project's label before changing anything.

### Exercise 5: Explain why down preserves user data by default.

**Hint:** Compare docker compose down with and without -v.

### Exercise 6: Design a two-copy experiment without interference.

**Expected evidence:** Distinct project names and distinct published host ports.

**Hint:** List every name and port the two copies would share.

## Common mistakes and diagnosis

Running Compose from another directory or without `-p`, so resources land in a different project. Adding `-v` to `docker compose down` as routine cleanup. Starting two copies that share a host port.

Exercise 4 is this chapter's boundary case: Diagnose an unexpected resource collision. List the existing projects, containers and published ports with their labels before renaming or removing anything that might belong to another copy. Preserve the original failure and the exact changed field before retrying. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations first. Name every resource the `ds60-docker-study` project creates and which of them `down` keeps. Then reconstruct worked example 2 (Start and inspect the project) with one different value, predict what changes, and name which of Compose service, Compose project, compose.yaml and project name the change touches.

When a host session ends, run `docker compose -p ds60-docker-study down` from your fixture copy. It removes the project's containers and network but keeps named volumes; deleting a volume is a separate, deliberate reset described in the fixture README.

## Primary references

- [Compose application model](https://docs.docker.com/compose/intro/compose-application-model/)
- [Compose project name](https://docs.docker.com/compose/how-tos/project-name/)

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
