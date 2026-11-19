# Day 1: Python Setup and the REPL

## How to run this lesson

Start the classroom from the repository root with `./classroom`, open
`/classroom`, choose **Python and data science**, and select Day 1. Windows
uses the same command inside WSL 2, and the
[one-command setup guide](../../../docs/one-command-classroom.md) covers Docker
preparation. Ordinary study requires the Docker classroom and a browser;
host Python, virtual environments, VS Code, pip, and
Jupyter are not prerequisites.

Day 1 opens a coding pad that already contains this lesson's examples. Type or
edit Python in the pad, press **Run**, and read the output panel. A line that
contains only `# %%` starts a new cell: names defined in an earlier cell are
available to later cells of the same Run, and each cell displays the value of
its last line. Every Run starts a fresh Python process, so names from an
earlier Run are gone, while your saved source stays in the pad. The
[classroom guide](../../../docs/classroom-experience.md) explains saving and
past results. Every Day 1 example works offline with Python's standard library.

## Level and prerequisites

**Level:** Beginner. **Stable ID:** `python-01`. **Direct prerequisites:** None.
You need no previous programming experience: you only need to open the
classroom and type into its pad. The examples use Python 3.11-compatible
syntax. Historical Day 1 is an ordering label, not a deadline.

- **Learner:** [Day 1 notebook](../notebooks/day01_setup_and_repl.ipynb).
- **Reference explanations:** [worked answers](../solutions/day01_setup_and_repl/day01_solutions.md).
- **Reference notebook:** [complete local examples](../solutions/day01_setup_and_repl/day01_solutions.ipynb).

## Learning objectives

By the end of this lesson, you can:

- write and run a short program that prints text and calculated values;
- bind names with `=` and predict the value a calculation produces;
- tell an explicit `print` from the display of a cell's last expression;
- read the last line of a `NameError` or `SyntaxError` and repair the source;
- use quotes and comments correctly; and
- explain why a new Run forgets names while your saved source remains.

## Your first two programs

### Worked example 1: Print a line of text

Predict the output before you press Run.

```python
print("Python reads source text.")
```

**Expected:** `Python reads source text.` The quotes make a text value, called a
string, and `print` shows it without the quotes. Delete the closing quote and
run again: Python stops with `SyntaxError: unterminated string literal`, which
Exercise 5 explores.

### Worked example 2: Name values, calculate, then print

Read each line in order and predict both output lines.

```python
price = 12
quantity = 3
total = price * quantity
print("Total:", total)
print("Ready")
```

**Expected:** `Total: 36` followed by `Ready`. The first three lines print
nothing: they bind names to values. `print` separates its two inputs with one
space. Change `quantity` to `0` and predict again: the first line becomes
`Total: 0`, and `Ready` does not change.

## Vocabulary and mental model

- **Program (source):** the text you write, such as `print("Hello")`. Python runs
  a program one statement at a time, from top to bottom.
- **Statement:** one complete instruction, usually one line, such as
  `total = price * quantity`.
- **Value:** a piece of data, such as the integer `12` or the string `"Ready"`.
- **String:** a text value written between quotes. Without the quotes, Python
  reads the word as a name instead of as text.
- **Name (variable):** a label that refers to a value. `price = 12` means "let
  `price` refer to 12"; it does not ask whether they are equal.
- **Expression:** code that produces a value, such as `price * quantity` or
  `7 * 6`.
- **Function call:** a name followed by parentheses, such as `print(...)`. The
  values inside the parentheses are its inputs, called arguments.
- **Comment:** text after `#` on a line. Python ignores it; it explains the code
  to a reader.
- **Exception and traceback:** when Python cannot continue, it raises an
  exception and prints a traceback. Read the last line first: it names the
  error type and gives a message.

### Syntax anatomy

`print("Total:", total)` calls `print` with two arguments separated by a comma.
The first is a string; the second is a name, so Python looks up its current
value. `print` writes both on one line with a space between them.

