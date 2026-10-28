# Day 1: Setup and REPL in the Docker Classroom

## How to run this lesson

From the repository root, start the prepared Docker classroom with `./classroom`.
Open `/classroom`, choose **Python and data science**, and select Day 1. Read the
Python capability notice and open the coding pad. Windows uses the same launcher
inside WSL 2. Follow the [one-command setup guide](../../../docs/one-command-classroom.md)
if Docker preparation is still needed. Ordinary study requires the Docker
classroom and a browser; host Python, virtual environments, VS Code, pip, and
Jupyter are not prerequisites.

The pad contains Python source from this notebook, with `# %%` comments marking
cells. Run submits the current program to a new worker process. With the prepared
notebook capability, cells share names inside that one submission and display a
cell's final expression. An ordinary program without cell markers uses normal
script behavior. Use `print` when output must be explicit in either form.

Read the examples here, then predict, Run, and inspect the output/result area.
Save edited source and notes in your Day 1 pad. Source and result records are
stored by the classroom; variables disappear when the process ends. Navigate
back to Day 1 to inspect saved text. The [classroom guide](../../../docs/classroom-experience.md)
explains results and saved work. Reading an old result does not execute it or
prove that your current source matches it.

The ten tasks use tiny offline standard-library programs and supplied reasoning
records. A reference run can verify values and exceptions. Only your own browser
observations can verify that you saved, navigated, and inspected your actual pad.
Keep those evidence types separate. Initial engine/image preparation can need a
connection; opening or running these already prepared examples needs no download.

## Level and prerequisites

**Level:** Beginner. **Stable ID:** `python-01`. **Direct prerequisites:** None.
You need no previous programming or terminal administration. You should be able
to open the prepared classroom and type into its pad. The supported Python
examples use 3.11-compatible syntax; inspect the capability notice for the
selected prepared runtime. Historical Day 1 is an ordering label, not a deadline.

- **Learner:** [Day 1 notebook](../notebooks/day01_setup_and_repl.ipynb).
- **Reference explanations:** [worked answers](../solutions/day01_setup_and_repl/day01_solutions.md).
- **Reference notebook:** [complete local examples](../solutions/day01_setup_and_repl/day01_solutions.ipynb).

## Learning objectives

Identify the interpreter that is executing your source, read a small program in
order, distinguish an explicit print from interactive display, and preserve a
recoverable source edit. Explain fresh-process variables versus stored source
and results. Inspect module availability without installing packages, use
runtime identity to diagnose an import complaint, and read a first error before
changing anything. Finally, describe how optional REPL and Jupyter state differs
from a browser Run without being required to install those tools.

## Vocabulary and concepts

- **Source:** The text of a program, such as `print("Hello")`. Saving that text
  preserves instructions for another execution. A result is what happened when
  one particular version of those instructions ran.
- **Interpreter:** The program that reads Python instructions and carries them
  out. `sys.executable` reports its executable path. A screen that merely says
  Python does not establish which environment supplied that interpreter.
- **Process:** One running instance of a program. Its names and temporary values
  live in memory. A new process starts without variables defined only in an old
  process, even when both processes read the same saved source.
- **Container:** An isolated environment for running processes with prepared
  tools and a filesystem view. The classroom's worker runs Python in a Linux
  container. A container is not the same thing as the Python process inside it.
- **Image:** Prepared container contents, including the selected interpreter and
  installed packages. Editing your pad does not edit or rebuild that image.
  The classroom stores learner source/results separately from prepared images.
- **Module and package:** A module is importable Python functionality. A package
  groups modules, and an installed distribution can supply one or more of them.
  The standard library comes with Python; third-party distributions need
  deliberate environment preparation. Day 1 imports only standard-library tools.
- **Virtual environment:** A Python interpreter/package environment used to
  separate dependencies. It is narrower than a container's filesystem/process
  boundary. A worker can contain a virtual environment internally, but that does
  not require you to create one on your host machine.
- **Working directory:** The process's base directory for relative file names.
  `Path.cwd()` reports it. It is neither a universal repository location nor
  proof of where the classroom stores saved pads. Do not depend on a particular
  developer's absolute path.
- **REPL:** Read-Evaluate-Print Loop, a live interactive interpreter prompt. It
  evaluates entries and can display expression results automatically. Names
  persist until that live process ends. `>>>` is the prompt, not Python source
  that should be copied into a browser program.
- **Kernel:** The live interpreter process connected to a Jupyter notebook.
  Ordinary cells in that kernel share memory. The course's optional contributor
  kernel is named Python (ds60sqlpy), but its friendly name alone does not prove
  the executable path. Browser Runs have a different fresh-process lifetime.

### Syntax anatomy before the first program

