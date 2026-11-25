# How to run and study a Python lesson

This page holds the operating routine that every Python lesson shares: the
60-day data science course in [ds-60day](ds-60day/README.md) and the
foundations, language, NumPy, pandas, algorithm and engineering modules in
[professional](professional/README.md). Each lesson guide links here instead of
repeating it, so the guide itself can spend its words on that lesson's concept,
data and traps.

## Run a lesson in the browser classroom

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use the same launcher from Ubuntu in WSL 2. Choose
**Python and data science** on the shared `/classroom` home, then open the
lesson by its stable ID (for example `python-02` or `python-numpy-05`). The
[launcher guide](../docs/one-command-classroom.md) covers first preparation,
`./classroom stop` and `./classroom resume`, and the
[classroom guide](../docs/classroom-experience.md) explains saved work,
runtimes and switching subjects. No host Python, notebook kernel or package
installation is needed for this route.

1. Read the lesson's capability notice before running anything. It states
   which coding or reading workflow the lesson supports in the prepared
   runtime and whether an optional extra is missing.
2. Paste or open the learner source in the saved coding pad. Drafts, notes and
   result history live in the Docker learning volume, not in your checkout.
3. Every browser Run starts a fresh Python process. Include imports, fixtures,
   function calls and checks in the saved source; in-memory arrays, closures,
   iterators and event loops do not survive between runs.
4. Learner files start answer-free. A `TODO` or a function that raises
   `NotImplementedError` is the expected starting state, not a setup failure,
   and a passing worked example does not mean the exercises are finished.
5. Save your prediction and the observed value, type, shape or exception next
   to the source that produced it, so a reviewer can reproduce the evidence.

### Optional contributor notebook route

Use a separately prepared POSIX environment on Linux/macOS or Ubuntu in
Windows WSL 2. Complete [contributor setup](../CONTRIBUTING.md) once,
including the notebook and data dependencies. Docker's Python worker does not
install packages into this host interpreter. Run the following commands from
the repository root using that prepared environment.

1. Check the interpreter and register its notebook kernel. Registration is
   needed once for this environment, or again after moving/replacing it:

   ```bash
   uv run --no-sync python scripts/course.py doctor --no-database
   uv run --no-sync python -m ipykernel install --user --name ds60sqlpy --display-name "Python (ds60sqlpy)"
   ```

   `--no-database` keeps this Python setup check local and does not require
   PostgreSQL. Do not install packages with `%pip` in a lesson. Use the
   declared dependency group when an optional import needs preparation.
2. Read the lesson's companion guide, then launch the notebook directory:

   ```bash
   uv run --no-sync python -m jupyter lab python/ds-60day/notebooks
   ```

   Open the lesson's notebook and select **Python (ds60sqlpy)**. The friendly
   name alone is insufficient if you use several checkouts: confirm that the
   kernel's `sys.executable` points to this checkout's `.venv/bin/python`.
   [VS Code guidance](../docs/vscode.md) explains the alternative editor
   route; Windows users open that editor in WSL with the same Linux environment.
3. Restart the kernel and run cells from the top. Notebook cells share kernel
   state; each browser Run starts a fresh process. Use **Run All** only after
   writing your predictions, then compare the actual value, type, shape or
   side effect.
4. Attempt the numbered exercises in your own scratch cells and keep a backup
   of your notebook edits. Do not edit the official solution while attempting
   the practice, and restart and run from the first cell before calling the
   lesson complete; a clean run catches hidden state and stale variables.

Notebook files and contributor CLI progress belong to this host checkout. They
are separate from the browser's saved pads, notes and progress in Docker
volumes. Neither route copies attempts or completion markers to the other, so
record progress in the interface you actually used.

### Optional contributor script route for professional modules

Professional modules ship a learner script in `python/professional/lessons/`.
In the prepared environment, open the repository folder in VS Code, copy the
script to an ignored folder under `.learning/` if you want to keep your attempt
across course updates, and run it from the repository root:

```sh
uv run --no-sync python python/professional/lessons/ <module >.py
```

