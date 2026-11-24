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

The classroom displays this guide and saves your worksheet, `courses/docker/lessons/docker-010.md`. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example. **How to use the lessons** in the [subject README](../README.md) collects these rules in one place.

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

For each exercise, name the object involved and the phase of its lifetime before changing anything, then vary only the condition the task names. Exercises that ask you to predict, explain, compare or diagnose keep their answers in the solutions file; the others show the evidence to look for.

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

Exercise 4 is this chapter's boundary case: Diagnose a running container that returns errors. Send one request to the application and read its status code and log line; a container STATUS of Up only reports that the main process exists. Preserve the original failure and the exact changed field before retrying. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations first. Recall which exit code each program produced and which log line identified the failure. Then reconstruct worked example 2 (Compare successful and failing short programs) with one different value, predict what changes, and name which of standard streams, container logs, exit status, container state and events the change touches.

When a host session ends, run `docker compose -p ds60-docker-study down` from your fixture copy. It removes the project's containers and network but keeps named volumes; deleting a volume is a separate, deliberate reset described in the fixture README.

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
