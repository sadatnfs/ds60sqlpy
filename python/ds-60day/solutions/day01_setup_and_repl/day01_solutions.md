# Day 1 Solutions: Python Setup and the REPL

These references match the ten learner exercises. Every snippet uses only
Python's standard library and runs in the prepared classroom without
installing anything. A reference program can show output and errors; it cannot
inspect your saved browser pad, so the saving and fresh-Run tasks also need
your own observations. Paths and records that are supplied as examples are
labelled and are never measurements of the current device.

Use the [learner guide](../../companion-guides/day01_setup_and_repl.md) and
[learner notebook](../../notebooks/day01_setup_and_repl.ipynb) first. The
[reference notebook](day01_solutions.ipynb) holds the same executable answers.
Its source strings for separate Runs are instructions to submit one at a time,
not an imitation of fresh process memory inside one notebook.

## Exercise 1: Change a calculation and predict the total

**Inputs:** Worked example 2 with `quantity = 5` and a new line `tax = 4`.

**Expected:** Compute `total_with_tax = price * quantity + tax` and print `Total with tax: 64`. Python multiplies before it adds, so the value is `12 * 5 + 4`, not `12 * (5 + 4)`.

**Verify:** Write your predicted output as a comment before running, then add `assert total_with_tax == 64`. Change `quantity` to `0`, predict `Total with tax: 4`, and rerun.

**Hint:** Evaluate the right-hand side in your head with the current values, multiplication first.

The right-hand side is evaluated with the current values: `12 * 5` is 60,
and adding `tax` gives 64. Multiplication happens before addition, exactly as
in ordinary arithmetic, so no parentheses are needed; writing
`price * (quantity + tax)` would instead compute `12 * 9`, which is 108. The
assertion turns the prediction into a check that stops the program if the
value is wrong. With `quantity = 0` the product is 0 and only the tax remains,
so the line reads `Total with tax: 4`. The most common slip is changing the
number in the `print` line instead of the assignment: the output must come
from the calculation, not from typed text.

```python
price = 12
quantity = 5
tax = 4
total_with_tax = price * quantity + tax
print("Total with tax:", total_with_tax)
assert total_with_tax == 64
```

## Exercise 2: Predict printed and last-expression output

**Inputs:** A cell containing `# %%`, `print("before")`, and `7 * 6` on separate lines; then the same two lines without the `# %%` marker.

**Expected:** The marked cell prints `before` and then displays `42`. The unmarked program prints only `before`: it calculates 42, but nothing asks to show it. Replacing `7 * 6` with `print(7 * 6)` prints `42` in both forms.

**Verify:** Keep the output of all three versions and point to the line that produced each visible `42`. Ignore any `Out[n]` counter; it is a display label, not part of the result.

**Hint:** Calculating a value and printing it are different requests. Do not type the `>>>` prompt from an interactive session into the pad.

The `# %%` marker tells the classroom to run the pad as notebook cells, and a
notebook cell displays the value of its last expression. That is why the marked
version shows 42 after printing `before`. An ordinary program has no such
display step: Python still calculates `7 * 6`, but the value is discarded
because nothing asks to show it. `print(7 * 6)` is an explicit request, so it
works in both forms. A missing number is therefore not a failed calculation;
check whether the line was a bare expression or a `print` call. Copying `>>>`
from an interactive prompt into the pad causes a `SyntaxError`, because the
prompt belongs to the tool, not to the program.

```python
print("before")
print(7 * 6)
assert 7 * 6 == 42
```

## Exercise 3: Modify and save a source marker

**Inputs:** The line `print("marker: red")` in your own Day 1 pad.

**Expected:** Change `red` to `amber`, save, and Run to see exactly `marker: amber`. Navigate to another lesson and back to Day 1, then check that the saved source still says `amber`.

**Verify:** Record the output and what you saw after returning. The output proves what one Run printed; only looking at the returned pad proves that the source was saved.

**Hint:** Editing the source changes what the next Run executes. An old result does not change when you edit.

The complete source change is one word inside the quotes. The output line
`marker: amber` proves what that Run printed, but it cannot prove that the
edit was saved: you could have run unsaved text. Navigating away and back is a
separate observation of the saved pad, which is why the task asks for both.
If the output still says `red`, compare the current source with the source
attached to that result before assuming that saving failed; you may be reading
an earlier result. Nothing about this task needs a host file, an installed
editor, or a change to the classroom image.

```python
print("marker: amber")
# Look at the saved browser pad separately; this output does not prove storage.
```