`print("Hello")` calls Python's built-in print function. The parentheses hold
its input; quotes make `Hello` a text value rather than a variable name. Leave
the quotes in place. `print("Total:", total)` supplies two inputs separated by
a comma, and print places a space between them. A line starting with `#` is a
comment for a reader. In the classroom pad, a standalone `# %%` is also a cell
boundary understood by the notebook execution adapter.

`price = 12` binds the name price to the integer twelve. One equals sign means
assignment, not a question about equality. Later `price * quantity` multiplies
the two current values. Names are case sensitive: `print` and `Print` are
different names. Python normally reads the submitted program from top to bottom,
so a name must be defined before it is used.

`import sys` makes the standard-library sys module available under that name.
The dot in `sys.executable` selects information provided by the module.
`from pathlib import Path` gives this program the name Path from the pathlib
module; `Path.cwd()` asks it for the current directory. These inspected values
can vary between processes and machines. Record actual output instead of
copying a path from a solution.

Some reference checks use `assert condition`. A true condition continues; a
false condition raises AssertionError. `==` compares values, whereas `=` assigns
a value. A small assertion checks a particular fact; it is not a completion
marker for all the manual browser tasks. A nonempty string counts as true in
an assertion; an empty string counts as false.

`True` and `False` are Boolean values for yes/no observations. `None` is a
special no-result value. A module specification describes where an interpreter
could find a module. In `importlib.util.find_spec("math") is not None`, the
function is asked to look for math, then `is not None` checks that it returned
a specification rather than the no-result value. This reads availability and
does not install a package.

## Worked example / walkthrough

### Ask the running interpreter for facts

Before running, predict which lines contain machine-dependent information.
Then use this complete program. It needs no third-party import and reads no
personal file. Its four labels make the observations easy to match to source.

```python
import platform
import sys
from pathlib import Path

print("Python:", platform.python_version())
print("Implementation:", platform.python_implementation())
print("Interpreter:", sys.executable)
print("Working directory:", Path.cwd())
```

**Expected:** Four labelled lines with a Python version, implementation name,
nonempty executable path, and current directory. The prepared version should
agree with the selected capability. A worker executable can be inside its own
prepared environment; it need not contain your host checkout's `.venv` path.
This is a real interpreter observation. It does not reveal an image digest,
the entire installed package list, or the browser's storage implementation.

### Separate calculation from visible presentation

Read each assignment in order and predict the two output lines. The first two
names hold integers; multiplication calculates a new total. The last lines ask
print to show the result and then a marker. They work both as notebook cells
and as an ordinary submitted script.

```python
price = 12
quantity = 3
total = price * quantity
print("Total:", total)
print("Ready")
```

**Expected:** `Total: 36` followed by `Ready`. Changing quantity to zero would
make the first line `Total: 0`, while the second line stays `Ready`. Merely
writing `total` as the final expression is an interactive display request in a
marked cell, but an ordinary script does not automatically print it. Keep
explicit print calls when comparing modes. There is no hidden previous value:
the program defines each required name before using it.

## Exercises

Attempt the following ten contracts in order. Save predictions and observations in notes. Manual browser steps and supplied-record reasoning are labelled explicitly.

### Exercise 1: Inspect the running Python

**Inputs:** The first worked example, using only platform, sys, and pathlib.

**Expected:** Print the Python version, implementation, executable, and current working directory with the four given labels. Record the actual values in notes. The executable and directory must be nonempty; do not require a host .venv path or claim the output identifies a Docker image digest.

**Verify:** Compare each labelled line with the corresponding expression in the source. Confirm the selected Python capability supports this lesson. If the version or interpreter is unexpected, preserve the observation and inspect the selected runtime before changing any installation.

**Hint:** A Python path inside a worker can differ from the checkout path on your computer.

### Exercise 2: Predict printed and last-expression output

**Inputs:** A marked cell containing print("before") followed by 7 * 6, and the same two lines submitted without a # %% marker.

**Expected:** Predict before running: the notebook-shaped marked cell prints before and displays the final value 42; the ordinary unmarked program prints only before. Replace the final expression with print(7 * 6) and observe 42 printed in either mode. Do not type the >>> prompt into the pad.

**Verify:** Keep the source and output for all three variants. Ignore variable Out[n] prompt numbers; compare the printed before, the displayed or printed 42, and the unmarked program with no 42. Explain which line asks for explicit printing.

**Hint:** The capability notice explains cell markers. A last expression and a print call are different requests.

### Exercise 3: Modify and save a source marker

**Inputs:** The source print("marker: red") in your own Day 1 pad.

**Expected:** Change red to amber, save the source, and Run to obtain exactly marker: amber. Navigate away and return to Day 1, then inspect that the saved source still says amber. Keep the result separate from the saved text. Do not edit the course image or other learners' work.

