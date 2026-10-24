# docker-010: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

Standard output and standard error are streams a process uses to communicate. Docker’s logging system captures those streams according to its configured driver. Logs are useful observations but are not a database and do not automatically have infinite retention.

An exit status is a small integer returned when a process ends. Zero conventionally means success; a nonzero value reports failure according to the program. A running container has not yet produced its final exit status. Its process can still be unhealthy, waiting indefinitely or returning incorrect responses.

The most effective beginner troubleshooting habit is to preserve evidence before changing state. Record the exact image, container state, recent bounded logs and a minimal failing request. Restarting repeatedly can destroy the first useful symptom, and dumping an entire environment can expose credentials unrelated to the problem.

`docker compose logs --tail 30 app` asks for a bounded recent stream for the project service. `docker compose ps -a` shows lifecycle state. `docker inspect` provides structured fields for a named container; use format selections when you need just exit status or OOMKilled. `docker events` observes lifecycle events but is not a substitute for application request tracing.

The fixture writes concise HTTP access observations to standard error and JSON response data to the HTTP client. Keep those destinations distinct. If you redirect output to a file during a host experiment, store it in your ignored learner copy rather than committing machine logs to the source repository.

## Exercise 1: Predict the streams used by the two short programs.

Stream conventions help tools separate normal output from diagnostics. They do not prevent an application from misusing a stream, so inspect its documented behavior.

**Expected:** Success line on stdout, failure diagnostic on stderr.

## Exercise 2: Choose a bounded log command.

A bounded sample is easier to review and less likely to leak unrelated data. Scope should be enforced by project and service selection rather than by filtering a huge global dump afterward.

**Expected:** Project-scoped service logs with an explicit tail limit.

## Exercise 3: Write an incident observation packet.

These observations connect source packaging to the process and application layers. Include timestamps so a later healthy state is not confused with the original failure.

**Expected:** Image identity, lifecycle state, recent logs and one failing request.

## Exercise 4: Diagnose a running container that returns errors.

The engine reports process lifecycle. HTTP responses and domain assertions establish whether that process performs its intended function.

**Expected:** Investigate application behavior rather than declaring success from running.

## Exercise 5: Explain why a restart-only repair is weak evidence.

A restart can be an operational mitigation while still leaving root cause unknown. State both facts instead of claiming that disappearance proves a permanent fix.

**Expected:** It can hide the cause and may not preserve a useful failure record.

## Exercise 6: Design log content for a public teaching server.

Logs often persist beyond the request. A small diagnostic schema gives enough context to debug while limiting the information copied into reports or shared screenshots.

**Expected:** Useful request metadata without tokens, raw secrets or private payloads.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