`total = price * quantity` is an assignment. Python first evaluates the
right-hand side using the current values of `price` and `quantity`, then binds
the name on the left to the result. One `=` assigns; two (`==`) compare and
produce `True` or `False`. Names are case sensitive, so `print` and `Print` are
different names, and a name must be assigned before a later line uses it.

A cell's last line can be an expression such as `7 * 6`. In a cell marked with
`# %%`, the classroom displays that value, much as an interactive prompt would.
An ordinary program without markers calculates the value but does not show it;
only `print` writes output in both forms.

Some exercises check a fact with `assert condition`. A true condition lets the
program continue; a false one stops it with `AssertionError`. `True` and
`False` are the two Boolean values, and `None` means "no value".

## How the classroom runs your code

When you press Run, the classroom sends the pad's source to a fresh Python
**process** (one running copy of the Python **interpreter**, the program that
executes Python) inside a prepared worker. The process runs your source,
returns its output, and exits. Its names disappear with it; your saved source
and the record of the result stay in the classroom. Python also has a
**working directory**, the folder it uses to resolve relative file names.

### Worked example 3: Ask the running interpreter about itself

`import` makes a standard-library module available by name; it never installs
anything. Predict which of the four lines depend on the machine.

```python
import platform
import sys
from pathlib import Path

print("Python:", platform.python_version())
print("Implementation:", platform.python_implementation())
print("Interpreter:", sys.executable)
print("Working directory:", Path.cwd())
```

**Expected:** four labelled lines, such as `Python: 3.12.x` and
`Implementation: CPython`. The interpreter path and working directory belong to
the worker, not to your computer, so record what you actually see instead of
copying a path from elsewhere. This report identifies the running Python; it
does not list installed packages or show where the classroom stores your pad.

## Exercises

Work through the ten tasks in order. Before running anything, write your
prediction in the pad as a comment. Tasks 3 and 4 also ask for something you
observe in the browser, such as the saved pad after you return to it; record
those observations in your notes.

### Exercise 1: Change a calculation and predict the total

**Inputs:** Worked example 2 with `quantity = 5` and a new line `tax = 4`.

**Expected:** Compute `total_with_tax = price * quantity + tax` and print `Total with tax: 64`. Python multiplies before it adds, so the value is `12 * 5 + 4`, not `12 * (5 + 4)`.

**Verify:** Write your predicted output as a comment before running, then add `assert total_with_tax == 64`. Change `quantity` to `0`, predict `Total with tax: 4`, and rerun.

**Hint:** Evaluate the right-hand side in your head with the current values, multiplication first.

### Exercise 2: Predict printed and last-expression output

**Inputs:** A cell containing `# %%`, `print("before")`, and `7 * 6` on separate lines; then the same two lines without the `# %%` marker.

**Expected:** The marked cell prints `before` and then displays `42`. The unmarked program prints only `before`: it calculates 42, but nothing asks to show it. Replacing `7 * 6` with `print(7 * 6)` prints `42` in both forms.

**Verify:** Keep the output of all three versions and point to the line that produced each visible `42`. Ignore any `Out[n]` counter; it is a display label, not part of the result.

**Hint:** Calculating a value and printing it are different requests. Do not type the `>>>` prompt from an interactive session into the pad.

### Exercise 3: Modify and save a source marker

**Inputs:** The line `print("marker: red")` in your own Day 1 pad.

**Expected:** Change `red` to `amber`, save, and Run to see exactly `marker: amber`. Navigate to another lesson and back to Day 1, then check that the saved source still says `amber`.

**Verify:** Record the output and what you saw after returning. The output proves what one Run printed; only looking at the returned pad proves that the source was saved.

**Hint:** Editing the source changes what the next Run executes. An old result does not change when you edit.

### Exercise 4: Observe two genuinely separate Runs

**Inputs:** Run A: `visit = "north"` followed by `print(visit)`. Run B: replace the whole pad with only `print(visit)`.

**Expected:** Run A prints `north`. Run B stops with `NameError: name 'visit' is not defined`, because every Run starts a new process with no names. Repair B by adding `visit = "south"` before the print and Run again to see `south`.

**Verify:** Keep all three results and name the line that is missing from B. Two cells inside one Run would share names, so do not test this with two cells of the same Run.

