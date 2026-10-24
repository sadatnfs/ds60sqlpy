# Debug from Evidence Instead of Guessing

**Stable ID:** `python-foundations-02`

**Estimated time:** 150 minutes, split across sessions as needed.

## Level and prerequisites

Foundation. Direct catalog prerequisites: `python-03`.

You can assign values, inspect types, choose a branch, and recognize an exception from Days 1 to 3. This lab slows down the debugging process before loops and larger programs arrive. You do not need a debugger extension or any new package.

## Learning objectives

- Classify syntax, runtime, and incorrect-result failures.
- Read an exception from its final line back to the failing statement.
- Reduce a failure to a small, repeatable input.
- Change one hypothesis at a time and preserve a regression case.

## How to run this lesson

**Primary browser route:** run `./classroom` from the repository root and
choose **Python** on `/classroom`. Open this lesson in the shared workspace,
read its capability notice, and use its supported coding or reading workflow.
The [classroom guide](../../../docs/classroom-experience.md) explains saved work, runtimes and switching subjects.

**Optional native notebook/editor route:** the instructions below describe
separately prepared host tools. They are useful alternatives, not prerequisites
for opening this lesson in the Docker classroom.

Use the repository folder in VS Code. The rendered lesson page is a preview;
edit the actual [learner script](../lessons/py_foundations_02_debug_evidence.py). Copy it to an ignored
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
& $CoursePython python\professional\lessons\py_foundations_02_debug_evidence.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/lessons/py_foundations_02_debug_evidence.py
```

The terminal shows a small worked example and the remaining TODO count.
TODOs are the starting exercise state. Write predictions before changing
code. Run after one change, save the observed value or exception, and compare
with the exercise's acceptance check. A successful example does not mean the
unfinished exercises are complete. Keep the separate
[explanatory solutions](../solutions/py_foundations_02_debug_evidence_solutions.md) and
[runnable solution](../solutions/py_foundations_02_debug_evidence_solution.py) closed until you have an
attempt and evidence, or deliberately ask for a worked comparison.

## Vocabulary and concepts

Debugging is an investigation into a disagreement between intended and
observed behavior. Treat the program as evidence, not as a puzzle solved by
random edits. A small program with one input and one clear failure is easier
to reason about than a full application whose state you cannot reconstruct.
First write what should happen and what actually happened. Then locate the
earliest difference. Only then propose and test a change.

- **Symptom:** the observable failure, such as a wrong total or an exception.
- **Hypothesis:** a specific explanation that could be disproved by a check.
- **Reproduction:** a repeatable input and command that produces the symptom.
- **Traceback:** the execution history printed when an exception escapes.
- **Regression case:** a saved example that catches a previously fixed defect.
- **Boundary case:** an input exactly at a rule's change point, such as zero.

Syntax errors prevent Python from interpreting a statement. Runtime errors
happen while a syntactically valid program executes, such as division by zero.
Logic errors can produce the wrong answer while the process still exits
normally. An exit code of zero is useful process evidence, but it cannot prove
that your intended calculation was implemented. A comment claiming success
is even weaker: it does not inspect any actual behavior.

## Worked example / walkthrough

### Example A: preserve the exact boundary

```python
quantity = 0
if quantity > 0:
    status = "ready"
else:
    status = "empty"
