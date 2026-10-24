# docker-008: Environment variables, command arguments and configuration

## Level and prerequisites

Beginner; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-007`

## Learning objectives

Design defaults and validation for a timeout variable. Write a public configuration evidence record. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

Configuration changes behavior without rebuilding application logic. Environment variables are string values supplied to a process. Command arguments are an ordered array of strings. Image defaults, Compose interpolation and the container’s environment are related but distinct mechanisms.

A Compose `.env` file commonly supplies values used when Compose renders its model. That does not mean every value is automatically injected into every container. A service’s `environment` or `env_file` configuration controls injection. Host-shell interpolation, Compose interpolation and shell expansion inside a container occur at different times.

Treat configuration as data with validation. A missing value should produce a clear startup error or documented default. A string containing `false` is still a nonempty string in many languages. Numeric ports and timeouts need parsing and bounds. Secrets should not be casually placed in versioned files or printed by a diagnostic command.

## Anatomy and a trace you can follow

The fixture reads `APP_MESSAGE` and serves it in a JSON field. Compose explicitly sets the value. A source-only message edit changes the image; an environment edit changes runtime configuration and usually requires container recreation to take effect. An image environment value is a default which runtime options can override.

The exec-form command array does not expand `$NAME` like a shell. If the application needs an environment value, have the application read it or use an intentionally reviewed shell wrapper. `docker compose config` is valuable for validation but can display interpolated private values; use synthetic data in this lesson.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

## Worked example / walkthrough

### Worked example 1: Set a public runtime message

This is a Compose fragment for the copied fixture.

```yaml
services:
  app:
    environment:
      APP_MESSAGE: "hello from my configuration"
```

**Expected observation:** The app reads this public string after recreation; the image source can remain unchanged.

### Worked example 2: Read one explicit variable

The short process reads its own environment.

```sh
docker run --rm --pull never -e APP_MESSAGE=sample ds60-docker-study:local python -c "import os; print(os.environ['APP_MESSAGE'])"
```

**Expected observation:** Exactly sample is printed; no secret value is involved.

## Six progressive exercises

### Exercise 1: Distinguish Compose interpolation from container environment.

**Expected evidence:** Model rendering versus process input.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Predict the type of APP_MESSAGE.

**Expected evidence:** A string, even when its contents look numeric.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Design defaults and validation for a timeout variable.

**Expected evidence:** A documented default plus finite positive bounded numeric parsing.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose an exec array containing literal $PORT.

**Expected evidence:** No shell expansion occurs in an argument array.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Explain why restart may not apply changed Compose environment.

**Expected evidence:** Existing container configuration and recreation differ.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Write a public configuration evidence record.

**Expected evidence:** Name, safe synthetic value, source of override and observed response.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose an exec array containing literal $PORT. Use its expected observation, No shell expansion occurs in an argument array., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/compose/how-tos/environment-variables/)
- [Official reference 2](https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-008: Environment variables, command arguments and configuration.
Read courses/docker/guides/docker-008.md and courses/docker/lessons/docker-008.md. Direct prerequisites: `docker-007`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
