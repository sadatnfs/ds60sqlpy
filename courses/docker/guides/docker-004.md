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

The classroom saves `courses/docker/lessons/docker-004.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** Start the fixture project, then time the stop in worked example 2: `time docker compose -p ds60-docker-study stop --timeout 10 app`. The fixture already does three things right. Its `CMD` is exec form, `init: true` places a small init as PID 1 that forwards signals, and `server.py` installs a SIGTERM handler that shuts the HTTP server down cleanly. So the stop should take well under ten seconds, and `docker compose -p ds60-docker-study ps -a` should report `Exited (0)` rather than 137. Run `docker compose -p ds60-docker-study exec app ps -o pid,args` before stopping if `ps` is available in your image; otherwise read `/proc/1/cmdline`. Write the PID 1 command, the stop duration and the exit code in the worksheet. Start the service again with `up -d --wait` when you are done.

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

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

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

Exercise 4 is this chapter's boundary case: Diagnose a service kept alive only by sleep. List the processes inside the container and identify which one is PID 1 before reading the running status as evidence about the server.

A subtler problem is a startup script that ends without `exec`. A `start.sh` that sets variables and then runs `python server.py` leaves the shell as the parent, so SIGTERM reaches the shell, which does not forward it, and Python never runs its handler. The engine waits for the timeout and then sends SIGKILL, which you see as a stop that always takes the full grace period and an exit code of 137. The fix is one word: end the script with `exec python server.py`, so Python replaces the shell and receives signals directly. An init process helps reap children but does not repair a script that swallows the signal.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** Describe what happens to the main process during `docker compose stop --timeout 10` when it ignores SIGTERM.

**Transfer case.** A worker container always takes exactly 30 seconds to stop and then shows exit code 137. Its Compose file sets `stop_grace_period: 30s` and its command is `sh -c "python worker.py"`. What is happening, and what would you change first?

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

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