**Verify:** Record the new output and your manual observation of the returned pad. The reference can show the expected program text/output; only your browser observation establishes that your pad was saved. A past result saying amber alone does not prove the current source was saved.

**Hint:** A source edit changes what will run. The result is evidence from one earlier execution.

### Exercise 4: Observe two genuinely separate Runs

**Inputs:** Run A: visit = "north" then print(visit). Run B: replace the entire submitted source with only print(visit). Keep # %% if using the supplied notebook-cell variant.

**Expected:** Run A prints north. Run B fails with NameError for visit because it starts a new process; do not combine A and B into two cells of one Run. Repair B by defining visit = "south" before printing, then observe south. Save your source/notes so the experiment is recoverable.

**Verify:** Keep both separate result records and the repaired result. Identify the missing definition in B. If you use optional Jupyter, restart its kernel between A and B to reproduce this boundary, and explicitly note that its ordinary cells otherwise share state.

**Hint:** Removing a line from the submitted source is different from leaving the old line in an earlier cell.

Run A, as one complete submission:

```python
#%%
visit = "north"
print(visit)
```

Run B, replacing the entire submitted source. Its NameError is intentional:

```python
#%%
print(visit)
```

Repaired B, again as its own complete submission:

```python
#%%
visit = "south"
print(visit)
```

### Exercise 5: Inspect module availability without installing

**Inputs:** The standard-library importlib.util.find_spec function and the names math, numpy, and lesson_day01_package_that_does_not_exist.

**Expected:** Print whether each name has a discoverable module specification using is not None. math must be available; the intentionally absent lesson name is False in the prepared fixture. Record numpy's actual answer without importing or installing NumPy. If the supposedly absent name exists in a modified environment, record that exception to the fixture instead of deleting anything.

**Verify:** Keep the three labelled Boolean results and current interpreter identity. Explain that False means not discoverable by this interpreter, not absent from every computer. No pip command, download, or package mutation belongs in the attempt.

**Hint:** A discovery result describes the selected interpreter. It is not an installation request or a guarantee that every later import will succeed.

### Exercise 6: Diagnose supplied missing-package records

**Inputs:** Illustration A: runtime-A/python discovers numpy; runtime-B/python does not. Illustration B: two observations of runtime-C/python both fail to discover numpy. These are supplied neutral records, not measurements of your device.

**Expected:** For A, identify the different selected interpreter before proposing an environment repair. For B, identify a package missing from the selected runtime and consult its declared dependency/capability guidance. Write one sentence explaining why reinstalling blindly is unsupported by either record.

**Verify:** Label each answer supplied-record reasoning. Compare the A/B runtime identities and availability fields explicitly. Do not print invented paths as your own sys.executable or run host package administration.

**Hint:** The same word Python on two screens is weaker evidence than the actual interpreter identity.

### Exercise 7: Read and repair the first error

**Inputs:** A separate submission print(greeting), whose error says NameError: name 'greeting' is not defined.

**Expected:** Identify the error type, the missing name, and the source line. Repair the program by defining greeting = "Hello" before printing, yielding Hello. Also explain why Print("Hello") refers to a different, undefined name. Do not wrap the error in a broad handler just to hide it.

**Verify:** Keep the failed and repaired source/result pair. Confirm the repaired output is Hello and explain that case-sensitive spelling and definition order caused the two mistakes. A successful later Run does not erase the earlier evidence.

**Hint:** Read the final error line first, then find the matching source line; package installation cannot define a missing local name.

### Exercise 8: Separate image, process, and saved work

**Inputs:** Five items to classify: prepared Python/packages; visit = "north" while code runs; saved Day 1 source; an earlier Run's saved result; current working directory.

**Expected:** Classify them respectively as prepared image contents, process memory, stored pad text, stored execution evidence, and a process setting. Explain that saving source/results can survive a new Run while the variable does not. Changing a variable does not rebuild an image.

**Verify:** Write the five item/category pairs in notes. Mark this as an ownership model, not a live inspection of Docker storage. Use the real two-Run observation from task 4 as evidence only for process-variable isolation.

**Hint:** A working directory tells Python how to resolve relative paths. It does not name the browser's learning volume.

### Exercise 9: Repeat saved source and compare evidence

**Inputs:** The complete source count = 40; count = count + 2; print("repeat:", count), with one statement on each line.

**Expected:** Save and Run that source twice without editing it. Both program observations must be repeat: 42. Compare the selected source and result text; preserve both records. Do not rely on a value remembered from an earlier process or include variable timestamps in this comparison.

**Verify:** Record the two matching output lines and manually inspect that the same saved source produced them. This establishes repeatability of this tiny deterministic program; it does not prove every future program or dataset is reproducible.

**Hint:** The assignment resets count to forty in every new process before adding two.