The terminal shows the worked examples and the remaining `TODO` count. Read
each `TODO` as a contract: record the input, returned value, raised exception
and side effect before implementing it. Run after one change and compare with
the exercise's acceptance check. Some engineering modules also have a focused
test file in `python/professional/tests/`, run with
`uv run --no-sync pytest -q <test file>`. Keep exploratory changes in a copy or
a new test; the checked-in solution remains a comparison artifact. Local
`.learning/` files and CLI progress belong to this checkout; they never read or
update the browser's Docker learning volume, and this route is never a
prerequisite for the browser classroom.

## Optional extras and offline data

The default Python Core runtime covers most lessons. A few lessons use an
optional extra (`geo`, `ml`, `nlp`, `production` or `deep-learning`). Pressing Run
or choosing a notebook kernel never installs packages, so those lessons name a
prepared browser alternative course and an explicit preparation path. A host
notebook environment and a Docker app image are separate; see
[dependency profiles](../docs/dependency-profiles.md) and
[Docker app package options](../docs/docker-profiles.md) before preparing
either one, and never install packages inside a learner pad.

Course data is local. The [original synthetic fixtures](fixtures/README.md)
replace first-run sample-data downloads; their values demonstrate programming
methods, not historical or observational facts, so keep numerical conclusions
scoped to the declared teaching input. Reference model runs use `n_jobs=1` so
they behave the same on Windows, CI runners and small notebook environments.
Benchmark a larger worker count on your own workload only after correctness is
established.

## Study routine

1. **Predict first.** Before running a worked example, write down the shape,
   type or direction of the result, so a surprise becomes evidence.
2. **Practice in five modes.** Treat the numbered exercises as prediction,
   guided modification of a worked example, independent application with a new
   input, debugging an edge case at a boundary, and retrieval from memory with
   the guide closed.
3. **Treat each exercise as a contract.** Copy its input, expected behavior,
   constraints and **Verify** line into your work cell before writing code. A
   result is complete only when the stated assertion or inspection runs and you
   can say what it proves.
4. **Use hints after an attempt.** Read one progressive hint at a time, and
   only after an honest attempt.

## Compare with a reference solution

Each lesson links a separate explained solution and, for professional modules,
an executable reference. Open them only after an attempt with evidence, or when
you deliberately want a worked comparison.

- Run a professional reference from the repository root with
  `uv run --no-sync python python/professional/solutions/<module>_solution.py`.
  Its assertions are the evidence; the printed success line alone is not.
- Compare decisions before syntax: input validation, the returned value, the
  raised exception, ordering and mutation, and what the result is allowed to
  claim.
- Change one boundary input and make one assertion fail on purpose before
  accepting an answer. Then restore it and rerun from a fresh kernel or fresh
  process, because hidden notebook state can make a wrong answer look right.
- For each answer, state what the result proves, which assumption it relies
  on, and which input would make the policy reject or choose a different path.
- A reference is one defensible contract, not the only valid code. An
  alternative is acceptable when it keeps the same inputs, outputs, failure
  policy and evidence.

## Use an AI tutor (optional)

Each guide ends with a copyable tutor prompt. The guide, notebook or learner
script, and the stated checks are enough to finish a lesson without an AI
assistant. If you use one, copy the prompt from the repository root; it follows
the checked-in `guide-ds60sqlpy-learning` skill: explain, predict, attempt, one
progressive hint at a time, evidence and retrieval. Paths under `solutions/`
stay closed until you ask after an attempt. See
[learning with an AI tutor](../docs/learning-with-an-ai-tutor.md).

## Recover from common failures

- **Missing module in a notebook:** confirm the kernel's `sys.executable`
  before installing anything; a different checkout's kernel is the usual cause.
- **Missing optional package in the browser:** read the capability notice and
  use the lesson's prepared browser alternative instead of installing.
- **Result changes between runs:** restart and run from the top, then check
  for an unseeded random generator or a variable defined only in a deleted
  cell.
- **File not found:** run from the repository root, or follow the example's
  working-directory instruction.
- **Classroom not ready:** run `./classroom status` and see
  [troubleshooting](../docs/troubleshooting.md).
