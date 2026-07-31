# Day 3 — Control Flow, Truthiness, and Exceptions

**Level:** Beginner

Control flow chooses which statements run. Exceptions separate an expected
failure path from the successful path.

## Learning objectives

By the end of this lesson, you can:

- write mutually exclusive `if`/`elif`/`else` branches;
- iterate with `for` and repeat conditionally with `while`;
- catch only the exceptions you can handle; and
- define and raise a domain-specific exception with a useful message.

## Prerequisites

Complete Day 2 (`python-02`): types, conversions, comparisons, and truthiness.





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

2. Read `python/ds-60day/companion-guides/day03_control_flow_exceptions.md`, then open `python/ds-60day/notebooks/day03_control_flow_exceptions.ipynb` from the repository
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

**Lesson outcome:** use day 3 — control flow, truthiness, and exceptions to practice branch selection, loop decisions, and narrow exception boundaries
and explain the evidence produced by your code.
<!-- END HOW TO RUN -->

<!-- BEGIN BEGINNER DEEP DIVE -->
## Beginner deep dive — build the idea before the syntax

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

### Worked example 1 — Order specific branches before general branches

Classify a value after validating its domain. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
def classify_score(score: int) -> str:
    if not 0 <= score <= 100:
        raise ValueError("score must be between 0 and 100")
    if score >= 90:
        return "distinction"
    if score >= 60:
        return "pass"
    return "fail"

[classify_score(value) for value in (42, 75, 95)]
```

**Expected observation**

```text
`['fail', 'pass', 'distinction']`. The guard rejects out-of-domain values before classification.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### Worked example 2 — Protect only the fallible conversion

Let unrelated programming errors remain visible. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
def parse_count(text: str) -> int | None:
    try:
        count = int(text.strip())
    except ValueError:
        return None
    else:
        return count

[parse_count(text) for text in (" 12 ", "twelve")]
```

**Expected observation**

```text
`[12, None]`. Only invalid integer text is converted into the chosen sentinel.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### A debugging routine for this topic

When the output differs from your prediction, use this order:

1. Trace conditions from top to bottom and mark the first one that becomes true.
2. Move validation before classification when impossible values enter normal branches.
3. Shrink a large `try` block until it contains only the operation with the expected failure.
4. Replace bare `except:` or `except Exception:` with the narrow type you can recover from.

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

**Useful alternative:** Return a sentinel only when absence is part of the function's contract; otherwise raise a specific exception and let the caller decide.

**Boundary to remember:** Boundary values such as 0, 1, 59, 60, 89, 90, and 100 expose gaps and overlaps in ordered conditions.
<!-- END BEGINNER DEEP DIVE -->

## Vocabulary and mental model

- **Branch:** one possible route through a program.
- **Condition:** an expression interpreted as true or false.
- **Loop invariant:** a fact that remains true as a loop progresses.
- **Exception:** an object that interrupts normal execution when an operation
  cannot satisfy its contract.
- **Raise:** signal a failure; **catch:** handle a specific failure.
- **`else`/`finally`:** exception `else` runs only after success; `finally` runs
  whether the operation succeeds or fails.

Treat exceptions as structured failure information, not as a substitute for all
branching.

## Worked example

```python
def parse_positive_int(raw: str) -> int:
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"expected an integer, received {raw!r}") from exc

    if value < 0:
        raise ValueError("value must be non-negative")
    return value
```

The conversion failure and domain-rule failure have different causes. The
messages make both diagnosable.

## Exercises and progressive hints

Each item is a complete mini-contract. Before writing code, copy its input,
expected behavior, constraints, and verification into your work cell. A
result is not complete merely because it “looks right”; run the stated
assertion or inspection and explain what it proves.

1. Print FizzBuzz for every integer from 1 through 30 inclusive. **Rules:** multiples of both 3 and 5 print `FizzBuzz`; only 3 prints `Fizz`; only 5 prints `Buzz`; all others print the number. **Constraints:** use one ordered `if`/`elif`/`else` chain.
   **Verify:** positions 3, 5, 15, 16, and 30 are correct and exactly 30 lines are produced.

2. Write `parse_age(text)` that returns an integer for valid integer text and returns `None` only when conversion raises `ValueError`. **Constraints:** put only `int(text)` inside `try`; do not use a bare `except`.
   **Verify:** test `'42'`, `' 7 '`, and `'seven'`, then explain which path uses `else`.

3. Define `NegativeMeasurementError` as a subclass of `ValueError`, then write `validate_measurement(value)` that returns non-negative values unchanged and raises your exception for `-0.1`.
   **Verify:** show one normal return and catch the exact custom type in a small demonstration; do not catch it inside the validator.

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
6. **Implementation:** Implement `classify_score(score)` returning fail/pass/distinction and reject scores outside 0–100 with `ValueError`.
   **Progressive hint:** Validate the domain before choosing a result branch.
   **Verify:** Assert representative scores return `fail`, `pass`, and `distinction`, then assert `-1` and `101` each raise `ValueError`.
7. **Debugging:** Replace a bare `except:` around parsing and calculation with the narrowest useful handler, while allowing programming errors to surface.
   **Progressive hint:** Keep only the conversion inside the protected block.
   **Verify:** Show invalid integer text is handled while a deliberate unrelated `TypeError` still reaches the test; keep only conversion inside `try`.
8. **Edge case and explanation:** Design `safe_ratio(numerator, denominator)` for a zero denominator. Choose between raising, returning `None`, or a default and justify it.
   **Progressive hint:** A reusable library function usually should not invent a numeric result.
   **Verify:** Test a nonzero ratio and a zero denominator; assert the chosen zero policy exactly and explain why no fabricated numeric answer leaks through.

Before opening the reference solution, write one sentence explaining
which contract or mental model each result confirms.

## Self-check

- Why does branch order matter in FizzBuzz?
- When should a loop use `break` versus a condition in `while`?
- Why is `except Exception:` usually too broad?
- What information is preserved by `raise NewError(...) from exc`?

Expected behavior: FizzBuzz has exactly 30 outputs, invalid numeric text is
reported without hiding unrelated bugs, and negative values raise the custom
exception.

## Common pitfalls and diagnosis

- **FizzBuzz never prints the combined case:** inspect branch order.
- **An infinite `while` loop:** identify which statement must change the loop
  condition; interrupt the notebook kernel if necessary.
- **Errors disappear silently:** never use a bare `except: pass`; log, return a
  documented fallback, or re-raise.
- **`UnboundLocalError` after `try`:** a variable was assigned only on the
  success path. Return from each branch or initialize deliberately.
- **The wrong exception is caught:** reproduce the smallest failing expression
  and inspect the traceback's final line.

## Continue

- [Open the learner notebook](../notebooks/day03_control_flow_exceptions.ipynb)
- [Check the separate solution](../solutions/day03_control_flow_exceptions/day03_solutions.md)
- [Next: Day 4 — Loops, comprehensions, and generators](day04_loops_comprehensions_generators.md)

## Ask Codex about this lesson

Codex coaching is optional; the guide and notebook above contain the full
lesson. If you want a patient tutor, copy this prompt from the repository
root:

```text
Use $guide-ds60sqlpy-learning to tutor me through `python-03`
(Day 3 — Control Flow, Truthiness, and Exceptions). I am a complete beginner. Emphasize branch selection, loop decisions, and narrow exception boundaries.
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
