# c-035: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

A signal is an asynchronous notification delivered to a process or thread under platform rules. A handler can interrupt ordinary execution at an inconvenient point, so it cannot safely call arbitrary library functions or manipulate general shared state. Keep handlers minimal: record a permitted signal flag and let normal control flow perform cleanup. volatile sig_atomic_t is the standard C pattern for a simple handler communication flag, but volatile is not a general thread synchronization mechanism. A synchronous raise in this fixture makes observation deterministic. Production signal handling needs a broader shutdown and interrupted-system-call policy.

signal installs a handler and returns the previous disposition or SIG_ERR. raise delivers a signal to the running program according to the implementation. A handler receives the signal number. Assign a sig_atomic_t flag and return. Do not call printf, malloc or mutex operations from a portable signal handler. The Linux production alternative sigaction offers more precise disposition control and is a separate POSIX API.

## Exercise 1: Install and restore a handler

Install the lesson handler for SIGINT and restore the previous disposition.

```c
void (*previous)(int) = signal(SIGINT, lesson_handler);
CHECK(previous != SIG_ERR);
CHECK(signal(SIGINT, previous) != SIG_ERR);
```

**Expected:** Both operations succeed.

The fixture restores process state instead of leaving a changed signal policy for unrelated later work.

## Exercise 2: Record a raised notification

Raise SIGINT while the lesson handler is installed.

```c
signal_seen = 0;
void (*previous)(int) = signal(SIGINT, lesson_handler);
CHECK(previous != SIG_ERR);
CHECK(raise(SIGINT) == 0);
CHECK(signal_seen == 1);
CHECK(signal(SIGINT, previous) != SIG_ERR);
```

**Expected:** The signal flag becomes one.

The handler only assigns a flag. The ordinary flow performs assertions and restoration after the handler returns.

## Exercise 3: Keep work outside the handler

Translate an already set flag into a normal-flow shutdown decision.

```c
signal_seen = 1;
bool stop = (signal_seen != 0);
CHECK(stop);
signal_seen = 0;
```

**Expected:** The normal-flow decision becomes stop.

Complex cleanup belongs outside the handler, where ordinary library and ownership rules apply.

## Exercise 4: Handle no notification

Inspect a cleared signal flag.

```c
signal_seen = 0;
CHECK(signal_seen == 0);
```

**Expected:** The shutdown decision remains false.

The explicit initial state prevents a stale flag from being mistaken for a new event.

## Exercise 5: Reset between independent operations

Set then clear the flag in ordinary control flow.

```c
signal_seen = 1;
signal_seen = 0;
CHECK(signal_seen == 0);
```

**Expected:** The next operation begins without a stale notification.

Reset policy is part of lifecycle design. A real event loop must consider whether clearing can race with a new notification.

## Exercise 6: Transfer a bounded shutdown model

Stop admitting work after observing the signal flag while retaining active-work count.

```c
bool accepting = true;
int active = 2;
signal_seen = 1;
if (signal_seen)
  accepting = false;
CHECK(!accepting && active == 2);
signal_seen = 0;
```

**Expected:** Admission stops and unfinished work remains visible.

A stop request does not mean in-flight operations completed. Drain or cancel them under a separate bounded policy.

## After comparison

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.