**Hint:** Saving source keeps instructions, not the values a previous process held.

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

### Exercise 5: Read a SyntaxError before anything runs

**Inputs:** Program A: `print("first")` then `print("Hello)`, whose closing quote is missing. Program B: `print("Hello"`, whose closing parenthesis is missing. Submit each without `# %%` markers.

**Expected:** Program A prints nothing and reports `SyntaxError: unterminated string literal (detected at line 2)`; Program B reports `SyntaxError: '(' was never closed`. Python checks the whole program's grammar before running any line, so even the correct `print("first")` does not run. Repair both to see `first` and `Hello`.

**Verify:** Record each error's last line and the line number it names. Then add a `# %%` line above `print("Hello)` and Run again: now `first` prints before the error, because each marked cell is checked separately.

**Hint:** The caret (`^`) under the source line shows where Python noticed the problem; the real mistake can be just before it.

### Exercise 6: Check what this interpreter can import

**Inputs:** `importlib.util.find_spec`, the module names `math` and `lesson_day01_package_that_does_not_exist`, and a supplied record: two tools both display Python 3.12, but only the one at `illustration/venv-a/python` can import `numpy`.

**Expected:** Print `math: True` and `intentionally absent: False` using `importlib.util.find_spec(name) is not None`. Explain in one sentence why the supplied record shows that a matching version number does not mean the same set of packages.

**Verify:** Keep the two printed lines. Label the record answer as reasoning about supplied examples, not a measurement of your device. Install nothing: `find_spec` only looks.

**Hint:** Each interpreter searches its own installed packages. Compare interpreter paths, not just version numbers.

### Exercise 7: Read and repair the first error

**Inputs:** A separate submission `print(greeting)`, whose error ends with `NameError: name 'greeting' is not defined`.

**Expected:** Identify the error type, the missing name, and the line. Repair the program by assigning `greeting = "Hello"` before the print, which outputs `Hello`. Also explain why `Print("Hello")` fails with `NameError: name 'Print' is not defined`.

**Verify:** Keep the failing and repaired versions and their output. The repaired output must be exactly `Hello`. Explain that definition order caused the first error and capitalization the second.

**Hint:** Read the last line of the traceback first, then find that line in your source. Installing anything cannot define a missing name.

### Exercise 8: Use quotes and comments correctly

**Inputs:** The line `print(Hello)` and the line `# print("Hello")`.

**Expected:** `print(Hello)` stops with `NameError: name 'Hello' is not defined`, because without quotes `Hello` is a name. Adding quotes, `print("Hello")`, prints `Hello`. The second line prints nothing: everything after `#` is a comment.

**Verify:** Write a two-line program whose first line is a comment describing the second, and whose second line prints exactly `Hello, Day 1`. Run it and confirm exactly one output line.

**Hint:** Quotes mark text; `#` marks a note for readers.

### Exercise 9: Reassign a name and rerun the same source

**Inputs:** The program `count = 40`, `count = count + 2`, and `print("repeat:", count)`, one statement per line.

**Expected:** Predict `repeat: 42`: the second line reads the current value 40, adds 2, and rebinds `count` to 42. Save and Run the unchanged source twice; both Runs print `repeat: 42`.

**Verify:** Record both outputs. Explain why the second Run does not print `repeat: 44`: each Run is a new process, so `count` starts again at 40.

**Hint:** `count = count + 2` is not an equation; Python evaluates the right side first, then rebinds the name.

### Exercise 10: Print several values on one line

**Inputs:** `name = "Ada"` and `day = 1`.

**Expected:** `print("Learner:", name, "Day:", day)` prints `Learner: Ada Day: 1`, and `print(name, day, sep=" | ")` prints `Ada | 1`. Predict both lines, including every space, before running.

**Verify:** Keep the two output lines. Then run `print("Day:" + day)` once and record its last line, `TypeError: can only concatenate str (not "int") to str`, because `+` cannot join text and a number. Day 2 shows how to convert between them.

