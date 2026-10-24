# docker-004: Processes, PID 1, signals and graceful shutdown

## Level and prerequisites

Beginner; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-003`

## Learning objectives

Write a four-step graceful shutdown sequence. Design a shutdown acceptance check for a writer. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

PID is a process identifier within a process namespace. The container’s initial process has PID 1 in that namespace and participates in special Linux signal and child-reaping behavior. Docker normally considers a container alive while its main process remains alive. Starting a server in the background and allowing the main shell to exit therefore does not create a durable service.

A signal is a notification delivered to a process. A graceful termination handler stops accepting new work, lets bounded in-flight work finish, closes resources and exits. An abrupt kill cannot perform application cleanup. Docker stop ordinarily sends the configured stop signal, waits for a grace period and then forces termination if necessary.

The exec form of a Dockerfile command gives the runtime an argument array directly. The shell form starts a shell, whose signal forwarding and child handling can become relevant. An init process can reap adopted children and forward signals, but it does not add application-specific transaction recovery. Good shutdown is a cooperation between the orchestrator, process tree and application.

## Anatomy and a trace you can follow

Compare `CMD ["python", "server.py"]` with `CMD python server.py`. The JSON array has no shell interpolation; each string is one argument. Compose `init: true` requests a small init where supported. The fixture uses it, sets a stop grace period, and logs to standard streams. Do not add an infinite sleep to hide that the real application exited.

For a shutdown investigation record the main process, signal, elapsed time, exit status and whether data is consistent. Exit 137 often indicates a SIGKILL-style termination, but by itself does not prove an out-of-memory cause. Inspect the engine’s OOMKilled state and events before concluding why a process was killed.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

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

### Exercise 1: Predict what happens when the main process exits.

**Expected evidence:** The container enters an exited state.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Compare exec-form and shell-form startup.

**Expected evidence:** An argument array versus an intervening shell.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Write a four-step graceful shutdown sequence.

**Expected evidence:** Stop new work, bound draining, close owned resources, exit.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose a service kept alive only by sleep.

**Expected evidence:** The alive container does not prove the application is healthy.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Explain why exit 137 is not a complete OOM diagnosis.

**Expected evidence:** It identifies a termination pattern, not its unique cause.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Design a shutdown acceptance check for a writer.

**Expected evidence:** Bounded stop, consistent persisted record and restart recovery.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose a service kept alive only by sleep. Use its expected observation, The alive container does not prove the application is healthy., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/reference/dockerfile/#entrypoint)
- [Official reference 2](https://docs.docker.com/reference/cli/docker/container/stop/)

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
