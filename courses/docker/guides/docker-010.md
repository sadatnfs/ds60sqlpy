# docker-010: Logs, exit status and observation before repair

## Level and prerequisites

Beginner; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-009`

## Learning objectives

Write an incident observation packet. Design log content for a public teaching server. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

Standard output and standard error are streams a process uses to communicate. Docker’s logging system captures those streams according to its configured driver. Logs are useful observations but are not a database and do not automatically have infinite retention.

An exit status is a small integer returned when a process ends. Zero conventionally means success; a nonzero value reports failure according to the program. A running container has not yet produced its final exit status. Its process can still be unhealthy, waiting indefinitely or returning incorrect responses.

The most effective beginner troubleshooting habit is to preserve evidence before changing state. Record the exact image, container state, recent bounded logs and a minimal failing request. Restarting repeatedly can destroy the first useful symptom, and dumping an entire environment can expose credentials unrelated to the problem.

## Anatomy and a trace you can follow

`docker compose logs --tail 30 app` asks for a bounded recent stream for the project service. `docker compose ps -a` shows lifecycle state. `docker inspect` provides structured fields for a named container; use format selections when you need just exit status or OOMKilled. `docker events` observes lifecycle events but is not a substitute for application request tracing.

The fixture writes concise HTTP access observations to standard error and JSON response data to the HTTP client. Keep those destinations distinct. If you redirect output to a file during a host experiment, store it in your ignored learner copy rather than committing machine logs to the source repository.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

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

### Exercise 1: Predict the streams used by the two short programs.

**Expected evidence:** Success line on stdout, failure diagnostic on stderr.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Choose a bounded log command.

**Expected evidence:** Project-scoped service logs with an explicit tail limit.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Write an incident observation packet.

**Expected evidence:** Image identity, lifecycle state, recent logs and one failing request.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose a running container that returns errors.

**Expected evidence:** Investigate application behavior rather than declaring success from running.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Explain why a restart-only repair is weak evidence.

**Expected evidence:** It can hide the cause and may not preserve a useful failure record.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Design log content for a public teaching server.

**Expected evidence:** Useful request metadata without tokens, raw secrets or private payloads.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose a running container that returns errors. Use its expected observation, Investigate application behavior rather than declaring success from running., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/engine/logging/)
- [Official reference 2](https://docs.docker.com/reference/cli/docker/container/inspect/)

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
