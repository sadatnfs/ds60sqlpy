# Day 2 — Variables and Core Types

**Level:** Beginner

Python values have types; variable names refer to those values. This lesson
turns text input into useful values and formats results clearly.

## Learning objectives

By the end of this lesson, you can:

- distinguish `str`, `int`, `float`, `bool`, and `None`;
- convert compatible values deliberately instead of relying on guesswork;
- use comparisons, truthiness, string methods, and f-strings; and
- explain why an input value is text until it is parsed.

## Prerequisites

Complete Day 1 (`python-01`): run the course environment and a notebook cell.





<!-- BEGIN HOW TO RUN -->
## How to run this lesson

Work from the repository root. The rendered HTML lesson is a readable
preview; execute the real notebook in VS Code or JupyterLab.

1. Confirm the course environment before changing it:

   ```powershell
   # Windows PowerShell
   $CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
       (Resolve-Path .\.venv\Scripts\python.exe).Path
   } else {
       (Resolve-Path .\.venv\python.exe).Path
   }
   & $CoursePython scripts\course.py doctor
   ```

   ```bash
   # macOS/Linux
   .venv/bin/python scripts/course.py doctor
   ```

2. Read `python/ds-60day/companion-guides/day02_basics_types.md`, then open `python/ds-60day/notebooks/day02_basics_types.ipynb` from the repository
   folder in VS Code or JupyterLab.
3. Select **Python (ds60sqlpy)**. Do not run `%pip` in the notebook. If
   an import is missing, use the doctor and the catalog dependency label
   to repair the shared environment.
4. Restart the kernel and run from the first cell downward. Before every
   example, write a prediction; after it runs, compare the actual value,
   type, shape, or side effect with the stated observation.
5. Attempt each numbered exercise in its own work cell. Use the explicit
   verification as part of the task. Keep `solutions/` closed until you
   have a tested attempt or deliberately ask for help.

**Lesson outcome:** use day 2 — variables and core types to practice objects, names, built-in types, conversion, and truthiness
and explain the evidence produced by your code.
<!-- END HOW TO RUN -->

<!-- BEGIN BEGINNER DEEP DIVE -->
## Beginner deep dive — build the idea before the syntax

### Start with one mental picture

A Python value is an **object** with a type and behavior. A variable is a
name that refers to an object; it is not a box permanently restricted to
one type. Operators choose behavior from the operand types, which is why
`7 + 2` performs arithmetic while `"7" + "2"` joins text.

Input enters a program as text unless a boundary explicitly parses it.
Keep three stages visible: normalize the raw text, convert it to the
intended type, then calculate. Formatting turns a result back into text
for a person. Truthiness is a separate idea: zero, empty collections,
empty strings, and `None` are false-like, but the non-empty string
`"False"` is truthy.

### Vocabulary in plain language

- **object:** a runtime value with a type, identity, and supported operations.
- **name:** an identifier that refers to an object.
- **type:** the category that defines a value's operations and behavior.
- **literal:** source syntax that directly creates a value, such as `42` or `'hi'`.
- **conversion:** constructing a value of one type from another representation.
- **truthiness:** the rule Python uses when a value appears in a Boolean context.

### Syntax anatomy

In `price = float(raw_price.strip())`, Python first looks up
`raw_price`, calls the string method `strip`, passes the returned text to
`float`, and finally binds the resulting number to `price`. The
right-hand side completes before assignment. In
`f"${price:.2f}"`, the colon starts a format specification; `.2f` means
fixed-point display with two digits after the decimal.

### Worked example 1 — Parse, calculate, then format

Keep representation changes separate from arithmetic. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
raw_quantity = " 3 "
raw_price = "4.50"
quantity = int(raw_quantity.strip())
price = float(raw_price)
total = quantity * price
(quantity, price, total, f"${total:.2f}")
```

**Expected observation**

```text
`(3, 4.5, 13.5, '$13.50')`. The final string is presentation; `total` remains numeric.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### Worked example 2 — Make Boolean parsing explicit

