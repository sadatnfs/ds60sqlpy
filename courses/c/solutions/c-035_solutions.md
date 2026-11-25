# c-035: explained solutions

`c-035_solution.c` assembles the "install and restore a handler" case through the "transfer a bounded shutdown model" case in one `main.c`.

Compare only after an attempt: [Compare and transfer](../STUDY-GUIDE.md#compare-and-transfer).

## Mechanism and assumptions

A signal is an asynchronous notification delivered to a process or thread under platform rules. A handler can interrupt ordinary execution at an inconvenient point, so it cannot safely call arbitrary library functions or manipulate general shared state. Keep handlers minimal: record a permitted signal flag and let normal control flow perform cleanup. volatile sig_atomic_t is the standard C pattern for a simple handler communication flag, but volatile is not a general thread synchronization mechanism. A synchronous raise in this fixture makes observation deterministic. Production signal handling needs a broader shutdown and interrupted-system-call policy.

signal installs a handler and returns the previous disposition or SIG_ERR. raise delivers a signal to the running program according to the implementation. A handler receives the signal number. Assign a sig_atomic_t flag and return. Do not call printf, malloc or mutex operations from a portable signal handler. ISO C lets an implementation reset a disposition to SIG_DFL before it calls the handler. glibc does exactly that when a program is compiled in a strict ISO mode such as -std=c17, the mode the classroom uses (System V semantics), so a second SIGINT would terminate the process unless normal flow reinstalls the handler first; a -std=gnu17 build keeps the handler (BSD semantics). The Linux production alternative sigaction offers precise, documented disposition control and is a separate POSIX API.

## Exercise 1: Install and restore a handler: predict an edited check

In worked example 1, change `CHECK(signal(SIGINT, previous) != SIG_ERR);` to `CHECK(signal(SIGINT, previous) == SIG_ERR);`. Predict whether the CHECK still holds and why, then run and restore.

The unchanged code is worked example 1:

```c
void (*previous)(int) = signal(SIGINT, lesson_handler);
CHECK(previous != SIG_ERR);
CHECK(signal(SIGINT, previous) != SIG_ERR);
```

**Expected:** `Check failed`: `CHECK(signal(SIGINT, previous) == SIG_ERR);` is false, although both operations succeed.

**Verify:** Explain which claim `CHECK(signal(SIGINT, previous) == SIG_ERR);` makes that the state fails; restoring `CHECK(signal(SIGINT, previous) != SIG_ERR);` passes again.

The fixture restores process state instead of leaving a changed signal policy for unrelated later work.

## Exercise 2: Record a raised notification: diagnose an edited check

Worked example 2's CHECK now reads `CHECK(signal(SIGINT, previous) == SIG_ERR);`. Explain why it fails although the signal flag becomes one, then restore it.

The unchanged code is worked example 2:

```c
signal_seen = 0;
void (*previous)(int) = signal(SIGINT, lesson_handler);
CHECK(previous != SIG_ERR);
CHECK(raise(SIGINT) == 0);
CHECK(signal_seen == 1);
CHECK(signal(SIGINT, previous) != SIG_ERR);
```

**Expected:** `Check failed` until the CHECK reads `CHECK(signal(SIGINT, previous) != SIG_ERR);` again, though the signal flag becomes one.

**Verify:** Explain why `CHECK(signal(SIGINT, previous) == SIG_ERR);` rejects a state that `signal(SIGINT, previous) != SIG_ERR` accepts, using your failing and repaired runs.

The handler only assigns a flag. The ordinary flow performs assertions and restoration after the handler returns.

## Exercise 3: Keep work outside the handler

Raise SIGINT with the lesson handler installed and let a normal-flow function turn the recorded flag into a shutdown decision.

```c
signal_seen = 0;
void (*previous)(int) = signal(SIGINT, lesson_handler);
CHECK(previous != SIG_ERR);
CHECK(!stop_requested());
CHECK(raise(SIGINT) == 0);
CHECK(stop_requested());
CHECK(signal(SIGINT, previous) != SIG_ERR);
signal_seen = 0;
```

**Expected:** The decision is continue before the signal and stop after the handler records it.

**Verify:** Keep a CHECK equivalent to `!stop_requested()`. Control edit: changing `signal_seen = 0;` to `signal_seen = 1;` must fail it; then restore it.

The handler only records the event. Complex cleanup belongs to the caller of stop_requested, where ordinary library and ownership rules apply.

## Exercise 4: Handle no notification

Install the handler without raising a signal, inspect the decision and restore the previous disposition.

```c
signal_seen = 0;
void (*previous)(int) = signal(SIGINT, lesson_handler);
CHECK(previous != SIG_ERR);
CHECK(!stop_requested());
CHECK(signal(SIGINT, previous) == lesson_handler);
```

**Expected:** Installing a handler records no notification, and the restoring call returns the lesson handler.

**Verify:** Keep a CHECK equivalent to `!stop_requested()`. Control edit: changing `signal_seen = 0;` to `signal_seen = 1;` must fail it; then restore it.

Installing a handler does not deliver a signal. The value returned by the restoring call proves the handler was still installed, so no delivery had reset it.

## Exercise 5: Reinstall after a delivery

Raise SIGINT once, reinstall the handler in normal flow, then raise it a second time before restoring the original disposition.

```c
signal_seen = 0;
void (*previous)(int) = signal(SIGINT, lesson_handler);
CHECK(previous != SIG_ERR);
CHECK(raise(SIGINT) == 0 && signal_seen == 1);
void (*after)(int) = signal(SIGINT, lesson_handler);
CHECK(after == SIG_DFL || after == lesson_handler);
signal_seen = 0;
CHECK(raise(SIGINT) == 0 && signal_seen == 1);
CHECK(signal(SIGINT, previous) != SIG_ERR);
signal_seen = 0;
```

**Expected:** Both deliveries are handled. In the classroom worker the reinstalling call returns SIG_DFL, because glibc in -std=c17 mode reset the disposition after the first delivery.

**Verify:** Keep a CHECK equivalent to `signal(SIGINT, previous) != SIG_ERR`. Control edit: `CHECK(signal(SIGINT, previous) == SIG_ERR);` must fail; then restore it.

ISO C allows the reset, so code that relies on signal must reinstall the handler before the next delivery. Without the reinstall, the second raise in a System V build would terminate the process. The check accepts both results the standard permits, while the expected observation records what the classroom compiler does; sigaction removes the ambiguity.

## Exercise 6: Transfer a bounded shutdown model

Raise SIGINT while two tasks are active and stop admitting work in normal flow, retaining the active-work count.

```c
signal_seen = 0;
void (*previous)(int) = signal(SIGINT, lesson_handler);
CHECK(previous != SIG_ERR);
bool accepting = true;
int active = 2;
CHECK(raise(SIGINT) == 0);
if (stop_requested())
  accepting = false;
CHECK(!accepting && active == 2);
CHECK(signal(SIGINT, previous) != SIG_ERR);
signal_seen = 0;
```

**Expected:** Admission stops and unfinished work remains visible.

**Verify:** Keep a CHECK equivalent to `!accepting && active == 2`. Control edit: changing `int active = 2;` to `int active = 3;` must fail it; then restore it.

A stop request does not mean in-flight operations completed. Drain or cancel them under a separate bounded policy.

## After comparison

Install `lesson_handler` for `SIGTERM`, raise `SIGTERM` and predict `stop_requested()` first: the handler runs but records only `SIGINT`, so the flag stays 0. CHECK that, restore the previous `SIGTERM` disposition, then extend the handler to accept both numbers and CHECK that the flag is set. Explain why calling `printf` inside the handler would not be async-signal-safe, while assigning a `volatile sig_atomic_t` is.
