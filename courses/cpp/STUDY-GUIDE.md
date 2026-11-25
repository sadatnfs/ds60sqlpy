# C++ study guide

Every lesson in this track shares the same files, the same browser worker and the
same six-exercise routine. This page explains those shared routines once, so each
lesson guide can spend its words on its own mechanism: what its pad proves, what
its two worked programs contrast, its exercises and the transfer question that
closes it. Read this page before your first pad and return when a guide links
to a section.

## Lesson files

Each lesson `cpp-NNN` has four files:

- `guides/cpp-NNN.md` is the guide: mechanism, worked examples, six exercises,
  self-check and pitfalls.
- `lessons/cpp-NNN.cpp` is the learner pad. Its `main` already asserts the
  lesson's normal and boundary cases, and comments at the end list the six
  exercises with their expected results.
- `fixtures/cpp-NNN-cases.json` is the case ledger. It records each exercise's
  input or change and the expected observation. Treat it as immutable: when your
  run disagrees with it, change your program or your reasoning, never the ledger.
- `solutions/cpp-NNN_solutions.md` holds the explanations, and
  `solutions/cpp-NNN_solution.cpp` is the executable reference. Keep both closed
  until you have attempted a task or deliberately asked for a reveal.

The reading pilot `cpp-001` uses a Markdown worksheet instead of a `.cpp` pad,
because it studies transcripts rather than running code.

## Run a lesson pad

Open the unified classroom, choose C++ and open the lesson's pad. Predict the
output, edit, save, then choose Run. The `cpp20` worker stages the pad as
`main.cpp`, compiles and links that one translation unit as C++20 with warnings
and thread support, then runs it under bounded time and output.

Read the result in phases. A compiler diagnostic means no new program was built.
A linker error means compilation succeeded but a definition is missing or
duplicated. Only after both succeed do stdout, stderr and the exit status describe
your program. A pad that ends by printing its `examples passed` line exited with
status 0 after every assertion in `main` held.

[The compile and run tutorial](compile-and-run.md) gives the exact local commands,
flags, exit-status capture, path rules and the Docker route. Use it when you want
to reproduce a Run outside the browser.

## Host projects

The browser accepts exactly one source file and fixed flags. Work that needs
several translation units, headers you install, CMake or CTest targets, sanitizer
or debugger flags, shared libraries or timing on a quiet machine is a host-project
exercise. Do it in an owned scratch folder or the Docker-only project route in
the tutorial, and record what you actually built and ran. A pad Run is not
evidence for any of those activities.

## Worked examples

Each worked example is a complete, independent program. Copy one into `main.cpp`
or compile its checked-in file under `examples/` with the tutorial's command. Do
not concatenate two examples: each defines its own `main`, and two `main`
functions in one translation unit do not compile.

Build with assertions enabled. The printed `example N checks passed` line runs
only after the displayed assertions held, so it is a bounded check of those exact
values. It is not a substitute for the six exercises, which change the inputs and
ask you to predict before you run.

## Work the six exercises

Work the exercises in order. Each states the input or change, the **Expected**
result and a **Verify** step that says how to check that result.

1. Predict the result in writing before running anything.
2. Make the change in a scratch copy of the pad so the original assertions stay
   available as a regression check.
3. Run, then compare the observation with the Expected line and the case ledger.
4. When an exercise asks for a compile failure, keep the first diagnostic and
   name the phase and the source location; exact vendor wording varies.
5. Use the progressive hint only after a prediction, and record which part of
   the mechanism the hint changed in your reasoning.

## Self-check and retrieval

The self-check asks you to explain one observation from the mechanism and one
change in worked example 2. Answer from memory, then reopen the guide to check.
The retrieval prompt asks you to rebuild one exercise with the source closed and
to name the assumption that would break at a larger scale or on another platform.
Write that answer down before moving to the next lesson.

## Compare with the solutions

Open the explanations only after an attempt. The executable reference keeps the
pad's assertions and adds checks for the exercise changes that a single program
can demonstrate. Exercises that require a compile failure, a host project or a
written review appear only as reasoning and Verify steps. Compare your evidence
with the reasoning, not just the final value; a different but correct program is
fine when it satisfies the same contract. An authored reference is not a platform
acceptance receipt for your machine.