## Exercise 4: Observe two genuinely separate Runs

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

Run A defines `visit` and prints `north` inside one process. Run B's complete
source never assigns `visit`, and a new Run starts a new process, so reading
the name raises `NameError`. Two cells in the same Run would share names and
hide this boundary, which is why the sources must be submitted separately.
The repair adds an assignment before the print and therefore prints `south`.
The reference keeps the three sources as strings so that this notebook can
still run from top to bottom; they are instructions to submit, not evidence
that three processes ran. In optional Jupyter, cells share a live kernel, so
restart the kernel between the first and second programs to see the same
`NameError`.

```python
run_a_source = '#%%\nvisit = "north"\nprint(visit)\n'
run_b_source = "#%%\nprint(visit)\n"
run_c_source = '#%%\nvisit = "south"\nprint(visit)\n'
print("Run A, B, and repaired B are separate submissions.")
print("Expected: north; then NameError for visit; then south.")
```

## Exercise 5: Read a SyntaxError before anything runs

**Inputs:** Program A: `print("first")` then `print("Hello)`, whose closing quote is missing. Program B: `print("Hello"`, whose closing parenthesis is missing. Submit each without `# %%` markers.

**Expected:** Program A prints nothing and reports `SyntaxError: unterminated string literal (detected at line 2)`; Program B reports `SyntaxError: '(' was never closed`. Python checks the whole program's grammar before running any line, so even the correct `print("first")` does not run. Repair both to see `first` and `Hello`.

**Verify:** Record each error's last line and the line number it names. Then add a `# %%` line above `print("Hello)` and Run again: now `first` prints before the error, because each marked cell is checked separately.

**Hint:** The caret (`^`) under the source line shows where Python noticed the problem; the real mistake can be just before it.

Before an ordinary program runs, Python reads the whole file and checks its
grammar. An unclosed quote or parenthesis makes that check fail, so nothing
runs, not even the correct first line. That is the difference from the
`NameError` in the seventh task, which happens only when Python reaches the
bad line and after earlier lines have printed. Marked cells are checked one at
a time, which is why adding `# %%` lets `first` print before the error. Read
the last line of the report first: it names the problem (an unterminated
string or a parenthesis that was never closed), and the line number points to
where Python noticed it. The fix is always in the source text; nothing needs
to be installed.

```python
program_a = 'print("first")\nprint("Hello)\n'
program_b = 'print("Hello"\n'
repaired = 'print("first")\nprint("Hello")\n'
print("Submit each program as its own Run, without # %% markers.")
print("Expected A: no output, then SyntaxError: unterminated string literal (detected at line 2)")
print("Expected B: SyntaxError: '(' was never closed")
print("Expected repaired: first, then Hello")
```

## Exercise 6: Check what this interpreter can import

**Inputs:** `importlib.util.find_spec`, the module names `math` and `lesson_day01_package_that_does_not_exist`, and a supplied record: two tools both display Python 3.12, but only the one at `illustration/venv-a/python` can import `numpy`.

**Expected:** Print `math: True` and `intentionally absent: False` using `importlib.util.find_spec(name) is not None`. Explain in one sentence why the supplied record shows that a matching version number does not mean the same set of packages.

**Verify:** Keep the two printed lines. Label the record answer as reasoning about supplied examples, not a measurement of your device. Install nothing: `find_spec` only looks.

**Hint:** Each interpreter searches its own installed packages. Compare interpreter paths, not just version numbers.

`find_spec` asks the running interpreter whether it can find a module, and
returns `None` when it cannot, so `is not None` turns the answer into `True` or
`False`. `math` is part of the standard library and is always found; the long
invented name is not installed anywhere, so it prints `False`. Looking is not
installing: no network or package change happens. In the supplied record, two
tools report the same Python version, yet each interpreter has its own set of
installed packages, so only one of them can import `numpy`. When an import
works in one tool and fails in another, compare which interpreter each tool
runs before changing any installation. The printed record below is supplied
reasoning, not an observation of the machine running it.

```python
import importlib.util

print("math:", importlib.util.find_spec("math") is not None)
print(
    "intentionally absent:",
    importlib.util.find_spec("lesson_day01_package_that_does_not_exist") is not None,
)
assert importlib.util.find_spec("math") is not None
print("Supplied record: venv-a and venv-b both display Python 3.12; only venv-a has numpy.")
print("These are supplied records, not a measurement of this device.")
```

## Exercise 7: Read and repair the first error

