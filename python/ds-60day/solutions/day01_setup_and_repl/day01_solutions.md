# Day 1: Explained Docker Classroom Answers

These references match the ten learner contracts. All executable snippets use
standard-library tools and can run in the prepared Python classroom. They do
not install packages or configure a host interpreter. A reference program can
prove its output and errors; it cannot inspect a learner's saved browser pad.
Manual observations below must be supplied by the learner. Illustrative paths
and diagnostic records are labelled and must never be reported as measurements
of the current device.

Use the [learner guide](../../companion-guides/day01_setup_and_repl.md) and
[learner notebook](../../notebooks/day01_setup_and_repl.ipynb) first. The
[reference notebook](day01_solutions.ipynb) keeps executable examples separate
from explanations. Its two-Run source strings are instructions for separate
submissions, not an attempt to imitate fresh process memory inside one kernel.

## Exercise 1: Inspect the running Python

**Inputs:** The first worked example, using only platform, sys, and pathlib.

**Expected:** Print the Python version, implementation, executable, and current working directory with the four given labels. Record the actual values in notes. The executable and directory must be nonempty; do not require a host .venv path or claim the output identifies a Docker image digest.

**Verify:** Compare each labelled line with the corresponding expression in the source. Confirm the selected Python capability supports this lesson. If the version or interpreter is unexpected, preserve the observation and inspect the selected runtime before changing any installation.

**Hint:** A Python path inside a worker can differ from the checkout path on your computer.

The identity program asks the currently running interpreter for its own facts. platform.python_version returns a version string, platform.python_implementation names the implementation, sys.executable gives an executable path, and Path.cwd gives the current working directory. The four labels connect each output to one expression. Record the actual strings instead of copying a reference path. A Docker worker can legitimately use an internal virtual environment whose path is unrelated to the host checkout. The assertions below check a nonempty executable, an absolute working directory, and the supported version family; they do not require a developer-specific prefix. These observations also have limits. They do not tell you which immutable image digest supplied the files, whether every optional package is installed, or where the browser stored its saved pad. If the selected runtime is unexpected, preserving these facts and reading its capability notice is a useful first diagnosis. Installing host Python would not change the interpreter already executing this browser submission.

```python
import platform
import sys
from pathlib import Path

print("Python:", platform.python_version())
print("Implementation:", platform.python_implementation())
print("Interpreter:", sys.executable)
print("Working directory:", Path.cwd())
assert sys.executable
assert Path.cwd().is_absolute()
```

## Exercise 2: Predict printed and last-expression output

**Inputs:** A marked cell containing print("before") followed by 7 * 6, and the same two lines submitted without a # %% marker.

**Expected:** Predict before running: the notebook-shaped marked cell prints before and displays the final value 42; the ordinary unmarked program prints only before. Replace the final expression with print(7 * 6) and observe 42 printed in either mode. Do not type the >>> prompt into the pad.

**Verify:** Keep the source and output for all three variants. Ignore variable Out[n] prompt numbers; compare the printed before, the displayed or printed 42, and the unmarked program with no 42. Explain which line asks for explicit printing.

**Hint:** The capability notice explains cell markers. A last expression and a print call are different requests.

The marked-cell form gives the execution adapter an interactive cell boundary. After printing before, its final expression evaluates to forty-two and the interactive display shows that value. The Out prompt's counter is presentation metadata, so it is not part of the arithmetic answer. An ordinary unmarked script also calculates forty-two, but calculation alone does not request printed output. Its only printed line is before. The portable answer below makes the printing request explicit and therefore produces before and 42 in both modes. This is why a missing displayed number is not automatically a failed calculation. Inspect the source form and the operation that produces visible output. In a terminal REPL, the >>> symbols belong to the tool; copying those symbols into the pad can cause SyntaxError. This reference demonstrates the explicit-print variant. The marked and unmarked variants should be compared as separate submissions so their display behavior is actual execution evidence rather than an imagined transcript.

```python
print("before")
print(7 * 6)
assert 7 * 6 == 42
```

## Exercise 3: Modify and save a source marker

**Inputs:** The source print("marker: red") in your own Day 1 pad.