Do not confuse a non-empty spelling with a Boolean value. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
raw_enabled = " FALSE "
normalized = raw_enabled.strip().lower()
enabled = normalized == "true"
(normalized, enabled, bool(raw_enabled))
```

**Expected observation**

```text
`('false', False, True)`. `bool(raw_enabled)` is `True` because the original string contains characters.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### A debugging routine for this topic

When the output differs from your prediction, use this order:

1. When `+` gives an unexpected result, inspect both operands with `type(...)`.
2. When conversion fails, print `repr(raw_text)` so spaces and escape characters are visible.
3. Use `is None` when absence must remain different from `0`, `0.0`, or an empty string.
4. Remember that string methods return new strings; bind the result if you want to keep it.

### Practice ramp

Work through the numbered exercises in five modes rather than treating all
of them as blank-code prompts:

1. **Prediction:** state the value, type, shape, rows, or side effect before
   execution.
2. **Guided modification:** change one part of a worked example and explain
   which part of the result must change.
3. **Independent application:** implement the same idea with a new input and
   an explicit contract.
4. **Debugging and edge cases:** reproduce a failure, identify the violated
   assumption, and prove the repair at a boundary.
5. **Retrieval:** close the guide and explain the core model from memory
   before moving on.

**Useful alternative:** Explicit conversions are usually clearer than relying on implicit coercion; a small parsing function is useful when accepted spellings form a real input contract.

**Boundary to remember:** Empty text, whitespace-only text, `None`, zero, and non-ASCII text often reveal assumptions hidden by happy-path examples.
<!-- END BEGINNER DEEP DIVE -->

## Vocabulary and mental model

- **Value:** data such as `42`, `3.5`, or `"Ada"`.
- **Type:** the rules and operations associated with a value.
- **Variable:** a name bound to a value; assignment does not copy every object.
- **Conversion:** constructing one type from a compatible value, such as
  `float("3.14")`.
- **Truthiness:** the boolean interpretation of a value. Empty strings and
  containers are false; non-empty ones are true.
- **Immutable:** unable to change in place. String methods return new strings.

## Worked example

```python
raw_celsius = "21.5"
celsius = float(raw_celsius)
fahrenheit = celsius * 9 / 5 + 32
label = "  Indoor Sensor  ".strip().lower()

print(f"{label}: {fahrenheit:.1f} °F")
```

Trace the types after each line. Parsing and presentation are separate steps:
the calculation uses numbers, while the f-string creates display text.

## Exercises and progressive hints

Each item is a complete mini-contract. Before writing code, copy its input,
expected behavior, constraints, and verification into your work cell. A
result is not complete merely because it “looks right”; run the stated
assertion or inspection and explain what it proves.

1. Prompt twice with `input()` for numbers such as `12.5` and `7.25`, convert both strings to `float`, and print `19.75`. **Constraints:** display a short label with the result and do not concatenate the raw strings.
   **Verify:** first show that `type(input(...))` is `str`, then test whole-number and decimal text.

2. Starting from `raw = ' Data Science '`, create a new value exactly equal to `'data science'`. **Constraints:** use string methods rather than slicing or a hard-coded replacement.
   **Verify:** assert the normalized result and show that `raw` itself is unchanged because strings are immutable.

3. Convert the text `'3.14'` to a floating-point number, double it, and format the result as `6.28`. **Constraints:** keep the original text in one name and the numeric value in another.
   **Verify:** assert the parsed value has type `float` and explain why `'3.14' * 2` is not numeric multiplication.

### Additional mastery practice

Separate parsing, calculation, and presentation. Predict a value's type before relying on an operator or truthiness rule.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

4. **Prediction:** Predict the value and type of `"7" * 2`, `7 / 2`, `7 // 2`, `bool("")`, and `bool("0")` before running them.
   **Progressive hint:** Operators follow operand types; non-empty strings are truthy.
   **Verify:** Create a table of predicted/actual value and type for all five expressions; every row must match, including `bool('0') is True`.