**Inputs:** A separate submission `print(greeting)`, whose error ends with `NameError: name 'greeting' is not defined`.

**Expected:** Identify the error type, the missing name, and the line. Repair the program by assigning `greeting = "Hello"` before the print, which outputs `Hello`. Also explain why `Print("Hello")` fails with `NameError: name 'Print' is not defined`.

**Verify:** Keep the failing and repaired versions and their output. The repaired output must be exactly `Hello`. Explain that definition order caused the first error and capitalization the second.

**Hint:** Read the last line of the traceback first, then find that line in your source. Installing anything cannot define a missing name.

The last line of the traceback names the error type (`NameError`) and the
missing name (`greeting`); the line above it shows where Python was when it
failed. Python looks a name up when the line runs, and nothing had bound
`greeting` yet. Assigning it on an earlier line repairs the program, which then
prints `Hello`. `Print("Hello")` fails for a different reason: names are case
sensitive, and `Print` with a capital P was never defined. Wrapping the error in
a handler to hide it would leave the real mistake in place, and installing a
package cannot define a name that belongs in your own source.

```python
greeting = "Hello"
print(greeting)
assert greeting == "Hello"
```

## Exercise 8: Use quotes and comments correctly

**Inputs:** The line `print(Hello)` and the line `# print("Hello")`.

**Expected:** `print(Hello)` stops with `NameError: name 'Hello' is not defined`, because without quotes `Hello` is a name. Adding quotes, `print("Hello")`, prints `Hello`. The second line prints nothing: everything after `#` is a comment.

**Verify:** Write a two-line program whose first line is a comment describing the second, and whose second line prints exactly `Hello, Day 1`. Run it and confirm exactly one output line.

**Hint:** Quotes mark text; `#` marks a note for readers.

Quotes decide whether a word is text or a name. `"Hello"` is a string value,
so `print` can show it; `Hello` without quotes asks Python to look up a name
that was never assigned, which raises `NameError`. A `#` starts a comment, and
Python ignores everything from the `#` to the end of the line, so commenting
out a line is a quick way to stop it from running without deleting it. A good
comment says why a line exists or what it should produce; the program below
prints exactly one line because the first line is only a note.

```python
# Python skips this comment; the next line prints the greeting.
print("Hello, Day 1")
```

## Exercise 9: Reassign a name and rerun the same source

**Inputs:** The program `count = 40`, `count = count + 2`, and `print("repeat:", count)`, one statement per line.

**Expected:** Predict `repeat: 42`: the second line reads the current value 40, adds 2, and rebinds `count` to 42. Save and Run the unchanged source twice; both Runs print `repeat: 42`.

**Verify:** Record both outputs. Explain why the second Run does not print `repeat: 44`: each Run is a new process, so `count` starts again at 40.

**Hint:** `count = count + 2` is not an equation; Python evaluates the right side first, then rebinds the name.

`count = count + 2` reads the current value of `count` (40), adds 2, and then
binds the name to the new value 42; the old value is not changed in place, the
name simply refers to a different number. Running the unchanged source again
starts a new process, so the first line sets `count` back to 40 and the result
is again 42, never 44. Two matching outputs show that this small program is
repeatable; they do not prove that every future program is, especially one
that reads the clock, random numbers, or files that change.

```python
count = 40
count = count + 2
print("repeat:", count)
assert count == 42
```

## Exercise 10: Print several values on one line

**Inputs:** `name = "Ada"` and `day = 1`.

**Expected:** `print("Learner:", name, "Day:", day)` prints `Learner: Ada Day: 1`, and `print(name, day, sep=" | ")` prints `Ada | 1`. Predict both lines, including every space, before running.

**Verify:** Keep the two output lines. Then run `print("Day:" + day)` once and record its last line, `TypeError: can only concatenate str (not "int") to str`, because `+` cannot join text and a number. Day 2 shows how to convert between them.

**Hint:** Commas give `print` separate arguments; `sep` replaces the space that `print` puts between them.

`print` accepts any number of arguments separated by commas, converts each to
text, and writes them with one space between them, so numbers and strings can
be mixed freely. `sep=" | "` is a keyword argument that replaces that space
with another separator. Joining with `+` is different: `+` between two strings
combines them, but between a string and an integer it has no meaning, so Python
raises `TypeError` instead of guessing. Day 2 converts the number with
`str(day)` when a single joined string is really needed.

```python
name = "Ada"
day = 1
print("Learner:", name, "Day:", day)
print(name, day, sep=" | ")
```