### Exercise 10: Explain optional REPL and Jupyter identity

**Inputs:** Supplied optional-tool records: REPL uses illustration/venv-a/python, Jupyter uses illustration/venv-b/python, and both display Python 3.12. These records are examples, not paths on your machine.

**Expected:** Explain that matching language versions do not establish the same interpreter/package environment. A REPL and an ordinary Jupyter kernel each retain names within their live process; browser Runs begin fresh. State that these host tools are optional and use only the browser if they are unprepared.

**Verify:** Write a comparison of tool, interpreter identity, and state lifetime using the supplied records. If you later choose the contributor route, compare actual sys.executable values there rather than treating the sample paths as real. No kernel registration or venv creation is required by this exercise.

**Hint:** A friendly kernel display name is a selector label, not a measurement of the executable path.

## Self-check

Explain source, interpreter, and process using the first worked example. What
is preserved when you save the pad, and what disappears after Run completes?
Why can two tools display Python 3.12 but disagree about a package? What does a
working directory tell you, and what does it fail to establish about saved work?
Explain why pressing Run twice is different from running two cells in one Run.

**Verify:** Keep a real identity report, the two printed calculation lines,
marked/unmarked expression observations, the two-Run NameError and repair, and
two matching `repeat: 42` results. Add your manual saved-pad observation and
label the supplied-record answers as reasoning. Correct program output cannot
stand in for a save/navigation observation that you did not make.

## Common pitfalls

If you see NameError for Hello, check whether you omitted the quotes around a
text value. If NameError mentions greeting, locate its assignment above the
first use. If Print is undefined, fix the capital letter. If a line has an
unclosed quote or parenthesis, Python may report SyntaxError before any line
runs; compare the indicated punctuation with the small complete examples.
Package installation does not repair any of these source errors.

If nothing appears for `7 * 6`, inspect the source mode and use `print(7 * 6)`.
If a supposedly fresh test still knows visit, check whether Run A remains in
an earlier cell of the same submission or you are using a live Jupyter kernel.
Do not erase saved work to obtain fresh process memory. Replace only your own
submitted experiment source and keep a recoverable note of the earlier text.

If an import works in one tool and not another, compare the actual interpreter
and selected dependency profile first. Discovery is a read-only diagnostic,
not a package installation. A prepared image, a running Python variable, a saved
pad, and a saved result are distinct things; changing one does not imply the
others were changed or validated.

## Next step

Continue with [Day 2: variables and basic types](day02_basics_types.md).
If the initial Docker classroom is unavailable, use the
[one-command guide](../../../docs/one-command-classroom.md) to resolve that
setup boundary before interpreting Python source errors. Keep the current pad
and notes when navigating; course source and your editable pad are separate.

### Optional contributor REPL and Jupyter route

This subsection is optional. Ordinary learners can complete every task above
in the browser. If you deliberately want host contributor tools, follow
[CONTRIBUTING](../../../CONTRIBUTING.md) once to prepare its locked environment.
A host virtual environment does not install packages into Docker, and Docker's
packages do not automatically populate the host environment.

After that preparation, `uv run --no-sync python` opens its REPL from the
repository root. Type `import sys` and then `print(sys.executable)` to inspect
that live process; `exit()` leaves the REPL. A separately prepared notebook
workflow uses `uv run --no-sync python -m jupyter lab python/ds-60day/notebooks`
and the Python (ds60sqlpy) kernel. If registration is needed after moving the
prepared environment, the contributor guide describes `ipykernel` registration;
it is not part of Day 1's required practice. Compare actual executable paths
in those tools, and restart a kernel when testing fresh-state behavior.
Host notebook files and browser learning-volume pads are separate artifacts.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to tutor me through python-01: Setup and REPL in the Docker classroom.
Read python/ds-60day/companion-guides/day01_setup_and_repl.md and python/ds-60day/notebooks/day01_setup_and_repl.ipynb. Direct prerequisites: none. Start with no assumed programming knowledge and define each symbol before using it.
Emphasize source, interpreter/process identity, explicit print versus marked-cell display, working directory, package discovery without installation, containers versus virtual environments, and fresh Runs versus saved source/results. Explain one mechanism, ask me to predict, let me attempt, give one hint at a time, then review actual evidence and retrieval in my own words. Do not read solutions/ until I ask for comparison or have made an honest attempt.
Use the prepared offline Docker browser classroom. Host Python, venv, REPL, and Jupyter are optional contributor tools. Do not install packages, administer the host, change images, or claim to inspect my saved pad. No SQL, external service, or credentials are involved. Distinguish real interpreter/error output, supplied diagnostic examples, and manual save/navigation observations.
Done when all ten matching contracts have the appropriate observed or written evidence, and I can explain why a new Run forgets a variable while saved source/results can remain.
```
