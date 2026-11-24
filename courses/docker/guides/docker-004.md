# docker-004: Processes, PID 1, signals and graceful shutdown

## Level and prerequisites

Beginner; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-003`

## Learning objectives

Write a four-step graceful shutdown sequence. Design a shutdown acceptance check for a writer. Use PID 1, signals and graceful shutdown accurately when you explain what you observed.

## Purpose, vocabulary and mental model

PID is a process identifier within a process namespace. The container’s initial process has PID 1 in that namespace and participates in special Linux signal and child-reaping behavior. Docker normally considers a container alive while its main process remains alive. Starting a server in the background and allowing the main shell to exit therefore does not create a durable service.

A signal is a notification delivered to a process. A graceful termination handler stops accepting new work, lets bounded in-flight work finish, closes resources and exits. An abrupt kill cannot perform application cleanup. Docker stop ordinarily sends the configured stop signal, waits for a grace period and then forces termination if necessary.

The exec form of a Dockerfile command gives the runtime an argument array directly. The shell form starts a shell, whose signal forwarding and child handling can become relevant. An init process can reap adopted children and forward signals, but it does not add application-specific transaction recovery. Good shutdown is a cooperation between the orchestrator, process tree and application.

### Key terms

- **PID 1:** The process ID of a container's initial process, which has special Linux signal and child-reaping behavior.
- **Signal:** A notification delivered to a process, such as SIGTERM asking it to stop or SIGKILL ending it without cleanup.
- **Graceful shutdown:** Refusing new work, finishing bounded in-flight work, closing resources and exiting before the grace period ends.
- **Exec form:** The JSON array form of `CMD` or `ENTRYPOINT`, which gives the runtime the arguments directly without starting a shell.
- **Init process:** A small PID 1 program that reaps adopted child processes and forwards signals to the application.

## Anatomy and a trace you can follow

Compare `CMD ["python", "server.py"]` with `CMD python server.py`. The JSON array has no shell interpolation; each string is one argument. Compose `init: true` requests a small init where supported. The fixture uses it, sets a stop grace period, and logs to standard streams. Do not add an infinite sleep to hide that the real application exited.

For a shutdown investigation record the main process, signal, elapsed time, exit status and whether data is consistent. Exit 137 often indicates a SIGKILL-style termination, but by itself does not prove an out-of-memory cause. Inspect the engine’s OOMKilled state and events before concluding why a process was killed.

## How to use this lesson

The classroom displays this guide and saves your worksheet, `courses/docker/lessons/docker-004.md`. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example. **How to use the lessons** in the [subject README](../README.md) collects these rules in one place.

## Worked example / walkthrough

### Worked example 1: Read an explicit startup command

This is a Dockerfile fragment, not a command to type into Bash.

```dockerfile
WORKDIR /app
CMD ["python", "server.py"]
```

**Expected observation:** Python is the direct image command; the process stays in the foreground.

### Worked example 2: Observe a bounded stop

Run only after the disposable fixture project is up.

```sh
docker compose -p ds60-docker-study logs --tail 20 app
docker compose -p ds60-docker-study stop --timeout 10 app
docker compose -p ds60-docker-study ps -a
```

**Expected observation:** The owned app stops; logs and exit state provide evidence about its actual termination.

## Six progressive exercises

For each exercise, name the object involved and the phase of its lifetime before changing anything, then vary only the condition the task names. Exercises that ask you to predict, explain, compare or diagnose keep their answers in the solutions file; the others show the evidence to look for.

### Exercise 1: Predict what happens when the main process exits.

**Hint:** Ask what Docker watches to decide whether a container is running.

### Exercise 2: Compare exec-form and shell-form startup.

**Hint:** Write the process tree for each form and find PID 1.

### Exercise 3: Write a four-step graceful shutdown sequence.

**Expected evidence:** Stop new work, bound draining, close owned resources, exit.

**Hint:** Start from the moment the stop signal arrives and end with the exit status.

### Exercise 4: Diagnose a service kept alive only by sleep.

**Hint:** Check which process is PID 1 and what the server process is doing.

### Exercise 5: Explain why exit 137 is not a complete OOM diagnosis.

**Hint:** Compute 137 minus 128 and list what can send that signal.

### Exercise 6: Design a shutdown acceptance check for a writer.

**Expected evidence:** Bounded stop, consistent persisted record and restart recovery.

**Hint:** Stop the service in the middle of a write, then check the stored record and a restart.

## Common mistakes and diagnosis

Starting the server in the background and keeping the container alive with `sleep`. Using shell form, so a shell becomes PID 1 and may not forward SIGTERM. Reading exit code 137 as proof of an out-of-memory kill without checking the OOMKilled state.

Exercise 4 is this chapter's boundary case: Diagnose a service kept alive only by sleep. List the processes inside the container and identify which one is PID 1 before reading the running status as evidence about the server. Preserve the original failure and the exact changed field before retrying. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations first. Describe what happens to the main process during `docker compose stop --timeout 10` when it ignores SIGTERM. Then reconstruct worked example 2 (Observe a bounded stop) with one different value, predict what changes, and name which of PID 1, signals, graceful shutdown, exec form and init process the change touches.

When a host session ends, run `docker compose -p ds60-docker-study down` from your fixture copy. It removes the project's containers and network but keeps named volumes; deleting a volume is a separate, deliberate reset described in the fixture README.

## Primary references

- [Dockerfile reference: ENTRYPOINT](https://docs.docker.com/reference/dockerfile/#entrypoint)
- [docker container stop reference](https://docs.docker.com/reference/cli/docker/container/stop/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-004: Processes, PID 1, signals and graceful shutdown.
Read courses/docker/guides/docker-004.md and courses/docker/lessons/docker-004.md. Direct prerequisites: `docker-003`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
