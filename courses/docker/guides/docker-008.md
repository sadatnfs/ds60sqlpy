# docker-008: Environment variables, command arguments and configuration

## Level and prerequisites

Beginner; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-007`

## Learning objectives

Design defaults and validation for a timeout variable. Write a public configuration evidence record. Use environment variables, ENTRYPOINT and CMD accurately when you explain what you observed.

## Purpose, vocabulary and mental model

Configuration changes behavior without rebuilding application logic. Environment variables are string values supplied to a process. Command arguments are an ordered array of strings. Image defaults, Compose interpolation and the container’s environment are related but distinct mechanisms.

A Compose `.env` file commonly supplies values used when Compose renders its model. That does not mean every value is automatically injected into every container. A service’s `environment` or `env_file` configuration controls injection. Host-shell interpolation, Compose interpolation and shell expansion inside a container occur at different times.

Treat configuration as data with validation. A missing value should produce a clear startup error or documented default. A string containing `false` is still a nonempty string in many languages. Numeric ports and timeouts need parsing and bounds. Secrets should not be casually placed in versioned files or printed by a diagnostic command.

### Key terms

- **Environment variable:** A named string value supplied to a process, which the application must parse and validate itself.
- **`ENTRYPOINT`:** The Dockerfile instruction that sets the executable a container runs, with `CMD` supplying its default arguments.
- **Compose interpolation:** Substitution of variable references, often from a `.env` file, while Compose renders its model before containers start.
- **`env_file`:** A service setting that injects the variables from a named file into that service's container environment.
- **Configuration validation:** Parsing and bounds checking settings at startup, so a missing or malformed value fails with a clear error.

## Anatomy and a trace you can follow

The fixture reads `APP_MESSAGE` and serves it in a JSON field. Compose explicitly sets the value. A source-only message edit changes the image; an environment edit changes runtime configuration and usually requires container recreation to take effect. An image environment value is a default which runtime options can override.

An image's `ENTRYPOINT` names the executable and its `CMD` supplies default arguments, or the whole default command when there is no entrypoint. Arguments after the image name in `docker run IMAGE ARG...` replace `CMD` and are appended to the entrypoint; `--entrypoint` replaces the executable and also clears the image's default `CMD`. The fixture's Dockerfile sets only `CMD ["python", "server.py"]`, so `docker run IMAGE python -c ...` replaces the whole command, while its Compose `client` service sets `entrypoint: ["python", "-c"]` and passes the program text as `command`.

The exec-form command array does not expand `$NAME` like a shell. If the application needs an environment value, have the application read it or use an intentionally reviewed shell wrapper. `docker compose config` is valuable for validation but can display interpolated private values; use synthetic data in this lesson.

## How to use this lesson

The classroom displays this guide and saves your worksheet, `courses/docker/lessons/docker-008.md`. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example. **How to use the lessons** in the [subject README](../README.md) collects these rules in one place.

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

For each exercise, name the object involved and the phase of its lifetime before changing anything, then vary only the condition the task names. Exercises that ask you to predict, explain, compare or diagnose keep their answers in the solutions file; the others show the evidence to look for.

### Exercise 1: Distinguish Compose interpolation from container environment.

**Hint:** Run docker compose config and compare it with the environment inside the container.

### Exercise 2: Predict the type of APP_MESSAGE.

**Hint:** Ask what type every value in a process environment has.

### Exercise 3: Design defaults and validation for a timeout variable.

**Expected evidence:** A documented default plus finite positive bounded numeric parsing.

**Hint:** Decide what happens for a missing, a negative, a huge and a non-numeric value.

### Exercise 4: Diagnose an exec array containing literal $PORT.

**Hint:** Ask which program would expand $PORT and whether one runs in exec form.

### Exercise 5: Explain why restart may not apply changed Compose environment.

**Hint:** Compare what docker compose restart and docker compose up do to the container.

### Exercise 6: Write a public configuration evidence record.

**Expected evidence:** Name, safe synthetic value, source of override and observed response.

**Hint:** Record where the value came from and the response that shows it.

## Common mistakes and diagnosis

Expecting every `.env` value to appear inside the container. Restarting a container after changing its environment instead of recreating it. Overriding `--entrypoint` and expecting the image's `CMD` to still apply.

Exercise 4 is this chapter's boundary case: Diagnose an exec array containing literal $PORT. Print the argument vector the program actually received, and compare the exec array with the shell form, before adding a shell wrapper to the command. Preserve the original failure and the exact changed field before retrying. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations first. Explain from memory why `restart` keeps the old environment while recreating the service applies the new value. Then reconstruct worked example 2 (Read one explicit variable) with one different value, predict what changes, and name which of environment variables, ENTRYPOINT, CMD, Compose interpolation and configuration validation the change touches.

When a host session ends, run `docker compose -p ds60-docker-study down` from your fixture copy. It removes the project's containers and network but keeps named volumes; deleting a volume is a separate, deliberate reset described in the fixture README.

## Primary references

- [Environment variables in Compose](https://docs.docker.com/compose/how-tos/environment-variables/)
- [Compose variable interpolation](https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/)
- [Dockerfile reference: ENTRYPOINT](https://docs.docker.com/reference/dockerfile/#entrypoint)

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
