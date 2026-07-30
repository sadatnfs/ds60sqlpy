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

1. Print FizzBuzz for 1 through 30. **Hint:** test the most specific case
   (divisible by both numbers) before either individual case.
2. Parse user input while handling `ValueError`. **Hint:** keep only the
   conversion inside `try`; code outside should not be accidentally swallowed.
3. Define an exception for negative inputs and raise it when encountered.
   **Hint:** subclass `ValueError` because the type is acceptable but its value
   violates the function's contract.

### Additional mastery practice

Make branch order and exception boundaries deliberate. Catch only the failure that the current layer can interpret or repair.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

4. **Prediction:** Predict which branch handles 0, 9, and 12 when checks are ordered as `x % 2 == 0`, `x % 3 == 0`, then both. Explain the bug.
   **Progressive hint:** Only the first true branch runs; test the most specific rule first.
5. **Tracing:** Trace `try/except/else/finally` for a successful integer parse and for invalid text. Which clauses run in each path?
   **Progressive hint:** `else` follows success; `finally` runs in both cases.
6. **Implementation:** Implement `classify_score(score)` returning fail/pass/distinction and reject scores outside 0–100 with `ValueError`.
   **Progressive hint:** Validate the domain before choosing a result branch.
7. **Debugging:** Replace a bare `except:` around parsing and calculation with the narrowest useful handler, while allowing programming errors to surface.
   **Progressive hint:** Keep only the conversion inside the protected block.
8. **Edge case and explanation:** Design `safe_ratio(numerator, denominator)` for a zero denominator. Choose between raising, returning `None`, or a default and justify it.
   **Progressive hint:** A reusable library function usually should not invent a numeric result.

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