**Expected:** Change red to amber, save the source, and Run to obtain exactly marker: amber. Navigate away and return to Day 1, then inspect that the saved source still says amber. Keep the result separate from the saved text. Do not edit the course image or other learners' work.

**Verify:** Record the new output and your manual observation of the returned pad. The reference can show the expected program text/output; only your browser observation establishes that your pad was saved. A past result saying amber alone does not prove the current source was saved.

**Hint:** A source edit changes what will run. The result is evidence from one earlier execution.

The program text print marker amber is the complete source change. The quotes make marker: amber a text value, and print produces the line in the result area. Changing only a note or a previously saved result does not change the submitted program. After saving, navigating away and returning gives a separate observation of whether the current pad retained the amber source. That step is deliberately manual: neither this reference notebook nor a successful print can inspect another pad's persistence. Keep the two facts separate in your evidence, such as program output observed and saved source inspected after return. If the output still says red, compare the current source with the source attached to that result before assuming a storage failure. You may be reading an earlier record. There is no reason to modify a worker image, create a host file, or install an editor for this task. The classroom already supplies the editing and saved-work route.

```python
print("marker: amber")
# Inspect the saved browser pad separately; this output does not prove storage.
```

## Exercise 4: Observe two genuinely separate Runs

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

Run A defines visit and prints north within one process. Run B deliberately omits that definition from its complete submitted source. A new browser Run starts a new process, so reading visit raises NameError. Two marked cells inside a single Run would share memory and would not be the same experiment. The repair adds a new definition before the print and therefore prints south. The reference stores all three short sources as strings so you can submit each one separately without intentionally breaking a full top-to-bottom reference notebook run. Those strings are source instructions, not evidence that three processes were already launched. Native qualification tests launch the sources in separate processes, while a learner should retain the three actual browser result records. In ordinary Jupyter, two cells usually share a live kernel, so restart that kernel between the first and second programs when comparing this boundary. Saving source does not preserve the old process variable; it preserves instructions that can define a new variable next time.

```python
run_a_source = '#%%\nvisit = "north"\nprint(visit)\n'
run_b_source = "#%%\nprint(visit)\n"
run_c_source = '#%%\nvisit = "south"\nprint(visit)\n'
print("Run A, B, and repaired B are separate submissions.")
print("Expected: north; then NameError for visit; then south.")
```

## Exercise 5: Inspect module availability without installing

**Inputs:** The standard-library importlib.util.find_spec function and the names math, numpy, and lesson_day01_package_that_does_not_exist.

**Expected:** Print whether each name has a discoverable module specification using is not None. math must be available; the intentionally absent lesson name is False in the prepared fixture. Record numpy's actual answer without importing or installing NumPy. If the supposedly absent name exists in a modified environment, record that exception to the fixture instead of deleting anything.

**Verify:** Keep the three labelled Boolean results and current interpreter identity. Explain that False means not discoverable by this interpreter, not absent from every computer. No pip command, download, or package mutation belongs in the attempt.

**Hint:** A discovery result describes the selected interpreter. It is not an installation request or a guarantee that every later import will succeed.

find_spec asks the selected interpreter whether a module can be discovered. Comparing its answer with None produces True when a specification exists and False otherwise. The math module belongs to the standard library and must be discoverable here. NumPy is a third-party distribution; this task reports its actual discovery status but never imports its numerical code or installs it. The long intentionally absent name is a negative fixture in the prepared environment. If a modified environment genuinely supplies that name, its observed presence should be recorded rather than treated as permission to delete it. Discovery is narrower than a successful import: an installed module could still fail later because of a broken dependency or initialization error. Conversely, absence here does not mean the package is absent from a different interpreter on the host. Keep the current interpreter identity beside the availability observations. This is read-only diagnosis, so no pip, network connection, or image rebuild is part of the answer.

```python
import importlib.util

print("math:", importlib.util.find_spec("math") is not None)
print("numpy:", importlib.util.find_spec("numpy") is not None)
print(
    "intentionally absent:",
    importlib.util.find_spec("lesson_day01_package_that_does_not_exist") is not None,
)
assert importlib.util.find_spec("math") is not None
assert importlib.util.find_spec("lesson_day01_package_that_does_not_exist") is None
```

