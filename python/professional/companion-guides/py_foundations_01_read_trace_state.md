# Read a Program, Trace Its State, and Predict Its Output

**Stable ID:** `python-foundations-01`

**Estimated time:** 120 minutes, split across sessions as needed.

## Level and prerequisites

Foundation. Direct catalog prerequisites: `python-01`.

You only need to open a Python file, run the course interpreter, and find its terminal output. This module introduces names, assignment, strings, numbers, and prediction before Day 2 adds more types. You do not need loops, functions, or a notebook.

## Learning objectives

- Distinguish source text, a running program, and terminal output.
- Trace the value attached to each name after every executed line.
- Separate a number from text that displays the same digits.
- Use tiny predictions and fresh runs to diagnose state mistakes.

## How to run this lesson

**Primary browser route:** run `./classroom` from the repository root and
choose **Python** on `/classroom`. Open this lesson in the shared workspace,
read its capability notice, and use its supported coding or reading workflow.
The [classroom guide](../../../docs/classroom-experience.md) explains saved work, runtimes and switching subjects.

**Optional native notebook/editor route:** the instructions below describe
separately prepared host tools. They are useful alternatives, not prerequisites
for opening this lesson in the Docker classroom.

Use the repository folder in VS Code. The rendered lesson page is a preview;
edit the actual [learner script](../lessons/py_foundations_01_read_trace_state.py). Copy it to an ignored
folder under `.learning/` first if you want to keep your attempt across course
updates. Use the interpreter from setup. These examples need only Python's
standard library, have no network calls, and use the same inputs on each run.

Windows PowerShell:

```powershell
$CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
    (Resolve-Path .\.venv\Scripts\python.exe).Path
} else {
    (Resolve-Path .\.venv\python.exe).Path
}
& $CoursePython python\professional\lessons\py_foundations_01_read_trace_state.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/lessons/py_foundations_01_read_trace_state.py
```

The terminal shows a small worked example and the remaining TODO count.
TODOs are the starting exercise state. Write predictions before changing
code. Run after one change, save the observed value or exception, and compare
with the exercise's acceptance check. A successful example does not mean the
unfinished exercises are complete. Keep the separate
[explanatory solutions](../solutions/py_foundations_01_read_trace_state_solutions.md) and
[runnable solution](../solutions/py_foundations_01_read_trace_state_solution.py) closed until you have an
attempt and evidence, or deliberately ask for a worked comparison.

## Vocabulary and concepts

A program is a list of instructions stored as text. Running the file asks an
interpreter to perform those instructions. Reading a line does not execute it,
and changing the file does not retroactively change a run that already ended.
Imagine a desk with labeled notes: a name tells you which note to read, while
assignment replaces the value that the label currently refers to. Keep a trace
table on paper with one row per executed line. This is useful even when the
program is too short to need a debugger.

- **Source code:** the text instructions you edit and save in a `.py` file.
- **Value:** a piece of data, such as the number `4` or the text `"four"`.
- **Name:** a label, such as `quantity`, that currently refers to a value.
- **Assignment:** an instruction using `=` that binds the left name to the
  evaluated right side. It is an action, not an algebraic equality claim.
- **Expression:** source that evaluates to a value, such as `quantity + 2`.
- **Output:** information a running program writes, commonly through `print`.

Python normally performs these top-level statements from top to bottom. A
blank line creates visual space. A line starting with `#` is a comment for a
reader. A comment is not an instruction, so writing the expected answer in a
comment cannot make an incorrect calculation pass. Choose descriptive names;
`number_of_boxes` helps a future reader more than `x` when boxes are the topic.

## Worked example / walkthrough

### Example A: replacement does not update earlier calculations

Predict both printed numbers before running this complete example:

```python
quantity = 3
unit_price = 4
subtotal = quantity * unit_price
quantity = 5
print(subtotal)
print(quantity * unit_price)
```

The right side of `subtotal = quantity * unit_price` is evaluated when that
line runs. `*` multiplies two numbers. Python stores the resulting value under
`subtotal`; it does not store an automatically updating spreadsheet formula.
The later assignment changes `quantity` but does not re-execute the earlier
line. `print(...)` calls a built-in display operation; parentheses surround
the value to display. The expected output is `12` on one line, then `20`.
Your trace should show `subtotal` staying at 12 after quantity changes.

### Example B: text and numbers obey different operations

```python
number = 4
text = "4"
print(number + 2)
print(text + "2")
print(type(number).__name__)
print(type(text).__name__)
```

Expected output is `6`, `42`, `int`, and `str`, in that order. Quotes create
text; the quotes themselves are not part of the stored text. `+` adds numbers
but joins strings. `type(value).__name__` asks the interpreter for a readable
type label; treat it as an inspection tool for now. A type describes what
operations a value supports. Removing quotes changes meaning, even if the
terminal displays similar digits. Do not try to memorize every type today.

