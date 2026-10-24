# docker-026: Compose overrides, profiles and configuration review

## Level and prerequisites

Intermediate; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-025`

## Learning objectives

Create an override for a public message. Write a reviewable configuration launch record. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

An override file changes a base Compose application model. Profiles select optional services. Both mechanisms can make one project support development, teaching and operations tasks, but they also create more possible effective configurations to review.

The effective model matters more than any one input file. Merge rules differ for scalar values, mappings and sequences. An override can unexpectedly add ports or mounts rather than replace the intended list in the way a beginner assumes. Always inspect or validate the combined model before applying it.

Profiles are not a security boundary. A service omitted from the default startup is still available when explicitly selected or enabled. Use profiles for intentional optional tools and workloads, not for hiding privileged services in a file and assuming they cannot run.

## Anatomy and a trace you can follow

The fixture’s client has the tools profile. Ordinary `up` starts the app; an explicit tools invocation runs the peer check. For an override experiment, copy the fixture and change only a public message or unused loopback host port. Use `-f` in a fixed order and validate that same order.

Do not print a fully rendered production model containing secrets into a public log. This lesson uses synthetic public values. The goal is to explain which input supplied each final field and how a reviewer can reproduce the exact model.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

## Worked example / walkthrough

### Worked example 1: Enable the optional client intentionally

The fixture keeps this service out of ordinary startup.

```sh
docker compose -p ds60-docker-study --profile tools run --rm client
```

**Expected observation:** A short peer request is executed; the client container is removed after completion.

### Worked example 2: Review a combined model

Use two files in your own scratch copy.

```sh
docker compose -p ds60-docker-study -f compose.yaml -f compose.study.yaml config --quiet
```

**Expected observation:** The exact ordered combination validates without creating resources.

## Six progressive exercises

### Exercise 1: Distinguish profiles and overrides.

**Expected evidence:** Service selection versus model composition.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Predict ordinary startup with the tools profile disabled.

**Expected evidence:** The app starts and the optional client is not a persistent service.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Create an override for a public message.

**Expected evidence:** Only the intended environment value changes in the effective model.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose an unexpected extra port after merging.

**Expected evidence:** Inspect merge behavior and the complete effective ports list.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Explain why a profile is not access control.

**Expected evidence:** Someone with engine and project access can enable it.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Write a reviewable configuration launch record.

**Expected evidence:** Ordered files, profiles, project name and safe resolved settings.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose an unexpected extra port after merging. Use its expected observation, Inspect merge behavior and the complete effective ports list., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/compose/how-tos/multiple-compose-files/merge/)
- [Official reference 2](https://docs.docker.com/compose/how-tos/profiles/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-026: Compose overrides, profiles and configuration review.
Read courses/docker/guides/docker-026.md and courses/docker/lessons/docker-026.md. Direct prerequisites: `docker-025`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
