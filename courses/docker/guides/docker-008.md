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

The classroom saves `courses/docker/lessons/docker-008.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** Start the fixture project and request the root URL to read the default message. Then create `compose.override.yaml` in your copy with worked example 1 and run `docker compose -p ds60-docker-study config` to see the merged value before anything starts. Run `docker compose -p ds60-docker-study restart app` and request the root URL again: the old message remains, because restart reuses the existing container configuration. Now run `up -d --wait` and request it once more; the new message appears and `ps -q app` shows a new container ID. Finally, change worked example 2 to pass `-e APP_MESSAGE=42` and print `type(os.environ['APP_MESSAGE'])`: the result is `<class 'str'>`, because every environment value arrives as text. Delete the override file afterwards so later lessons start from the fixture defaults.

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

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

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

Exercise 4 is this chapter's boundary case: Diagnose an exec array containing literal $PORT. Print the argument vector the program actually received, and compare the exec array with the shell form, before adding a shell wrapper to the command.

Compose interpolation catches people in a second way: a literal dollar sign in a value is treated as a variable reference while the file is rendered. A message such as `cost $AMOUNT` becomes `cost ` followed by nothing, with a warning that the `AMOUNT` variable is not set, before the container ever sees it. Escape it as `$$AMOUNT`, which Compose renders as a single dollar sign, and confirm with `docker compose config`, which prints the rendered value. That same command is the quickest way to see whether a value came from the shell, an `.env` file or the YAML itself.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** Explain from memory why `restart` keeps the old environment while recreating the service applies the new value.

**Transfer case.** An image has `ENTRYPOINT ["python", "server.py"]` and `CMD ["--port", "8080"]`. A learner runs `docker run IMAGE --port 9090` and later `docker run --entrypoint python IMAGE -V`. What command line does each container start?

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

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
