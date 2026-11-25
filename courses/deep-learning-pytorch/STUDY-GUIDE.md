# PyTorch study guide

Every executable lesson in this course runs on the same prepared worker, follows the
same worked-example sequence and uses the same six-exercise layout. This page explains
those shared routines once. Each lesson guide keeps only what belongs to its own
mechanism: the mental model, the worked examples, the exercise contracts, the state
that carries between its worked blocks, its pitfalls and its interview reasoning.

## Launch a lesson

Start or resume the Docker classroom with `./classroom` from the repository root. On
Windows, run that command in WSL 2. In the shared home, choose the **Deep Learning with
PyTorch: tensors to reliable model releases** subject and select the lesson. Use its
`llm-torch-cpu` worker and wait for readiness before choosing **Run**. The
[classroom instructions](../../docs/one-command-classroom.md) explain how to prepare a
missing profile.

The worker supplies the declared packages and starts a fresh Python process for every
run, so no host Python or framework installation is needed. Save your current attempt
before replacing the pad with a complete worked example. Inputs are small local
fixtures: no package installation, dataset or model download, or online service call
is part of an ordinary lesson.

For an optional contributor workflow on Linux, macOS or Windows through WSL 2,
deliberately prepare an interpreter with the same declared dependencies, then run it
on an owned copy of the lesson's learner file under `.learning/expansion/<lesson-id>/`.
The general contributor uv environment does not imply that TensorFlow or PyTorch is
installed. The Docker profile remains the default execution route.

The first lesson, `torch-001`, is a reading worksheet. It has no worker run; you write
a reasoned response for each case instead.

## Run the worked sequence

Each guide's "How to run this lesson" section names the variables and helpers that its
Examples B and C reuse. Run the three worked blocks in order in one scratch file. To
reproduce a later block in a fresh process, include the blocks before it.

1. Read Example A without running it and write its intermediate quantities, with
   units, on paper.
2. Run the entire example in a fresh process, not only the final line in a notebook
   whose hidden variables can mask a missing definition.
3. Read Examples B and C as controlled changes to Example A's assumptions. Compare
   value, gradient and state contracts separately: equal forward numbers do not prove
   equal optimizer or training-mode behavior.
4. Compare your prediction with both observations before starting the exercises.

An assertion failure is a request to inspect an assumption, not a reason to widen every
tolerance. Use the explicit tolerance in each assertion. Several analytic float64
fixtures use `1e-12` and float32 fixtures use `1e-6`, but dtype alone is not a universal
numerical-error bound. Finite differences, reductions and conditioning can require
different justified tolerances. Integer counts, identities and boolean decisions should
be exact.

## How the exercises are organized

In most lessons the worked examples demonstrate the mechanism, exercises 1 to 3
transfer it to new inputs, and exercises 4 to 6 extend it to failures and boundary
cases. A few lessons whose references are bound to recorded runtime receipts keep an
older layout instead: exercises 1 to 3 repeat the worked examples as guided
reconstructions, and exercises 4 to 6 change the fixture or expose a failure. Those
lessons say so under their learning objectives.

A useful explanation connects each calculation to the reason it is needed rather than
treating a function name as a definition. Each exercise lists its **Expected**
observation and a **Verify** line naming the checks that confirm it in a fresh process.

## Prerequisites and next steps

Each guide names its direct prerequisite. That lesson introduces the notation used
next, so revisit its worked examples when an axis, probability or gradient is
unfamiliar. When you finish a lesson, keep your exercise 2 attempt as a regression case
beside a fresh transfer input before moving on. In a capstone, a failed acceptance
condition is a valid no-go decision; record the evidence that would reopen it.

## Sources and verification status

Each guide cites the PyTorch API or mechanism reference it was reviewed against. The
fixtures, examples, counterexamples and exercise design are original course material.
See [validation](../../docs/validation.md) for the execution gates. Check the CI
artifacts for the exact revision and platform to learn which runtime checks actually
ran; authored content alone does not establish runtime execution.

## After the solutions

Each lesson has an executable reference (`solutions/<lesson-id>_solution.py`) and an
explanatory solutions page. Open them only after your own attempt. After comparing:

1. Repeat exercise 4 with one changed fixture value and predict the difference before
   running it.
2. Keep your failing attempt at exercise 5 beside the repaired result and name the
   first value that differed.
3. Choose a new input for exercise 6 and solve it without looking.

A missing framework is not a failing assertion: if the worker is unavailable, record
the code as unexecuted rather than copying the expected text. The solutions use only
local fixtures.
