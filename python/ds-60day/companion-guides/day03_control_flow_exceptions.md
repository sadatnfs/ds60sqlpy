# Day 3: Control Flow, Truthiness, and Exceptions

**Level:** Beginner

Control flow chooses which statements run. Exceptions separate an expected
failure path from the successful path. Each example in this lesson runs its
decision once: change the input value and rerun to test another case. Day 4
adds loops, which repeat a decision automatically.

## Learning objectives

By the end of this lesson, you can:

- write mutually exclusive `if`/`elif`/`else` branches;
- predict how truthiness and comparisons behave inside conditions;
- catch only the exceptions you can handle with `try`/`except`/`else`/`finally`; and
- raise a built-in exception such as `ValueError` with a message that explains
  the failure.

## Prerequisites

Complete Day 2 (`python-02`): types, conversions, comparisons, and truthiness.

<!-- BEGIN HOW TO RUN -->
## How to run this lesson

Open `python-03` in the classroom, or `python/ds-60day/notebooks/day03_control_flow_exceptions.ipynb` on a host; the [Python study guide](../../STUDY-GUIDE.md) explains both.

**Outcome:** Order branches correctly and catch only the errors you can handle.
<!-- END HOW TO RUN -->

<!-- BEGIN BEGINNER DEEP DIVE -->
## Beginner deep dive: build the idea before the syntax

### Start with one mental picture

Control flow is the route execution takes through a program. An
`if`/`elif`/`else` chain chooses exactly one branch: Python tests from
top to bottom and stops at the first true condition. Put narrow or more
specific rules before broader ones, and validate impossible inputs
before classifying valid ones.

Exceptions separate a normal return path from a failure path. A `try`
block should contain only the operation expected to fail, while
`except` names the failure the current layer can interpret. Catching
every exception hides programming bugs. `else` runs after a successful
`try`; `finally` runs whether success or failure occurred.

### Vocabulary in plain language

- **condition:** an expression evaluated for truthiness.
- **branch:** one possible block selected by a condition.
- **guard clause:** an early check that rejects or handles an invalid case.
- **exception:** an object representing a failure that interrupts normal flow.
- **raise:** to deliberately signal an exception.
- **handler:** an `except` block for a named exception type.

### Syntax anatomy

In `if score >= 90:`, the colon ends the condition and starts an
indented suite. Only code indented under that branch belongs to it. In
`except ValueError as exc:`, `ValueError` is the narrow failure type and
`exc` is the actual exception object. An exception handler is not a
substitute for an ordinary condition that can be checked directly.

### Worked example 1: Order specific branches before general branches

Classify a value after validating its domain. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
score = 75

if not 0 <= score <= 100:
    grade = "invalid"
elif score >= 90:
    grade = "distinction"
elif score >= 60:
    grade = "pass"
else:
    grade = "fail"

grade
```

**Expected observation:** `'pass'`. Python tests the conditions from the top
and stops at the first true one: 75 is inside 0 to 100, is not at least 90, and
is at least 60. Change `score` to `42`, `95`, and `101`, predict each result,
and rerun: `'fail'`, `'distinction'`, and `'invalid'`. The range check comes
first so that 101 cannot reach the `'distinction'` branch.

### Worked example 2: Protect only the fallible conversion

Let unrelated programming errors remain visible. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
text = " 12 "

try:
    count = int(text.strip())
except ValueError:
    count = None
    outcome = "not an integer"
else:
    outcome = "parsed"

(count, outcome)
```

**Expected observation:** `(12, 'parsed')`. Only `int(...)` sits inside
`try`, so only a failed conversion can reach the handler, and the `else` block
runs only after the conversion succeeded. Change `text` to `"twelve"` and
rerun: `(None, 'not an integer')`. Both paths assign `count`, so the last line
never meets an undefined name.

### A debugging routine for this topic

When the output differs from your prediction, use this order:

1. Trace conditions from top to bottom and mark the first one that becomes true.
2. Move validation before classification when impossible values enter normal branches.
3. Shrink a large `try` block until it contains only the operation with the expected failure.
4. Replace bare `except:` or `except Exception:` with the narrow type you can recover from.

