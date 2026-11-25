# TensorFlow study guide

Every lesson in this course shares the same launch routine, the same worked-example
habits and the same six-exercise layout. This page explains those shared routines
once. Each lesson guide keeps what belongs to its own mechanism: the mental model,
the worked examples, the exercise contracts, its pitfalls and its tutor prompt.

## Launch a lesson

Start or resume the Docker classroom with `./classroom` from the repository root. On
Windows, run that command in WSL 2. In the shared home, choose the **Deep learning
with TensorFlow and Keras** subject and select the lesson. Each guide names its
worker: `python-core` for the NumPy foundations and the evidence lessons, and
`tensorflow-cpu` for framework lessons. Wait for readiness before choosing **Run**.
The [classroom instructions](../../docs/one-command-classroom.md) explain how to
prepare a missing profile, and the [Docker classroom guide](../../docs/docker-classroom.md)
describes each profile.

The worker supplies the declared packages and starts a fresh Python process, so no
host Python or TensorFlow installation is needed. Save your current attempt before
replacing the pad with a worked example. Inputs are small local literals: no package
installation, dataset or model download, or online service call is part of an
ordinary lesson.

The checked-in learner file in `lessons/` is a reusable worksheet, so edit a copy
rather than the original. For an optional contributor workflow on Linux, macOS or
Windows through WSL 2, deliberately prepare an interpreter with the lesson's declared
dependencies, then run it on an owned copy saved under
`.learning/expansion/<lesson-id>/`. The general contributor uv environment does not
imply that TensorFlow or PyTorch is installed. A missing dependency is a runtime setup
issue; do not install packages inside a lesson. The Docker profile remains the default
execution route.

The first lesson, `tf-001`, is a reading worksheet. It has no worker run; you record
predictions and a reasoned response for each case in the saved notes instead.

## Run the worked examples

1. Read Example A without running it. Write its intermediate quantities, with units,
   on paper.
2. Run the entire example in a fresh process, not only the final line in a notebook
   whose hidden variables can mask a missing definition.
3. Read the later examples as controlled changes to one assumption of Example A, and
   compare the observations before starting independent work.

Lessons `tf-002` to `tf-008` use a sequential scratch-file contract: run Examples A
and B in order in one scratch file, then run that complete file in a fresh process.
Example B may reuse the imports, helpers and fixture state from Example A, so do not
treat the later block as a standalone program. From `tf-009` on, each example block
repeats what it needs and runs on its own.

An assertion failure is a request to inspect an assumption, not a reason to widen
every tolerance. For float64 arithmetic use an absolute tolerance of `1e-12` unless an
exercise gives another bound. TensorFlow and PyTorch float32 comparisons use `1e-6`.
Integer counts, identities and boolean decisions should be exact.

## Predict before running

Before executing or calculating, write the result you expect from the normal fixture
and the changed condition that would invalidate it. Save that prediction. Afterward,
name the first observation that supported or contradicted it rather than rewriting
your original answer to match the reference. Each guide's prediction section names
the example and exercise to predict.

## Exercise plan

Each lesson has six exercises. Each one states an **Expected** observation and a
**Verify** line that names the check confirming it.

* In most lessons, exercises 1 and 2 repeat the worked examples as guided
  reconstructions, and exercises 3 to 6 change the fixture or expose a failure.
* In transfer lessons, the worked examples demonstrate the mechanism, exercises 1 and
  2 transfer it to new inputs, and exercises 3 to 6 extend it to failures and
  boundary cases.

A useful explanation connects each calculation to the reason it is needed rather than
treating a function name as a definition. Keep your first prediction alongside the
actual evidence so a changed conclusion remains visible, and explain one plausible
wrong result as well as the right one.

To review your own evidence, score five dimensions 0, 1 or 2: the declared data or
observation contract, a correct normal-case derivation, diagnosis of the changed
fixture, explicit handling of the invalid case, and a fresh explanation of the
evidence boundary. Normally seek 8 out of 10 with no zero for the contract or the
claim boundary, then require a new transfer example. This is a human learning rubric,
not an automatic certification or a completion awarded by one successful Run.

## Prerequisites and next steps

Each guide names its direct prerequisite. That lesson introduces the notation used
next, so revisit its worked examples when an axis, probability or gradient is
unfamiliar. The [course README](README.md) lists the authored sequence and the
runtime of every lesson; check the next lesson's runtime readiness before running it.

The entry Python course supplies basic functions, lists, dictionaries, testing and
NumPy arrays. Each lesson introduces its subject terms and needs no service account,
model weights, GPU or database.

When you finish a lesson, keep your exercise 2 attempt or the smallest counterexample
you found as a regression case beside a fresh transfer input, and rerun it when later
abstractions appear. In a capstone, a failed acceptance condition is a valid no-go
decision; record the evidence that would reopen it.

## Verification status

Each guide cites the TensorFlow, Keras or NumPy reference it was reviewed against.
The fixtures, examples, counterexamples and exercise design are original course
material. See [validation](../../docs/validation.md) for the execution gates. Check
the CI artifacts for the exact revision and platform to learn which runtime checks
actually ran; authored content alone does not establish runtime execution.

## After the solutions

Each lesson has an explanatory solutions page, and executable lessons also have a
reference script, `solutions/<lesson-id>_solution.py`, whose `verify()` helper runs
the six exercise checks on local literals. A passing reference is evidence about
those fixed cases only. Open the solutions after an attempt or an explicit reveal,
and keep your own version beside them. A different implementation is acceptable when
it preserves the stated input policy, observations and evidence boundary. After
comparing:

1. Change one fixture value in exercise 4 and predict the new result before running
   it.
2. Keep the failing version of exercise 5 next to its repair, and explain why the
   rejected case is invalid rather than only naming the exception class.
3. Choose another fixture before treating the answer as independent retrieval
   evidence.

Do not replace a failed assertion with a flattering default value or remove an
invalid-input case. A missing framework is an environment record, not a failed
assertion: if the worker is unavailable, record the code as unexecuted rather than
copying the expected text. No solution downloads data, calls an online model, deploys
a service or changes a database. Keep implementation correctness separate from broad
claims about unseen model quality, reliability or safety.