5. **Tracing:** Trace `raw = ' 0042 '; cleaned = raw.strip(); number = int(cleaned)` and record the value/type after every assignment.
   **Progressive hint:** String methods return new strings; conversion constructs an integer.
   **Verify:** Record `repr(value)` and `type(value).__name__` after `raw`, `cleaned`, and `number`; confirm the original string still contains spaces.
6. **Implementation:** Implement `parse_temperature(text)` so surrounding whitespace is accepted and the result is a float, then format one decimal place.
   **Progressive hint:** Keep parsing separate from f-string presentation.
   **Verify:** Assert whitespace inputs such as `' 32.5 '` return `32.5` and format as `'32.5'`; prove invalid text follows the documented exception path.
7. **Debugging:** Repair `enabled = bool(raw)` for inputs such as `"true"`, `"false"`, and `" FALSE "`. Reject unknown spellings.
   **Progressive hint:** Normalize the text and compare explicit accepted tokens.
   **Verify:** Assert accepted case/whitespace variants map to the intended Booleans and that an unknown token such as `'yes-ish'` raises a specific `ValueError`.
8. **Edge case and explanation:** Model an optional discount where `None` means not supplied and `0.0` means supplied but zero. Explain why a truthiness check loses meaning.
   **Progressive hint:** Use `is None` when absence is distinct from a numeric zero.
   **Verify:** Test `None`, `0.0`, and `0.25` separately; assert the first is absent while the latter two remain supplied numeric discounts.

Before opening the reference solution, write one sentence explaining
which contract or mental model each result confirms.

## Self-check

- What is the difference between `"8" + "2"` and `8 + 2`?
- Why does `bool("False")` evaluate to `True`?
- What does `None` communicate that `0` does not?
- Which format specifier would show one digit after the decimal point?

Expected behavior: numeric addition produces a number, text cleanup leaves the
original string unchanged, and formatted output is readable.

## Common pitfalls and diagnosis

- **Numbers concatenate:** print their types; one or both values are strings.
- **`ValueError` during conversion:** show the original value with `repr(...)`
  to reveal spaces or unexpected characters. Day 3 adds recovery logic.
- **Unexpected integer result assumptions:** `/` returns a float; `//` performs
  floor division, which differs from truncation for negative numbers.
- **Variable names shadow built-ins:** avoid names such as `str`, `list`, and
  `sum`; restarting the kernel clears accidental rebinding.
- **Floating-point output looks imprecise:** binary floats approximate many
  decimal fractions; format for display rather than comparing display strings.

## Continue

- [Open the learner notebook](../notebooks/day02_basics_types.ipynb)
- [Check the separate transfer solutions](../solutions/day02_basics_types/day02_solutions.md)
- [Next: Day 3 — Control flow and exceptions](day03_control_flow_exceptions.md)

## Ask Codex about this lesson

Codex coaching is optional; the guide and notebook above contain the full
lesson. If you want a patient tutor, copy this prompt from the repository
root:

```text
Use $guide-ds60sqlpy-learning to tutor me through `python-02`
(Day 2 — Variables and Core Types). I am a complete beginner. Emphasize objects, names, built-in types, conversion, and truthiness.
Read `python/ds-60day/companion-guides/day02_basics_types.md` and use the learner notebook
`python/ds-60day/notebooks/day02_basics_types.ipynb`. Do not open or quote anything under `solutions/` unless
I explicitly ask after making an honest attempt. Use these visible phases:
Explain, Predict, Attempt, Hint, Evidence, and Retrieval. First explain one
concept in plain language, then ask me to predict a small example and wait
for my attempt. Give only one progressive hint at a time. Help me run or
inspect my actual notebook evidence, adapt commands to my operating system,
and do not treat the rendered HTML preview as executable. Finish with 2-3
retrieval questions and one next step. Done when I can explain the mental
model without the guide, complete one independent exercise, and show the
prompt's verification evidence from my notebook.
```