### Practice ramp

Work this lesson's exercises in the five practice modes from the [Python study guide](../../STUDY-GUIDE.md).

**Useful alternative:** Use a placeholder such as `None` only when "no value" is a legitimate outcome; otherwise raise a specific exception so the failure cannot be mistaken for data.

**Boundary to remember:** Boundary values such as 0, 1, 59, 60, 89, 90, and 100 expose gaps and overlaps in ordered conditions.
<!-- END BEGINNER DEEP DIVE -->

## Vocabulary and mental model

- **Branch:** one possible route through a program.
- **Condition:** an expression interpreted as true or false.
- **Traceback:** the report Python prints for an unhandled exception; its last
  line names the exception type and message.
- **Exception:** an object that interrupts normal execution when an operation
  cannot satisfy its contract.
- **Raise:** signal a failure; **catch:** handle a specific failure.
- **`else`/`finally`:** exception `else` runs only after success; `finally` runs
  whether the operation succeeds or fails.

Treat exceptions as structured failure information, not as a substitute for all
branching.

## Worked example

```python
raw = "42"

try:
    value = int(raw)
except ValueError as exc:
    raise ValueError(f"expected an integer, received {raw!r}") from exc

if value < 0:
    raise ValueError(f"value must be non-negative, received {value}")

value
```

With `raw = "42"` the cell displays `42`. With `raw = "forty"`, the conversion
fails and the new message `expected an integer, received 'forty'` is raised;
`from exc` keeps the original `invalid literal for int()` error in the
traceback. With `raw = "-4"`, the conversion succeeds and the domain rule raises
`value must be non-negative, received -4`. The two failures have different
causes, and the messages make both diagnosable.

## Exercises and progressive hints

1. Given `number = 15`, write one ordered `if`/`elif`/`else` chain that sets `label` to `"FizzBuzz"` for multiples of both 3 and 5, `"Fizz"` for multiples of 3 only, `"Buzz"` for multiples of 5 only, and `str(number)` otherwise. **Constraints:** test divisibility with `%` and keep all four outcomes in one chain.
   **Verify:** rerun with `number` set to 3, 5, 15, 16, and 30 and assert the labels `"Fizz"`, `"Buzz"`, `"FizzBuzz"`, `"16"`, and `"FizzBuzz"`. Day 4 repeats this decision for 1 through 30 with a `for` loop.

2. Given `text = " 7 "`, put only `int(text)` inside `try`, set `age` to the integer on success, and set `age = None` when `ValueError` is raised. **Constraints:** do not use a bare `except`; use an `else` block to record success.
   **Verify:** run with `"42"`, `" 7 "`, and `"seven"` and assert that `age` is `42`, `7`, and `None`; explain which runs execute the `else` block.

3. Given `measurement = -0.1`, raise `ValueError` with the message `measurement must be non-negative, got -0.1` when the value is negative, and leave non-negative values unchanged. **Constraints:** check the sign with an `if` before any calculation uses the value.
   **Verify:** run once with `2.5` (no error, value unchanged) and once with `-0.1`; then wrap the check in `try`/`except ValueError as exc` and assert that `str(exc)` equals the exact message. Day 12 shows how to define a dedicated exception type such as `NegativeMeasurementError`.

### Additional mastery practice

Make branch order and exception boundaries deliberate. Catch only the failure that the current layer can interpret or repair.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

4. **Prediction:** Predict which branch handles 0, 9, and 12 when checks are ordered as `x % 2 == 0`, `x % 3 == 0`, then both. Explain the bug.
   **Progressive hint:** Only the first true branch runs; test the most specific rule first.
   **Verify:** Record the branch selected for `0`, `9`, and `12` before/after reordering; confirm the repaired `12` reaches the combined rule.
5. **Tracing:** Trace `try/except/else/finally` for a successful integer parse and for invalid text. Which clauses run in each path?
   **Progressive hint:** `else` follows success; `finally` runs in both cases.
   **Verify:** Use a four-column trace for `try`, `except`, `else`, and `finally` on valid/invalid text; each clause's executed flag must match the language rules.
