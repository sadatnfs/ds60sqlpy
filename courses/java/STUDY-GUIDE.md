# Java study guide

Every Java lesson guide links here for the routine that is the same in all 36
lessons: how a pad is compiled and run, how to run an example on your own JDK,
how the six exercises and their controls work, how to use hints, how to read a
failure and how to review after the solution. The lesson guides keep only what
is specific to their own programs.

## Run a lesson in the classroom

Open the Docker classroom, choose the prepared Java 21 profile and save a
learner pad before you edit it. The classroom compiles the pad as `Main.java`
with `javac --release 21` and runs it with `java -ea Main`.

The `-ea` flag enables assertions on purpose. A passing `assert` prints
nothing. A failing one throws `AssertionError`, and the process exits with a
failure status. Never delete or weaken an assertion to get a green run: the
assertion is the evidence. Lessons store the result of required work in a local
variable and assert on that variable, so a launch without `-ea` still performs
every operation.

## Run an example on a native JDK

With a prepared Java 21 JDK, copy a worked example into your own `Main.java`
under the ignored `.learning/expansion/<lesson-id>/` directory and run the same
two commands from that directory on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class is `Main`, so the file must be named `Main.java`. Each worked
example is a complete file, and Example B repeats the setup it needs from
Example A, so either compiles on its own. The six exercise reference blocks
form one complete program in the separate solution file.

Most lessons need only prepared JDK libraries and tiny local fixtures. When a
lesson needs anything more, such as the H2 driver in `java-029` or the manual
fixtures for modules, JARs and `jlink`, its guide names the exact file or path.
Do not download packages from inside a learner program. Examples that open
files, executors or loopback servers close what they own before they finish.

## Read before you run

Start at `main` and name each value before it is computed. Note which
operations create a new value, which mutate existing state and which can
throw. Then predict the first observable output or assertion result.

Decide first whether a failure would happen at compile time or at run time. A
program that does not compile never reaches `main`, so explain a compiler
diagnostic by the source rule it reports, not by runtime state. Keep normal,
boundary and invalid inputs in separate checks so each check has one purpose.
Write the prediction down; comparing it with the actual run is the point of
the exercise.

## How the six exercises are built

- Exercise 1 changes one input of Example A. Predict the result, run it,
  explain the reported value and restore the original line.
- Exercise 2 shows a one-token regression, or an edited assertion, in the code
  that Example B adds. Use the failing assertion to find and repair the defect
  without changing what the assertion claims.
- Exercises 3 to 6 are new investigations. Their **Expected** line states the
  observation, and their **Verify** line names a control edit.

A control edit is a one-token change that was compiled and run in the prepared
image and observed to make that exercise's own assertion fail. Keep an
assertion equivalent to the one in the reference, apply the control edit and
confirm that `java -ea Main` now fails with an `AssertionError` from that
assertion. Then restore the line. A check that still passes after its control
edit cannot tell a working program from a broken one.

## Use hints one at a time

Hints are written as rungs that begin with "First", "Then" and "Finally". Read
one rung, try the exercise again, and read the next rung only if you are still
stuck. Keep a small table of input, expected value, actual value and exception
type while you work. When you ask a tutor, ask about the first assumption that
turned out wrong rather than for the complete reference.

## Diagnose a failure

1. Keep the smallest source file that still shows the failure.
2. For a compiler error, read the first relevant diagnostic before editing
   several lines. Later diagnostics are often consequences of the same missing
   delimiter or wrong type.
3. For a runtime exception, find the first stack frame in your own code and
   compare the input it received with the method's contract.
4. For an assertion failure, compare the actual value with the independent
   expected value.

A clean exit is weaker evidence than a checked invariant, and a checked
invariant holds only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible
default; that hides invalid input or unfinished work. When code owns a
resource, check that it is released on both the success and the failure path.
In concurrent code, establish ordering with a synchronization primitive. An
observed timing coincidence is not a happens-before guarantee.

## Self-check and retrieval routine

Close the guide and the solution. Explain the lesson's key terms in your own
words, rebuild one example from a blank `Main.java`, and add a new boundary
input. Say whether that case should pass or fail before you compile it. Then
name one situation where the lesson's technique fits and one where a different
data structure, lifetime policy or abstraction would be clearer. The goal is
reasoning, not memorizing an API spelling.

## Use the solutions

Open the solutions folder only after an attempt or an explicit reveal. The
executable reference runs all six exercise checks together as one `Main.java`,
and the explanatory solution explains the choices and failure cases.

After comparing, run the complete reference with assertions enabled and return
to your own implementation. Recreate one check with different values and
predict its result before running it. Report a compiler error, an expected
domain exception and an assertion failure separately, because they come from
different stages. Keep ownership boundaries when you adapt file, network or
concurrency examples: a reference never authorizes access to a shared service
or deletion of learner state. Use a fresh tiny fixture when you need to tell
two readings of an API contract apart.

## Move to the next lesson

Keep your saved pad, your six exercise observations and at least one failing
counterexample next to its repaired version. Later lessons reuse these
contracts in larger programs. Move on when you can explain the lesson's
invariants without reading the answer. A reference implementation shows one
valid design under its stated assumptions; it is not a universal rule.

## Sources and evidence

Each guide links the official Java 21 API or language reference it was
reviewed against. Examples and exercise fixtures are original course material.
The [validation guide](../../docs/validation.md) and the CI artifacts for an
exact revision record actual compile and run results on a given platform.
Authoring, parsing, compilation, execution and learner mastery are separate
kinds of evidence; passing one does not establish another. The
[Docker classroom guide](../../docs/docker-classroom.md) covers image
preparation, logs and persistent learner state.
