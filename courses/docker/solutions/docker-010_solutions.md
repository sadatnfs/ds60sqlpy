# docker-010: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-010.md`.

## Exercise 1: Predict the streams used by the two short programs.

**Expected answer:** Success line on stdout, failure diagnostic on stderr.

**Why:** Stream conventions help tools separate normal output from diagnostics. They do not prevent an application from misusing a stream, so inspect its documented behavior.

**Approach:** Match each program to its stream: print('ok') writes to stdout, and an uncaught ValueError makes python write a traceback to stderr.

**Why this is correct:** Python prints uncaught exceptions on stderr and exits with status 1. Docker keeps both streams, so you can split them on the host.

**A plausible wrong approach:** Assuming all container output is one undivided log fails when a script captures only stdout, which loses the traceback.

**How to verify:** Rerun worked example 2 with 2>/dev/null: ok still appears, the traceback disappears, and echo $? prints a nonzero status.

## Exercise 2: Choose a bounded log command.

**Expected answer:** Project-scoped service logs with an explicit tail limit.

**Why:** A bounded sample is easier to review and less likely to leak unrelated data. Scope should be enforced by project and service selection rather than by filtering a huge global dump afterward.

**Approach:** Name the project, the service and a line limit: docker compose -p ds60-docker-study logs --tail 30 app.

**Why this is correct:** The project and service filters keep the sample to the fixture's own container, and --tail caps the volume before anything is copied into notes.

**A plausible wrong approach:** Running docker logs on every container and grepping afterward shows output from unrelated workloads and may expose their data.

**How to verify:** The output prefix names only the app service, and the line count is at most 30.

## Exercise 3: Write an incident observation packet.

**Expected evidence:** Image identity, lifecycle state, recent logs and one failing request.

**Why:** These observations connect source packaging to the process and application layers. Include timestamps so a later healthy state is not confused with the original failure.

**Approach:** Collect four items with timestamps: the image ID behind ds60-docker-study:local, docker compose ps -a state, a bounded log sample and one failing request with its status.

**Why this is correct:** Each item answers a different question: what was packaged, whether it ran, what it reported and how it behaved, all fixed to the time of failure.

**A plausible wrong approach:** Collecting only a screenshot of the browser error leaves no way to tell whether a stale image, stopped container or app bug caused it.

**How to verify:** A second reader can rebuild the timeline from the packet alone and name the layer where the failure first appears.

## Exercise 4: Diagnose a running container that returns errors.

**Expected answer:** Investigate application behavior rather than declaring success from running.

**Why:** The engine reports process lifecycle. HTTP responses and domain assertions establish whether that process performs its intended function.

**Approach:** Accept that the engine reports a running process and move on to the application: send requests and read the status codes and bodies.

**Why this is correct:** Container state only tracks the main process. If counter.json fails validation in read_counter, the fixture stays running while GET /counter raises inside the handler and the client gets no valid response.

**A plausible wrong approach:** Restarting until the status says Up treats process lifecycle as correctness and can repeat the same failing request forever.

**How to verify:** GET /counter failing while ps shows the container running, plus a ValueError traceback in the app logs, confirms an application-layer fault.

## Exercise 5: Explain why a restart-only repair is weak evidence.

**Expected answer:** It can hide the cause and may not preserve a useful failure record.

**Why:** A restart can be an operational mitigation while still leaving root cause unknown. State both facts instead of claiming that disappearance proves a permanent fix.

**Approach:** Separate mitigation from diagnosis: a restart may restore service, but it also replaces the evidence that explained the failure.

**Why this is correct:** After restart, the old process's memory state is gone. Only logs and exit records captured beforehand can still point to a cause.

**A plausible wrong approach:** Writing fixed by restart in an incident note claims a root cause that nobody observed, so the same fault returns unexplained.

**How to verify:** Check that the incident note records the pre-restart logs and states plainly that the cause is unknown if it has not been reproduced.

## Exercise 6: Design log content for a public teaching server.

**Expected evidence:** Useful request metadata without tokens, raw secrets or private payloads.

**Why:** Logs often persist beyond the request. A small diagnostic schema gives enough context to debug while limiting the information copied into reports or shared screenshots.

**Approach:** Log the method, path, status and duration for each request, and leave out headers, query strings and bodies that may carry tokens or personal data.

**Why this is correct:** Logs are copied into terminals, reports and screenshots. A fixed small schema keeps debugging value while keeping secrets out of those copies.

**A plausible wrong approach:** Logging full request headers for convenience copies Authorization values into every place the log travels.

**How to verify:** Send a request with a dummy Authorization header and confirm the log line shows method, path and status but not the header value.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
