# Go study guide

Every Go lesson guide in this track uses the same classroom, the same `check`
helper and the same six-exercise structure. This page explains those shared
routines once. Each lesson keeps only what is specific to its own mechanism:
the model, the worked examples, the exercise contracts, the predictions to make,
the mistake that lesson invites and a retrieval task in a new domain.

## Run a lesson

Choose Go in the unified Docker classroom and save your own pad before
experimenting. The prepared worker stages the pad as `main.go`, compiles it and
executes the resulting program with bounded time and output. The pad is one
source file. It does not supply interactive input, arbitrary command-line
arguments, package installation, Kubernetes credentials or a host Docker
socket. Ordinary references use the standard library, synthetic local data and
explicit checks.

`check` is a tiny teaching helper that panics when its condition is false:

```go
func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}
```

A failed `check` therefore produces a panic message and a nonzero process
result. Do not delete a check to make a run look successful; the check is the
evidence. Explanatory snippets in the solutions belong inside `func main()`
unless they declare a helper type or function.

## Build locally

For an independently prepared Go project on Linux or WSL 2, the equivalent
local build is:

```sh
go build -o lesson main.go
./lesson
```

Compiling proves that names and types are consistent. Only the executed checks
establish the stated example contracts.

## Read the worked examples

Each worked example is a complete Go file. Copy one whole block into your saved
pad and run it. Worked example 2 contains the first case as well as the second,
so it also carries every import and helper declaration the lesson needs; later
investigations may reuse those declarations. The separate reference in
`solutions/` implements all six cases in one `main.go`.

## Predict before running

Before each run, write three things: the input values, the state that can
change and the observation you expect. Then name the result that would disprove
your current interpretation. For concurrent code, predict a guaranteed
relationship (a count, a happens-before edge, a closed channel) rather than an
arbitrary scheduling order. For an error case, say whether the compiler rejects
it or the program returns or panics during execution.

## Work an exercise

Each lesson has six exercises. The first two start from the worked examples:
exercise 1 asks you to make one edit and predict its effect, and exercise 2
gives you a regression or a careless edit to diagnose. Exercises 3 to 6 are new
investigations written in the answer-free learner source under `lessons/`.

Every exercise has two contract lines:

- **Expected** states the observation a correct attempt produces.
- **Verify** states the evidence that proves it, usually a control edit.

A control edit is a one-token change that was observed to make that exercise's
check panic with the named message. Apply it, confirm the panic, then restore
the line. A check that no input can falsify is not evidence. Keep one
independent check per claim. A task may require tracing, construction, a
changed input or a deliberate safe failure. Never run a data race, corrupt
memory or contact a shared cluster merely to show why it would be wrong.

## Use hints one at a time

Each exercise has three progressive hints. The first restates the expected
observation, so you can confirm you are solving the right problem. The second
points at the mechanism the exercise depends on. The third is close to the
answer: either the concrete edit to evaluate by hand or the key reason the
result holds. Open the next hint only after you have tried the previous one and
written down what you still do not know.

## Diagnose a failure

- **Compiler error:** read from the first reported location in your own source
  and fix one cause at a time. Later errors are often consequences of the first.
- **Unused import or variable:** this is an error in Go. Add an import when its
  use exists rather than copying a large import list.
- **Panic from `check`:** a stated contract was violated. Compare the actual
  value with the expected value, then inspect the state change that produced it.
- **Returned `error`:** an error is an ordinary value that the caller must
  handle. An ignored error can make later output look plausible while the
  original operation failed.
- **Timing-dependent result:** replace sleeps used as synchronization with
  channels, mutexes or an explicit ownership protocol.

Treat empty data, missing values and cancellation as domain cases with explicit
policies, not as accidents to patch after a failure.

## Self-check and retrieval

Close the reference before a self-check. Rebuild one normal case and one
boundary case from a blank pad. Explain the lesson's main term without using
its name. Then change the domain while keeping the same invariant, and record
the new input, your prediction and the observed output. If a program passes
only because its input is hard-coded, decide which part would become a reusable
function in a larger project. Each lesson's self-check section gives a specific
task for this routine.

## Use the solutions

Open `solutions/` only after an attempt or an explicit reveal. The executable
reference proves that all six cases run together; the explained solutions show
the code for each case, its expected observation and why it holds. Several
lessons also add an approach, a plausible wrong approach and a verification
step per case. Keep the distinction between a pure model, an in-process fake
and a real external system visible in your notes.

## When to move on

Continue when you can explain the six observations and diagnose a changed case
without copying its answer. Primary sources linked from each lesson were
reviewed on 2026-10-23. The teaching explanations and synthetic fixtures are
original to this course.

## Ask an AI tutor

Each lesson ends with a tutor prompt for `$guide-ds60sqlpy-learning`. It names
the guide, your saved attempt and the solution files to keep closed. Paste it
into a tutor session, attempt each prediction before asking for a hint, and ask
for a reveal or comparison explicitly when you want one.
