# Day 2: Variables and Core Types

**Level:** Beginner

Python values have types; variable names refer to those values. This lesson
turns text input into useful values and formats results clearly.

## Learning objectives

By the end of this lesson, you can:

- distinguish `str`, `int`, `float`, `bool`, and `None`;
- convert compatible values deliberately instead of relying on guesswork;
- use comparisons, truthiness, string methods, and f-strings; and
- explain why typed input is text until it is parsed, and why this lesson
  supplies that text in a variable instead of calling `input()`.

## Prerequisites

Complete the program tracing on-ramp (`python-foundations-01`), which includes Day 1 (`python-01`). You can run a saved script and distinguish names, values, calculation, and output.

<!-- BEGIN HOW TO RUN -->
## How to run this lesson

Open `python-02` in the classroom, or `python/ds-60day/notebooks/day02_basics_types.ipynb` on a host; the [Python study guide](../../STUDY-GUIDE.md) explains both.

**Outcome:** Convert text to numbers and Booleans on purpose, then format the result.
<!-- END HOW TO RUN -->

<!-- BEGIN BEGINNER DEEP DIVE -->
## Beginner deep dive - build the idea before the syntax

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

**Typed input in this classroom.** `input("Prompt: ")` pauses a program
until someone types a line, then returns that line as a `str`. The
classroom Run executes your pad as a finished program with no keyboard
attached, so `input()` stops there with `EOFError: EOF when reading a
line`. This lesson therefore supplies the typed text in a variable, for
example `left_text = "12.5"`. That value has exactly the type `input()`
would return, so every conversion step is the same. In an interactive
terminal or a contributor Jupyter notebook, `input()` waits for you
instead.

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

### Worked example 1 - Parse, calculate, then format

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

**Expected observation:** `(3, 4.5, 13.5, '$13.50')`. The final string is presentation; `total` remains numeric.

### Worked example 2 - Make Boolean parsing explicit

Do not confuse a non-empty spelling with a Boolean value. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
raw_enabled = " FALSE "
normalized = raw_enabled.strip().lower()
enabled = normalized == "true"
(normalized, enabled, bool(raw_enabled))
```

**Expected observation:** `('false', False, True)`. `bool(raw_enabled)` is `True` because the original string contains characters.

### A debugging routine for this topic

When the output differs from your prediction, use this order:

1. When `+` gives an unexpected result, inspect both operands with `type(...)`.
2. When conversion fails, print `repr(raw_text)` so spaces and escape characters are visible.
3. Use `is None` when absence must remain different from `0`, `0.0`, or an empty string.
4. Remember that string methods return new strings; bind the result if you want to keep it.

### Practice ramp

Work this lesson's exercises in the five practice modes from the [Python study guide](../../STUDY-GUIDE.md).

**Useful alternative:** Explicit conversions are usually clearer than relying on implicit coercion. When the same accepted spellings are needed in many places, Day 5 shows how to package the conversion in a small function.

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

1. Treat `left_text = "12.5"` and `right_text = "7.25"` as two values a user typed. Convert both to `float`, add them, and print `Sum: 19.75`. **Constraints:** keep the text values and the numbers in different names, and do not join the strings.
   **Verify:** show that `type(left_text).__name__` is `'str'` before conversion and assert that the sum equals `19.75`; then change the texts to `"12"` and `"7"` and confirm the output is `Sum: 19.0`.

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
6. **Implementation:** Given `raw_temperature = " 32.5 "`, create a `float` named `temperature` and a display string named `shown` with one decimal place. Then run `float("warm")` once to see what invalid text does.
   **Progressive hint:** `float()` ignores surrounding spaces; formatting with `:.1f` produces text, not a new number.
   **Verify:** Assert `temperature == 32.5`, `type(temperature) is float`, and `shown == "32.5"`; record the last line of the `float("warm")` error, `ValueError: could not convert string to float: 'warm'`. Day 3 shows how to handle that error.
7. **Debugging:** `enabled = bool(raw)` gives `True` for `raw = " FALSE "` because any non-empty string is truthy. Repair the conversion so `"true"`, `"false"`, and `" FALSE "` map to the intended Booleans, and flag any other spelling as unknown.
   **Progressive hint:** Normalize with `strip()` and `lower()`, then compare the result with `==`.
   **Verify:** Compute `enabled = normalized == "true"` and `is_known = normalized == "true" or normalized == "false"`; assert that `"true"` gives `enabled is True`, `" FALSE "` gives `enabled is False` with `is_known is True`, and `"yes-ish"` gives `is_known is False`. Day 3 shows how to reject unknown text with an exception.
8. **Edge case and explanation:** Model an optional discount where `None` means not supplied and `0.0` means supplied but zero. Explain why a truthiness check loses meaning.
   **Progressive hint:** `discount is None` asks about absence; `bool(discount)` asks about truthiness.
   **Verify:** For `discount` set to `None`, `0.0`, and `0.25`, record `discount is None` and `bool(discount)`; assert that `is None` is `True` only for `None`, while `bool()` is `False` for both `None` and `0.0`.

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
- **`EOFError: EOF when reading a line`:** the program called `input()`, but
  no keyboard is attached to the run, as in the classroom Run. Supply the
  text in a variable such as `raw = "12.5"` instead.
- **Unexpected integer result assumptions:** `/` returns a float; `//` performs
  floor division, which differs from truncation for negative numbers.
- **Variable names shadow built-ins:** avoid names such as `str`, `list`, and
  `sum`; restarting the kernel clears accidental rebinding.
- **Floating-point output looks imprecise:** binary floats approximate many
  decimal fractions; format for display rather than comparing display strings.

## Continue

- [Open the learner notebook](../notebooks/day02_basics_types.ipynb)
- [Check the separate transfer solutions](../solutions/day02_basics_types/day02_solutions.md)
- [Next: Day 3 - Control flow and exceptions](day03_control_flow_exceptions.md)

## Ask an AI tutor about this lesson

AI coaching is optional. To use a tutor, copy this prompt from the repository root:

```text
Use $guide-ds60sqlpy-learning to tutor me through `python-02`
(Day 2: Variables and Core Types). Direct catalog prerequisites: `python-foundations-01`.
I have completed the direct prerequisites: `python-foundations-01`. Emphasize objects, names, built-in types, conversion, and truthiness.
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
