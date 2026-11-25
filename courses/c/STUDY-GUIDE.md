# C study guide

Every C lesson guide in this track uses the same classroom pad, the same checked
reference layout and the same six-exercise structure. This page explains those
shared routines once. Each lesson keeps what is specific to its own mechanism:
the mental model, vocabulary, syntax anatomy, two worked examples, the six
exercises with their expected observations, hints and control edits, and the
pitfalls that lesson invites.

## Run a C lesson

Open the unified Docker classroom, choose C and save a pad for the lesson. The
Linux worker compiles your `main.c` as C17 with warnings and pthread support,
then runs it under bounded time and output. You need no host compiler, and
Windows uses WSL 2.

The pad takes no extra compiler flags, interactive input, archives, host files
or packages. Files a reference creates are owned temporary fixtures, not saved
progress. Multi-file builds and sanitizer runs are contributor workflows that
need an explicitly prepared environment.

For an independently prepared Linux contributor environment, copy your own file
to an ignored working directory and run:

```sh
cc -std=c17 -Wall -Wextra -Wpedantic -pthread main.c -lm -o lesson
./lesson
```

## Reference layout and the always-on CHECK

Every reference is one `main.c` with `int main(void)`. It includes the standard
headers `<assert.h>`, `<limits.h>`, `<stdbool.h>`, `<stddef.h>`, `<stdint.h>`,
`<stdio.h>`, `<stdlib.h>` and `<string.h>`, plus any extra header a lesson
names. Helper functions sit above `main`, and each of the six cases runs in its
own block inside `main`. Solution snippets belong inside `main` unless they
declare a helper. Each worked example in a guide is a complete `main.c` that
prints `Worked example checks passed.`; worked example 2 repeats example 1's
case before adding its own.

`CHECK(condition)` calls `lesson_check`, which evaluates the condition once.
A true condition prints nothing. A false one writes `Check failed at main.c:`
and the line number to stderr, then calls `abort()`, so the run stops with a
nonzero status and the final success line never prints. Unlike `assert`,
defining `NDEBUG` cannot remove a CHECK, so a lesson's validation never depends
on optional assertions. Do not use `assert` as a substitute for validating
input in your own programs.

## Work an exercise

Exercise 1 changes one token in worked example 1 and asks you to predict the
result before running. Exercise 2 shows worked example 2 with a one-token
regression to diagnose and repair. Exercises 3 to 6 are investigations you write
yourself; each states the observation its CHECK must confirm.

When an exercise resists you, use the hints in order:

1. Restate the expected observation in your own words.
2. List the values the CHECK reads and trace each one from its initialization
   to the CHECK. Write down the declared size of every array it touches.
3. Apply the exercise's own hint, which names the edit or value to reason
   about, and predict the result before running anything.

## Control edits and regressions

Each Verify line names a control edit: one token that, when changed, makes the
CHECK fail. Every control edit and every regression in Exercises 1 and 2 was
executed in the prepared worker and observed to stop with `Check failed` at
that CHECK with no sanitizer report, so the edited program is defined. A
control proves that your CHECK can fail; a CHECK that passes no matter what the
code does proves nothing.

Keep the failing run and the repaired run side by side as evidence. Repair the
line that produced the wrong value, never the CHECK that reported it, and
restore every control edit before moving on.

## Diagnose failures

Fix compiler diagnostics one cause at a time, starting with the first warning;
a declaration mismatch early in a file cascades into later messages. When a
CHECK fails, compare the actual value with the claim the CHECK encodes and find
the earliest statement where the program state departed from your trace.

Separate three outcomes: a compiler diagnostic, a valid rejection that the
lesson's contract expects, and undefined behavior. A clean compile, or a run
that did not crash, does not rule out undefined behavior. Never run an
out-of-bounds access, a dangling read or a data race to see what it prints;
explain the bad expression as text and run a defined alternative instead.

For every pointer and index, name its target, bounds, alignment, lifetime and
mutability. Check each library result before using it, and release each owned
resource exactly once on every path.

## Compare and transfer

Compare with the explained solutions only after an attempt or an explicit
reveal. The reference program implements all six cases in one `main.c`;
reading it is not evidence of independent mastery, so rebuild a case from a
blank file before you count it as learned.

To transfer a lesson, add a fresh distinguishing input to your own source and
predict its result before running. Explain why every access stays within a
live object and every owned resource is released. An expected rejection belongs
in the test contract; undefined behavior does not. Keep diagnostics and
sanitizer evidence apart from ordinary output: a fixture proves the assumptions
it states, not universal safety.

## Sources and execution boundary

Each lesson links one primary reference, reviewed 2026-10-23. Teaching
explanations and synthetic fixtures are original. Keep ISO C17 guarantees
separate from POSIX and compiler-specific behavior. Pthreads, pipes and file
descriptors are Linux-container capabilities; native Windows is not a backend
target. Sanitizers and multi-file Make projects are prepared contributor
workflows, not capabilities of the one-file pad.