6. **Implementation:** A grader records scores as floats. Policy: from 89.5 to 100 is `"distinction"`, from 59.5 up to (but not including) 89.5 is `"pass"`, from 0 up to 59.5 is `"fail"`, and any score outside 0 to 100 raises `ValueError`. Given `score = 59.5`, write the chain.
   **Progressive hint:** Validate the range first, then test the thresholds from highest to lowest with `>=`.
   **Verify:** Rerun with `59.49`, `59.5`, `89.49`, `89.5`, `100.0`, and `100.5`; assert `"fail"`, `"pass"`, `"pass"`, `"distinction"`, `"distinction"`, and a `ValueError` for `100.5`.
7. **Debugging:** A cell wraps both `count = int(raw_count)` and `total_cost = count * unit_price` in one `try` block followed by a bare `except:` that sets `total_cost = 0`, and `unit_price` was never defined. Rebuild it so only the conversion is protected and only `ValueError` is caught.
   **Progressive hint:** Keep only the conversion inside the protected block and move the calculation after it.
   **Verify:** With `raw_count = "twelve"` the handler reports invalid text; with `raw_count = "12"` the `NameError` for `unit_price` now appears instead of a silent `0`; after defining `unit_price = 2.5`, assert `total_cost == 30.0`.
8. **Edge case and explanation:** Given `numerator = 3` and `denominator = 0`, choose a zero-denominator policy: raise `ZeroDivisionError` with a clear message, or set `ratio = None` and record why. Justify the choice.
   **Progressive hint:** Code that other people reuse usually should not invent a numeric answer such as `0.0`.
   **Verify:** With `denominator = 4`, assert `ratio == 0.75`; with `denominator = 0`, assert your chosen outcome exactly and explain why `0.0` would be a fabricated answer.

Before opening the reference solution, write one sentence explaining
which contract or mental model each result confirms.

## Self-check

- Why does branch order matter in FizzBuzz?
- Which boundary values (59, 60, 89, 90, 100, 101) prove that the score branches neither overlap nor leave gaps?
- Why is `except Exception:` usually too broad?
- What information is preserved by `raise NewError(...) from exc`?

Expected behavior: each FizzBuzz test value gets exactly one label, invalid
numeric text is reported without hiding unrelated bugs, and a negative
measurement raises `ValueError` with its exact message.

## Common pitfalls and diagnosis

- **FizzBuzz never prints the combined case:** inspect branch order.
- **`IndentationError`, or a line running in the wrong branch:** every line of
  a branch must be indented by the same amount under its `if`, `elif`,
  `else`, `try`, or `except` line. Find where the indentation ends.
- **Errors disappear silently:** never use a bare `except: pass`; log, return a
  documented fallback, or re-raise.
- **`NameError` after `try`:** a name was assigned only on the success path,
  so the failure path left it undefined. Assign it in the handler too (worked
  example 2 sets `count = None`) or initialize it before `try`.
- **The wrong exception is caught:** reproduce the smallest failing expression
  and inspect the traceback's final line.

## Continue

- [Open the learner notebook](../notebooks/day03_control_flow_exceptions.ipynb)
- [Check the separate solution](../solutions/day03_control_flow_exceptions/day03_solutions.md)
- [Next: Day 4; Loops, comprehensions, and generators](day04_loops_comprehensions_generators.md)

## Ask an AI tutor about this lesson

AI coaching is optional. To use a tutor, copy this prompt from the repository root:

```text
Use $guide-ds60sqlpy-learning to tutor me through `python-03`
(Day 3: Control Flow, Truthiness, and Exceptions). Direct catalog prerequisites: `python-02`.
I have completed the direct prerequisites: `python-02`. Emphasize branch selection, truthiness in conditions, and narrow exception boundaries.
Read `python/ds-60day/companion-guides/day03_control_flow_exceptions.md` and use the learner notebook
`python/ds-60day/notebooks/day03_control_flow_exceptions.ipynb`. Do not open or quote anything under `solutions/` unless
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