## Exercise 6: Diagnose supplied missing-package records

**Inputs:** Illustration A: runtime-A/python discovers numpy; runtime-B/python does not. Illustration B: two observations of runtime-C/python both fail to discover numpy. These are supplied neutral records, not measurements of your device.

**Expected:** For A, identify the different selected interpreter before proposing an environment repair. For B, identify a package missing from the selected runtime and consult its declared dependency/capability guidance. Write one sentence explaining why reinstalling blindly is unsupported by either record.

**Verify:** Label each answer supplied-record reasoning. Compare the A/B runtime identities and availability fields explicitly. Do not print invented paths as your own sys.executable or run host package administration.

**Hint:** The same word Python on two screens is weaker evidence than the actual interpreter identity.

Illustration A compares different interpreter identities. A package found by runtime-A is not evidence that runtime-B has the same package search environment. The first useful action is to check which runtime was selected and whether it is the one intended for the lesson. Illustration B keeps the interpreter identity fixed and reports the package missing in both observations. That supports investigating the declared dependency profile for that runtime. It does not establish that the package is missing everywhere or that a network installation is authorized. Both answers must be labelled supplied-record reasoning because the example names were provided, not measured on the current machine. The short reference prints that distinction explicitly. Reinstalling blindly could alter a host environment that is not used by the browser at all, leaving the original complaint unchanged. A diagnosis should connect interpreter identity, declared package requirements, and observed discovery before choosing a repair. Day 1 itself remains usable because all required imports are standard-library modules.

```python
print("Supplied A: compare the different interpreter selections first.")
print("Supplied B: the package is missing from the selected runtime.")
print("These are supplied records, not a measurement of this device.")
```

## Exercise 7: Read and repair the first error

**Inputs:** A separate submission print(greeting), whose error says NameError: name 'greeting' is not defined.

**Expected:** Identify the error type, the missing name, and the source line. Repair the program by defining greeting = "Hello" before printing, yielding Hello. Also explain why Print("Hello") refers to a different, undefined name. Do not wrap the error in a broad handler just to hide it.

**Verify:** Keep the failed and repaired source/result pair. Confirm the repaired output is Hello and explain that case-sensitive spelling and definition order caused the two mistakes. A successful later Run does not erase the earlier evidence.

**Hint:** Read the final error line first, then find the matching source line; package installation cannot define a missing local name.

NameError says Python tried to read a name that has no binding at that point. In the supplied one-line program the missing name is greeting, and the indicated source line is the print call. Defining greeting before that call supplies the binding. The repaired program prints Hello, and its assertion checks that the stored text is exactly the expected value. Uppercase Print is a separate name because Python spelling is case sensitive; it is not another way to call the built-in print function. These are source-order and spelling problems, so package installation cannot fix them. Reading the last line of an error first gives the error category and message, then the associated source line points to the smallest useful investigation. Keep the failed source/result pair and the repaired pair rather than erasing the original observation. A broad handler that suppresses every error could make a result appear successful while printing nothing and leaving the actual defect unexplained.

```python
greeting = "Hello"
print(greeting)
assert greeting == "Hello"
```

## Exercise 8: Separate image, process, and saved work

**Inputs:** Five items to classify: prepared Python/packages; visit = "north" while code runs; saved Day 1 source; an earlier Run's saved result; current working directory.

**Expected:** Classify them respectively as prepared image contents, process memory, stored pad text, stored execution evidence, and a process setting. Explain that saving source/results can survive a new Run while the variable does not. Changing a variable does not rebuild an image.

**Verify:** Write the five item/category pairs in notes. Mark this as an ownership model, not a live inspection of Docker storage. Use the real two-Run observation from task 4 as evidence only for process-variable isolation.

**Hint:** A working directory tells Python how to resolve relative paths. It does not name the browser's learning volume.

