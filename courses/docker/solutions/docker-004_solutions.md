# docker-004: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

PID is a process identifier within a process namespace. The container’s initial process has PID 1 in that namespace and participates in special Linux signal and child-reaping behavior. Docker normally considers a container alive while its main process remains alive. Starting a server in the background and allowing the main shell to exit therefore does not create a durable service.

A signal is a notification delivered to a process. A graceful termination handler stops accepting new work, lets bounded in-flight work finish, closes resources and exits. An abrupt kill cannot perform application cleanup. Docker stop ordinarily sends the configured stop signal, waits for a grace period and then forces termination if necessary.

The exec form of a Dockerfile command gives the runtime an argument array directly. The shell form starts a shell, whose signal forwarding and child handling can become relevant. An init process can reap adopted children and forward signals, but it does not add application-specific transaction recovery. Good shutdown is a cooperation between the orchestrator, process tree and application.

Compare `CMD ["python", "server.py"]` with `CMD python server.py`. The JSON array has no shell interpolation; each string is one argument. Compose `init: true` requests a small init where supported. The fixture uses it, sets a stop grace period, and logs to standard streams. Do not add an infinite sleep to hide that the real application exited.

For a shutdown investigation record the main process, signal, elapsed time, exit status and whether data is consistent. Exit 137 often indicates a SIGKILL-style termination, but by itself does not prove an out-of-memory cause. Inspect the engine’s OOMKilled state and events before concluding why a process was killed.

## Exercise 1: Predict what happens when the main process exits.

A container is not a VM with an independent background boot lifecycle. Its main process lifecycle drives the container state even if a script attempted to background work.

**Expected:** The container enters an exited state.

## Exercise 2: Compare exec-form and shell-form startup.

The difference affects expansion and process hierarchy. It is not a claim that every shell command is wrong, but shell wrappers must intentionally forward signals and wait for children.

**Expected:** An argument array versus an intervening shell.

## Exercise 3: Write a four-step graceful shutdown sequence.

An unbounded drain can prevent shutdown forever. Resource cleanup should be explicit, and data correctness may need a transaction or recovery protocol beyond closing file handles.

**Expected:** Stop new work, bound draining, close owned resources, exit.

## Exercise 4: Diagnose a service kept alive only by sleep.

The sleep process can make a status look running while the real server has crashed. Measure the application’s endpoint and actual process rather than adding a liveness placeholder.

**Expected:** The alive container does not prove the application is healthy.

## Exercise 5: Explain why exit 137 is not a complete OOM diagnosis.

A user or timeout can also send a kill signal. Correlate termination state with OOMKilled and relevant events before recommending memory changes.

**Expected:** It identifies a termination pattern, not its unique cause.

## Exercise 6: Design a shutdown acceptance check for a writer.

The important observation is what readers see after recovery. A clean exit code is useful but cannot by itself prove that a partially written application record is valid.

**Expected:** Bounded stop, consistent persisted record and restart recovery.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
