# docker-004: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-004.md`.

## Exercise 1: Predict what happens when the main process exits.

**Expected answer:** The container enters an exited state.

**Why:** A container is not a VM with an independent background boot lifecycle. Its main process lifecycle drives the container state even if a script attempted to background work.

**Approach:** Identify the main process from CMD ["python", "server.py"] and follow what happens when serve_forever returns and main() finishes.

**Why this is correct:** The container's lifetime is tied to its main process. When that python process exits, the engine marks the container exited and records the exit code.

**A plausible wrong approach:** Expecting a background thread to keep the container up fails, because threads belong to the main process and end with it.

**How to verify:** Stop the app with docker compose stop and read docker compose ps -a; the app row shows an exited state with the code the process returned.

## Exercise 2: Compare exec-form and shell-form startup.

**Expected answer:** An argument array versus an intervening shell.

**Why:** The difference affects expansion and process hierarchy. It is not a claim that every shell command is wrong, but shell wrappers must intentionally forward signals and wait for children.

**Approach:** Write both forms side by side: CMD ["python", "server.py"] versus CMD python server.py, and note which program becomes PID 1 or the direct child of init.

**Why this is correct:** The exec form runs python directly, so SIGTERM reaches the handler registered in server.py. The shell form starts /bin/sh -c, which may not forward the signal.

**A plausible wrong approach:** Declaring the shell form always broken is wrong; a shell that uses exec python server.py hands control to python and keeps signals working.

**How to verify:** docker compose exec app ps is unavailable in slim images, so inspect the configured command with docker image inspect and confirm Cmd is a two-item array.

## Exercise 3: Write a four-step graceful shutdown sequence.

**Expected evidence:** Stop new work, bound draining, close owned resources, exit.

**Why:** An unbounded drain can prevent shutdown forever. Resource cleanup should be explicit, and data correctness may need a transaction or recovery protocol beyond closing file handles.

**Approach:** Map each step to server.py: the SIGTERM handler calls server.shutdown, serve_forever stops accepting, the finally block runs server_close, and main returns.

**Why this is correct:** stop_grace_period: 10s bounds the drain, and the atomic counter.next to counter.json replace means no reader ever sees a half-written record during shutdown.

**A plausible wrong approach:** Closing the socket in the signal handler itself can raise errors in the serving thread, which is why the fixture starts shutdown on a separate daemon thread.

**How to verify:** Time docker compose -p ds60-docker-study stop app; it returns well before 10 seconds, and the logs show no traceback on exit.

## Exercise 4: Diagnose a service kept alive only by sleep.

**Expected answer:** The alive container does not prove the application is healthy.

**Why:** The sleep process can make a status look running while the real server has crashed. Measure the application’s endpoint and actual process rather than adding a liveness placeholder.

**Approach:** Ask what PID 1 actually is: if a command such as sleep infinity runs while the server starts in the background, the container tracks sleep, not the server.

**Why this is correct:** Container status reflects only the main process. A crashed background server leaves sleep running, so the status looks healthy while requests fail.

**A plausible wrong approach:** Adding a second sleep or longer timeout to hide the crash makes the false signal stronger and delays the moment anyone notices the outage.

**How to verify:** Use the healthcheck instead: the fixture's /healthz probe turns unhealthy when the server stops answering, regardless of which process holds PID 1.

## Exercise 5: Explain why exit 137 is not a complete OOM diagnosis.

**Expected answer:** It identifies a termination pattern, not its unique cause.

**Why:** A user or timeout can also send a kill signal. Correlate termination state with OOMKilled and relevant events before recommending memory changes.

**Approach:** Read 137 as 128 plus signal 9, SIGKILL, and then list who could have sent it: the kernel OOM killer, the engine after a stop timeout, or a user.

**Why this is correct:** The code records how the process ended, not why. docker inspect reports State.OOMKilled separately, and engine events show whether a stop or kill was issued.

**A plausible wrong approach:** Doubling mem_limit from 128m on every 137 can hide a stop timeout bug, because a process that ignores SIGTERM is killed after the grace period with the same code.

**How to verify:** Check docker inspect for State.OOMKilled and the event stream around the exit time; true OOM shows OOMKilled true, a timeout kill shows false.

## Exercise 6: Design a shutdown acceptance check for a writer.

**Expected evidence:** Bounded stop, consistent persisted record and restart recovery.

**Why:** The important observation is what readers see after recovery. A clean exit code is useful but cannot by itself prove that a partially written application record is valid.

**Approach:** Write three checks in order: stop within the grace period, inspect the record on disk, then start again and read it through the API.

**Why this is correct:** server.py writes counter.next and then renames it, so an interrupted write leaves the old counter.json intact. read_counter validates schema on startup.

**A plausible wrong approach:** Checking only for exit code 0 passes even if the counter file was truncated, because the process can exit cleanly after a bad write.

**How to verify:** After stop and start, GET /counter returns the last acknowledged value with schema_version 1, and the app logs show no invalid counter state error.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