print(status)
assert status == "empty"
```

The contract says an order is ready only when quantity is strictly positive.
`>` excludes zero. The colon begins a branch, and indentation marks its body.
`else` covers every case that did not satisfy the first condition. Expected
output is `empty`; the assertion checks that value. Replacing `>` with `>=`
is a one-character change with a real policy effect. Testing only quantity
three would miss it. Try quantities zero and one before calling the rule fixed.

### Example B: inspect before converting

```python
raw_quantity = " 12 "
print(repr(raw_quantity), type(raw_quantity).__name__)
quantity = int(raw_quantity)
print(quantity + 1)
assert quantity == 12
```

Expected output first exposes surrounding spaces and type `str`, then 13.
`repr` produces an inspectable representation; it can reveal whitespace that
ordinary display hides. `int` accepts surrounding whitespace for this input.
If the input becomes `"twelve"`, conversion raises `ValueError`. That symptom
does not prove that integer conversion is broken. It shows that the supplied
text does not match the accepted numeric representation. Decide whether to
reject it, prompt again, or support another representation. Do not silently
replace every invalid quantity with zero.

### Read a traceback deliberately

Start with the final exception class and message. Find the named source line
in your saved file. Inspect the values and types entering that line using a
temporary, bounded print. In a longer traceback, move upward until you reach
the call site that supplies those values. Do not copy a whole traceback into a
bug report when it contains private paths or user data. Preserve the class,
the smallest reproducing code, and harmless input that illustrates the failure.

When trying a repair, keep the input fixed. If you change code and data at the
same time, a successful run cannot tell you which change mattered. Test the
original reproduction, then a normal case and a boundary case. Removing a
failing statement, catching every exception, or editing an assertion to match
the wrong answer can make a process appear healthy while preserving the bug.

### Keep an investigation log

For each numbered task, write five short fields: expected behavior, observed
behavior, hypothesis, smallest experiment, and result. If the result contradicts
the hypothesis, keep it and choose a better explanation. A failed hypothesis
is progress when it removes a possibility. Save the repaired example alongside
its checks so a later refactor cannot quietly reintroduce the same defect.

## Exercises

1. **Classify three failures.** Create separate tiny scripts containing a missing closing parenthesis, `1 / 0`, and `total = 3 + 4` where the intended rule is multiplication. Classify each before running.

   **Verify:** Your log records `SyntaxError`, `ZeroDivisionError`, and a normal run with wrong value 7 instead of 12, respectively.

   **Hint:** A normal exit and a correct business result are separate claims.

2. **Inspect the raw input.** Inspect `raw = " 08 "` with `repr` and `type`, convert it deliberately, and calculate its successor. Then try `"eight"` in a separate run.

   **Verify:** The valid parsed value is 8 and successor is 9; invalid text raises `ValueError` and is not converted to zero.

   **Hint:** Read the exact characters before changing the parser.

3. **Repair the boundary.** A free-shipping rule says orders costing at least 20 qualify. The implementation uses `amount > 20`. Predict values 19, 20, and 21, then repair one comparison.

   **Verify:** A three-row observation table reports False, True, True after the change; the before table differs only at 20.

   **Hint:** Translate at least into its mathematical boundary.

4. **Read an exception precisely.** Run `int("4.5")` in a fresh file. Capture the exception class and the failing line. State whether the input is invalid integer text or a missing package.

   **Verify:** The recorded class is `ValueError`; no installation command is used, and the report identifies the text `"4.5"` as the failing input.

   **Hint:** A decimal-looking string is not an integer representation for int.

5. **Reduce a wrong result.** A receipt with price 7, quantity 3, and a whole-order discount 2 uses `price * (quantity - discount)`. Strip unrelated output and repair only the arithmetic grouping.

   **Verify:** The failing result is 7 and repaired result is 19. With discount zero, both formulas yield 21, showing why that case alone missed the bug.

   **Hint:** State whether the discount changes the number of items or the order total.

6. **Keep the failure visible.** Write a try/except around `int("unknown")` that records the conversion failure by setting a status string. Avoid an empty except block and do not return a fake successful amount.

   **Verify:** The terminal reports status `invalid quantity`; a valid `"4"` reports `accepted` and quantity 4.

   **Hint:** Catch the specific conversion exception near the conversion.

7. **Disprove a hypothesis.** Investigate `"2" + "3"` yielding `"23"`. Test the hypothesis that Python added the numbers incorrectly by inspecting types and repeating the operation on integers.

   **Verify:** Your log records string operands and integer result 5 in the control experiment, rejecting the arithmetic-bug hypothesis.

   **Hint:** Change one variable in your experiment: the value types.

8. **Write a regression note.** Choose the shipping or receipt defect. Save a four-part note containing contract, smallest failing input, repaired observation, and one nearby boundary case. Add executable checks.

   **Verify:** The note names concrete input 20 for shipping or (7, 3, 2) for the receipt, and assertions fail if you reintroduce the original operator.

   **Hint:** Temporarily reverse the repair to see whether the check detects it, then restore it.

## Self-check

Explain the difference between a symptom and an explanation without looking
at the vocabulary list. Describe a defect that never raises an exception.
Show why a boundary test can find something a normal test misses. Reproduce
one fixed example in a new file without copying its final implementation.

## Common pitfalls

If an edit appears to do nothing, verify saved file and executed path. If an
except block produces a plausible number after invalid input, remove the
fallback and inspect the conversion failure. If your test passes before the
repair, ask whether its input reaches the failing branch. If every attempt
changes many lines, return to the minimal reproduction and test one claim.
Use a package installer only when the evidence identifies an import problem.

## Next step

Continue into loops and functions. Keep the investigation log for Day 10 tests
and Day 11 debugging tools. Those tools make observations easier to collect;
they do not replace a clear contract or a falsifiable hypothesis.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for python-foundations-02.
Read python/professional/companion-guides/py_foundations_02_debug_evidence.md and python/professional/lessons/py_foundations_02_debug_evidence.py.
Check my direct prerequisites: python-03.
Keep solutions/ closed unless I request comparison after an attempt.
Explain the mental model, ask me to predict one result, let me attempt it,
give one hint at a time, inspect my evidence, and ask a retrieval question.
Done when I can independently reproduce the numbered acceptance checks,
explain a failure case, and transfer the policy to a changed input.
```
