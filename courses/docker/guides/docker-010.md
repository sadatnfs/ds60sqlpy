# docker-010: Logs, exit status and observation before repair

## Level and prerequisites

Beginner; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-009`

## Learning objectives

Write an incident observation packet. Design log content for a public teaching server. Use standard streams, container logs and exit status accurately when you explain what you observed.

## Purpose, vocabulary and mental model

Standard output and standard error are streams a process uses to communicate. Docker’s logging system captures those streams according to its configured driver. Logs are useful observations but are not a database and do not automatically have infinite retention.

An exit status is a small integer returned when a process ends. Zero conventionally means success; a nonzero value reports failure according to the program. A running container has not yet produced its final exit status. Its process can still be unhealthy, waiting indefinitely or returning incorrect responses.

The most effective beginner troubleshooting habit is to preserve evidence before changing state. Record the exact image, container state, recent bounded logs and a minimal failing request. Restarting repeatedly can destroy the first useful symptom, and dumping an entire environment can expose credentials unrelated to the problem.

### Key terms

- **Standard streams:** The standard output and standard error channels a process writes to, which Docker's logging driver captures.
- **Container logs:** The captured stream output for one container, which has bounded retention and is not a database.
- **Exit status:** The small integer a process returns when it ends, where zero conventionally means success.
- **Container state:** The engine's record of whether a container is created, running, restarting or exited, plus its exit code.
- **Events:** The engine's time-ordered stream of lifecycle notices such as create, start, die and stop.

## Anatomy and a trace you can follow

`docker compose logs --tail 30 app` asks for a bounded recent stream for the project service. `docker compose ps -a` shows lifecycle state. `docker inspect` provides structured fields for a named container; use format selections when you need just exit status or OOMKilled. `docker events` observes lifecycle events but is not a substitute for application request tracing.

The fixture writes concise HTTP access observations to standard error and JSON response data to the HTTP client. Keep those destinations distinct. If you redirect output to a file during a host experiment, store it in your ignored learner copy rather than committing machine logs to the source repository.

## How to use this lesson

The classroom saves `courses/docker/lessons/docker-010.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** Run worked example 2, then repeat each program without `--rm` and with names such as `ds60-ok` and `ds60-fail`. `docker ps -a --filter name=ds60-` shows `Exited (0)` and `Exited (1)`, and `docker logs ds60-fail` replays the traceback, because logs belong to the container, not the process. Separate the streams on the host with `docker logs ds60-fail 2>/dev/null`, which prints nothing because the traceback went to stderr. Next, start the project, request an unknown route such as `/missing`, and read `docker compose -p ds60-docker-study logs --tail 5 app`: the 404 appears as a request line while the container stays Up. Save each exit code and log line in the worksheet, then remove the two named containers with `docker rm ds60-ok ds60-fail`.

## Worked example / walkthrough

### Worked example 1: Read a bounded log sample

Use the copied fixture project and service name.

```sh
docker compose -p ds60-docker-study ps -a
docker compose -p ds60-docker-study logs --tail 30 app
```

**Expected observation:** A small project-specific state and log record, without touching unrelated containers.

### Worked example 2: Compare successful and failing short programs

Both process results are useful evidence.

```sh
docker run --rm --pull never ds60-docker-study:local python -c "print('ok')"
docker run --rm --pull never ds60-docker-study:local python -c "raise ValueError('teaching failure')"
```

**Expected observation:** The first exits zero; the second prints a traceback to stderr and exits nonzero.

## Six progressive exercises

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

### Exercise 1: Predict the streams used by the two short programs.

**Hint:** Ask which stream a print call uses and which a failure diagnostic uses.

### Exercise 2: Choose a bounded log command.

**Hint:** Limit the output by project, service and number of lines.

### Exercise 3: Write an incident observation packet.

**Expected evidence:** Image identity, lifecycle state, recent logs and one failing request.

**Hint:** Collect the image identity, the state, recent logs and one failing request before changing anything.

### Exercise 4: Diagnose a running container that returns errors.

**Hint:** Compare the container state with the HTTP status of a request.

### Exercise 5: Explain why a restart-only repair is weak evidence.

**Hint:** Ask what you learn about the cause if the error disappears after a restart.

### Exercise 6: Design log content for a public teaching server.

**Expected evidence:** Useful request metadata without tokens, raw secrets or private payloads.

**Hint:** List the fields that help diagnose a request and the values that must never be logged.

## Common mistakes and diagnosis

Restarting a failing container before saving its logs and exit status. Reading the whole log history instead of a bounded tail. Logging tokens or request bodies to make debugging easier.

Exercise 4 is this chapter's boundary case: Diagnose a running container that returns errors. Send one request to the application and read its status code and log line; a container STATUS of Up only reports that the main process exists.

A further trap is reading `docker logs` on a service that writes to a log file instead of the standard streams. The command then shows only startup lines, and the learner concludes that no requests arrived. The engine's logging driver captures only stdout and stderr of the main process, so a file such as `/var/log/app.log` is invisible to it and also disappears with the writable layer. Configure the application to log to stdout or stderr, as the fixture's HTTP server does, and keep any log file you truly need on a volume with its own retention plan.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** Recall which exit code each program produced and which log line identified the failure.

**Transfer case.** After a deployment, `docker compose ps` shows the app as `Up 3 minutes`, but users report errors. A teammate proposes `docker compose restart app` immediately. What should be captured first, and why is the restart weak evidence of a fix?

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

## Primary references

- [Docker logging](https://docs.docker.com/engine/logging/)
- [docker container inspect reference](https://docs.docker.com/reference/cli/docker/container/inspect/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-010: Logs, exit status and observation before repair.
Read courses/docker/guides/docker-010.md and courses/docker/lessons/docker-010.md. Direct prerequisites: `docker-009`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