The categories describe responsibilities rather than five interchangeable kinds of memory. Prepared Python and packages are supplied by the worker image. A variable such as visit exists in the running Python process and disappears with that process. Saved source is stored text that can be loaded for another run; a saved result is a record of an earlier execution. The current working directory is a setting used while resolving relative names. It does not tell you where the browser's learning volume is mounted or promise that a worker scratch file will remain next time. This is a stated ownership model, and the reference labels it that way instead of pretending to inspect Docker internals. Your actual two-Run experiment supplies direct evidence for the variable boundary, while your manual navigation supplies evidence for the saved-pad boundary. Editing a variable is not an image rebuild, and changing source after an execution does not rewrite the earlier result. Separating these layers makes later file, package, and debugging behavior easier to explain.

```python
print("Prepared Python/packages: image contents")
print("Live visit value: process memory")
print("Saved source: stored pad text")
print("Saved result: stored execution evidence")
print("Working directory: process setting")
print("This is the ownership model, not a Docker storage probe.")
```

## Exercise 9: Repeat saved source and compare evidence

**Inputs:** The complete source count = 40; count = count + 2; print("repeat:", count), with one statement on each line.

**Expected:** Save and Run that source twice without editing it. Both program observations must be repeat: 42. Compare the selected source and result text; preserve both records. Do not rely on a value remembered from an earlier process or include variable timestamps in this comparison.

**Verify:** Record the two matching output lines and manually inspect that the same saved source produced them. This establishes repeatability of this tiny deterministic program; it does not prove every future program or dataset is reproducible.

**Hint:** The assignment resets count to forty in every new process before adding two.

The saved program defines count as forty every time it starts. The next assignment calculates forty-two and rebinds count, then print emits repeat: 42. A second process repeats those same instructions from its own initial state, so it produces the same line. The program does not depend on a hidden count left over from the first run, a clock, a random value, a remote service, or a package installation. That is the relevant repeatability claim for this fixture. Two matching lines still need to be associated with the same submitted source; otherwise different programs could coincidentally print the same text. The reference assertion checks the arithmetic state in its own execution, while the learner's saved source and two result records supply the browser comparison. Reading an old result does not run it again. This tiny example is a starting point for reproducibility, not proof that any larger program with changing inputs or dependencies will produce identical results.

```python
count = 40
count = count + 2
print("repeat:", count)
assert count == 42
```

## Exercise 10: Explain optional REPL and Jupyter identity

**Inputs:** Supplied optional-tool records: REPL uses illustration/venv-a/python, Jupyter uses illustration/venv-b/python, and both display Python 3.12. These records are examples, not paths on your machine.

**Expected:** Explain that matching language versions do not establish the same interpreter/package environment. A REPL and an ordinary Jupyter kernel each retain names within their live process; browser Runs begin fresh. State that these host tools are optional and use only the browser if they are unprepared.

**Verify:** Write a comparison of tool, interpreter identity, and state lifetime using the supplied records. If you later choose the contributor route, compare actual sys.executable values there rather than treating the sample paths as real. No kernel registration or venv creation is required by this exercise.

**Hint:** A friendly kernel display name is a selector label, not a measurement of the executable path.

The optional records show two environment locations even though both tools report Python 3.12. A version identifies a language/runtime release family; it does not establish that both tools use the same executable and installed package environment. The supplied venv-a and venv-b names are illustrations and must not be copied into a current-device report. A live REPL keeps names between entries, and an ordinary Jupyter kernel keeps names between cells until its process is restarted. The Docker browser instead submits each Run to a fresh process, while notebook-shaped cells share names only within that submission. These differences explain why a name can remain available in one tool but fail in a new browser Run. Nothing in this answer requires creating a host virtual environment or registering a kernel. If the learner later chooses contributor tooling, actual sys.executable observations there provide the comparison, and the contributor guide owns any optional setup. A friendly kernel label by itself is not sufficient interpreter evidence.

```python
print("Supplied REPL interpreter: illustration/venv-a/python")
print("Supplied Jupyter interpreter: illustration/venv-b/python")
print("Same version does not prove the same package environment.")
print("Optional live kernels retain state; browser Runs start fresh.")
```

The optional host REPL/Jupyter commands remain in the contributor section of the guide. They are not a required repair for a working Docker classroom. Keep source, observed results, and manual browser evidence distinct when comparing your attempt.