**Hint:** Commas give `print` separate arguments; `sep` replaces the space that `print` puts between them.

## Self-check

Without looking back, explain why `price = 12` prints nothing while
`print("Total:", total)` prints a line. What does a cell's last expression show
in a marked cell, and what happens to it in an ordinary program? Why does a
`SyntaxError` stop a program before its first line runs, while a `NameError`
happens only when the bad line is reached? What does your pad keep after a Run
finishes, and what disappears?

**Verify:** Keep the identity report from worked example 3, the `Total: 36` and
`Ready` lines, the marked and unmarked `7 * 6` results, the `NameError` and its
repair, both `repeat: 42` results, and your note about the saved `amber` pad.

## Common pitfalls

- **`NameError: name 'Hello' is not defined`:** the quotes around a text value
  are missing, so Python looked for a name.
- **`NameError` for a name you did assign:** the assignment is below the line
  that uses it, or it was in an earlier Run. Move it above the use, in the same
  Run.
- **`NameError: name 'Print' is not defined`:** Python is case sensitive; write
  `print`.
- **`SyntaxError`:** a quote or parenthesis is unclosed, or `>>>` was copied
  into the pad. Look at the caret and at the character just before it.
- **Nothing appears for `7 * 6`:** the program has no `# %%` marker, or the
  expression is not the last line of its cell. Use `print(7 * 6)`.
- **A supposedly fresh Run still knows a name:** the defining line is still in
  an earlier cell of the same Run.

Installing packages repairs none of these errors: each one is in the source.

## Next step

Continue with [Day 2: Variables and Core Types](day02_basics_types.md). If the
classroom does not start, use the
[one-command guide](../../../docs/one-command-classroom.md) before reading
Python errors; a setup problem and a source error need different fixes.

### Optional contributor REPL and Jupyter route

This subsection is optional; ordinary learners complete every task above in
the browser. A few terms help when you read other documentation:

- **REPL:** Read-Evaluate-Print Loop, an interactive prompt (`>>>`) that runs
  one entry at a time and keeps names until you leave it.
- **Kernel:** the live Python process behind a Jupyter notebook. Its cells share
  names until the kernel restarts, unlike browser Runs.
- **Virtual environment:** a separate set of installed packages for one Python
  interpreter. The classroom worker has its own; you do not create one on your
  computer.
- **Container and image:** the classroom runs Python in a Linux container
  started from a prepared image that already contains Python and its packages.
  Editing your pad never changes the image.

If you want host contributor tools, follow [CONTRIBUTING](../../../CONTRIBUTING.md)
once to prepare its locked environment. A host environment does not install
packages into Docker, and Docker's packages do not appear on the host. After
that preparation, `uv run --no-sync python` opens a REPL from the repository
root. Type `import sys` and then `print(sys.executable)` to see which
interpreter is running, and `exit()` to leave. A separately prepared notebook
workflow uses `uv run --no-sync python -m jupyter lab python/ds-60day/notebooks`
and the Python (ds60sqlpy) kernel; restart the kernel when you want fresh
names. Host notebook files and browser pads are separate copies of your work.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to tutor me through python-01: Python Setup and the REPL.
Read python/ds-60day/companion-guides/day01_setup_and_repl.md and python/ds-60day/notebooks/day01_setup_and_repl.ipynb. Direct prerequisites: none. Start with no assumed programming knowledge and define each symbol before using it.
Emphasize print, strings and quotes, assignment and names, expressions, comments, reading NameError and SyntaxError, print versus a cell's displayed last expression, and why a new Run forgets names while saved source remains. Explain one mechanism, ask me to predict, let me attempt, give one hint at a time, then review my actual output as evidence and check retrieval in my own words. Do not read solutions/ until I ask for comparison or have made an honest attempt.
Use the prepared offline Docker browser classroom. Host Python, venv, REPL, and Jupyter are optional contributor tools. Do not install packages, administer the host, change images, or claim to inspect my saved pad. No SQL, external service, or credentials are involved.
Done when I have completed the ten exercises with their output or written observations, and I can explain in my own words why a new Run forgets a variable while saved source remains.
```