### A reliable trace routine

Read a single statement, identify the names on its right side, substitute
their current values, and calculate that expression. Only then update the
left name. For a print, write an output row without changing other rows.
If a name has never been assigned in the current run, stop: the interpreter
cannot invent its intended value. A saved file run starts a new process with
new top-level state. A notebook can keep old state between cells, so a fresh
file run is a useful reference when cell results look surprising.

Before each exercise, create two columns labeled prediction and observation.
A disagreement is useful evidence. Locate the first line where the trace
differs, rather than making several edits until an answer looks plausible.
Re-running with identical input should produce identical output for every
example here. If it does not, first check that you saved and ran the same file.

## Exercises

1. **Trace a reassignment.** Trace `apples = 2; pears = apples + 3; apples = 9` as three separate lines. Do not run until your trace is complete. State both final values.

   **Verify:** `apples` equals 9 and `pears` equals 5; the trace records pears being calculated before apples changes.

   **Hint:** A name stores the current result, not the history of its formula.

2. **Separate calculation from display.** Create `boxes = 4`, `items_per_box = 6`, and a calculated `items`. Display a human-readable label followed by the value. Repeat with zero boxes.

   **Verify:** The terminal contains totals 24 and 0 in the two runs; changing the label does not change either calculated number.

   **Hint:** Use `print("Items:", items)` to display a label and a value.

3. **Predict text joining.** Predict the output of `"3" + "7"` and of `3 + 7`. Explain how you can prove the difference if the output alone is confusing.

   **Verify:** The first value equals the string `"37"`; the second equals integer 10. Inspection reports `str` and `int` respectively.

   **Hint:** Quotes are part of the source language that creates a string.

4. **Find the first invalid line.** In a fresh script, put `print(balance)` before `balance = 10`. Capture the final exception line, then make the smallest ordering change that permits a run.

   **Verify:** Before repair the exception class is `NameError`; after repair a fresh run prints 10 exactly once.

   **Hint:** Walk through time, not the visual distance between lines.

5. **Test a stale calculation.** Calculate `total = 2 * 5`, change the quantity to 3 under a separate name, and compare the old total with a new calculation. Do not edit the expected values to hide a disagreement.

   **Verify:** Your trace contains an old total of 10 and a recomputed total of 15, and identifies the line that recalculates the result.

   **Hint:** Assign quantity before using it, then explicitly repeat the calculation.

6. **Distinguish comments from actions.** Add a comment that predicts a total of 100 beside code that actually calculates `4 * 5`. Run the file, then repair the comment while preserving correct code.

   **Verify:** The output remains 20 before and after the comment repair; your observation names the multiplication as the executed operation.

   **Hint:** A comment can be wrong without causing an exception.

7. **Make a minimal reproduction.** Copy just the three statements needed to show that `copied = original` for an integer keeps its old value after `original` is reassigned. Use original values 8 and 11.

   **Verify:** The new script prints original 11 and copied 8, with no dependency on previous interactive commands.

   **Hint:** Copied here is another name for the earlier integer value; mutable containers come later.

8. **Transfer the trace to a receipt.** Starting with three tickets at seven units each and a two-unit discount on the whole order, calculate the payable amount. Then test no tickets and no discount. Use clear names.

   **Verify:** The normal payable value is 19; the empty-order value is 0. A written trace explains why the discount is applied once to the order.

   **Hint:** Write the intended arithmetic in plain language before translating it.

## Self-check

Close the examples. Explain why changing a quantity does not update an earlier
subtotal. Recreate a three-line trace using different numbers. Then describe
what quotes, `=`, and parentheses contribute to the statements you typed.
Read your prediction before running, rather than reconstructing it afterward.

## Common pitfalls

If the output looks unchanged after editing, save the file and inspect the
terminal command's filename. If `NameError` appears, read the named identifier
and find its first assignment in execution order. If text joins when you
expected arithmetic, inspect the two operand types. If a notebook disagrees
with a script, restart its kernel and run cells in order before modifying the
calculation. These checks distinguish a state problem from a setup problem.

## Next step

Continue with Day 2, where you add conversions, Boolean values, comparisons,
and formatting. Keep the trace habit for branches and loops. It remains
useful when a future program has many more lines.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for python-foundations-01.
Read python/professional/companion-guides/py_foundations_01_read_trace_state.md and python/professional/lessons/py_foundations_01_read_trace_state.py.
Check my direct prerequisites: python-01.
Keep solutions/ closed unless I request comparison after an attempt.
Explain the mental model, ask me to predict one result, let me attempt it,
give one hint at a time, inspect my evidence, and ask a retrieval question.
Done when I can independently reproduce the numbered acceptance checks,
explain a failure case, and transfer the policy to a changed input.
```
