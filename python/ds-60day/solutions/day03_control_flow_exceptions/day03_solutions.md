# Day 03 — Solutions: Control Flow, Truthiness, and Exceptions

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

The solution is not a typing template. Read the learner contract, predict
the result, then compare decisions and evidence. The central mental model is
**branch selection, loop decisions, and narrow exception boundaries**.

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

### Vocabulary used in the worked answers

- **condition:** an expression evaluated for truthiness.
- **branch:** one possible block selected by a condition.
- **guard clause:** an early check that rejects or handles an invalid case.
- **exception:** an object representing a failure that interrupts normal flow.
- **raise:** to deliberately signal an exception.
- **handler:** an `except` block for a named exception type.

### Reference pattern 1 — Order specific branches before general branches

Classify a value after validating its domain.

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

**Expected observation:** `['fail', 'pass', 'distinction']`. The guard rejects out-of-domain values before classification.

### Reference pattern 2 — Protect only the fallible conversion

Let unrelated programming errors remain visible.

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

**Expected observation:** `[12, None]`. Only invalid integer text is converted into the chosen sentinel.

## Exercise-by-exercise reasoning map

The numbering and learner contracts below match the guide and notebook.
Each entry explains what to reason about, how to inspect the worked code,
an alternative, an edge case, and the evidence required for completion.

### Exercise 1 — reasoning, alternatives, and proof

**Learner contract:** Print FizzBuzz for every integer from 1 through 30 inclusive. **Rules:** multiples of both 3 and 5 print `FizzBuzz`; only 3 prints `Fizz`; only 5 prints `Buzz`; all others print the number. **Constraints:** use one ordered `if`/`elif`/`else` chain. **Verify:** positions 3, 5, 15, 16, and 30 are correct and exactly 30 lines are produced.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies branch selection, loop decisions, and narrow exception boundaries.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Return a sentinel only when absence is part of the function's contract; otherwise raise a specific exception and let the caller decide.

**Edge case:** Boundary values such as 0, 1, 59, 60, 89, 90, and 100 expose gaps and overlaps in ordered conditions.

**Solution evidence to inspect:** positions 3, 5, 15, 16, and 30 are correct and exactly 30 lines are produced.

### Exercise 2 — reasoning, alternatives, and proof

**Learner contract:** Write `parse_age(text)` that returns an integer for valid integer text and returns `None` only when conversion raises `ValueError`. **Constraints:** put only `int(text)` inside `try`; do not use a bare `except`. **Verify:** test `'42'`, `' 7 '`, and `'seven'`, then explain which path uses `else`.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies branch selection, loop decisions, and narrow exception boundaries.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Return a sentinel only when absence is part of the function's contract; otherwise raise a specific exception and let the caller decide.

**Edge case:** Boundary values such as 0, 1, 59, 60, 89, 90, and 100 expose gaps and overlaps in ordered conditions.

**Solution evidence to inspect:** test `'42'`, `' 7 '`, and `'seven'`, then explain which path uses `else`.

### Exercise 3 — reasoning, alternatives, and proof

**Learner contract:** Define `NegativeMeasurementError` as a subclass of `ValueError`, then write `validate_measurement(value)` that returns non-negative values unchanged and raises your exception for `-0.1`. **Verify:** show one normal return and catch the exact custom type in a small demonstration; do not catch it inside the validator.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies branch selection, loop decisions, and narrow exception boundaries.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Return a sentinel only when absence is part of the function's contract; otherwise raise a specific exception and let the caller decide.

**Edge case:** Boundary values such as 0, 1, 59, 60, 89, 90, and 100 expose gaps and overlaps in ordered conditions.

**Solution evidence to inspect:** show one normal return and catch the exact custom type in a small demonstration; do not catch it inside the validator.

### Exercise 4 — reasoning, alternatives, and proof

**Learner contract:** **Prediction:** Predict which branch handles 0, 9, and 12 when checks are ordered as `x % 2 == 0`, `x % 3 == 0`, then both. Explain the bug. **Progressive hint:** Only the first true branch runs; test the most specific rule first. **Verify:** Record the branch selected for `0`, `9`, and `12` before/after reordering; confirm the repaired `12` reaches the combined rule.

**Reasoning before code:** Evaluate the expression or state transition by hand first. Name the input state, the next operation, and the exact evidence that would falsify the prediction while applying branch selection, loop decisions, and narrow exception boundaries.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Return a sentinel only when absence is part of the function's contract; otherwise raise a specific exception and let the caller decide.

**Edge case:** Boundary values such as 0, 1, 59, 60, 89, 90, and 100 expose gaps and overlaps in ordered conditions.

**Solution evidence to inspect:** Record the branch selected for `0`, `9`, and `12` before/after reordering; confirm the repaired `12` reaches the combined rule.

### Exercise 5 — reasoning, alternatives, and proof

**Learner contract:** **Tracing:** Trace `try/except/else/finally` for a successful integer parse and for invalid text. Which clauses run in each path? **Progressive hint:** `else` follows success; `finally` runs in both cases. **Verify:** Use a four-column trace for `try`, `except`, `else`, and `finally` on valid/invalid text; each clause's executed flag must match the language rules.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the branch selection, loop decisions, and narrow exception boundaries model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Return a sentinel only when absence is part of the function's contract; otherwise raise a specific exception and let the caller decide.

**Edge case:** Boundary values such as 0, 1, 59, 60, 89, 90, and 100 expose gaps and overlaps in ordered conditions.

**Solution evidence to inspect:** Use a four-column trace for `try`, `except`, `else`, and `finally` on valid/invalid text; each clause's executed flag must match the language rules.

### Exercise 6 — reasoning, alternatives, and proof

**Learner contract:** **Implementation:** Implement `classify_score(score)` returning fail/pass/distinction and reject scores outside 0–100 with `ValueError`. **Progressive hint:** Validate the domain before choosing a result branch. **Verify:** Assert representative scores return `fail`, `pass`, and `distinction`, then assert `-1` and `101` each raise `ValueError`.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies branch selection, loop decisions, and narrow exception boundaries.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Return a sentinel only when absence is part of the function's contract; otherwise raise a specific exception and let the caller decide.

**Edge case:** Boundary values such as 0, 1, 59, 60, 89, 90, and 100 expose gaps and overlaps in ordered conditions.

**Solution evidence to inspect:** Assert representative scores return `fail`, `pass`, and `distinction`, then assert `-1` and `101` each raise `ValueError`.

### Exercise 7 — reasoning, alternatives, and proof

**Learner contract:** **Debugging:** Replace a bare `except:` around parsing and calculation with the narrowest useful handler, while allowing programming errors to surface. **Progressive hint:** Keep only the conversion inside the protected block. **Verify:** Show invalid integer text is handled while a deliberate unrelated `TypeError` still reaches the test; keep only conversion inside `try`.

**Reasoning before code:** Reproduce the bad behavior on the smallest input, state the violated contract, make one repair, and rerun both the failing boundary and a normal case. Keep the diagnosis grounded in branch selection, loop decisions, and narrow exception boundaries.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Return a sentinel only when absence is part of the function's contract; otherwise raise a specific exception and let the caller decide.

**Edge case:** Boundary values such as 0, 1, 59, 60, 89, 90, and 100 expose gaps and overlaps in ordered conditions.

**Solution evidence to inspect:** Show invalid integer text is handled while a deliberate unrelated `TypeError` still reaches the test; keep only conversion inside `try`.

### Exercise 8 — reasoning, alternatives, and proof

**Learner contract:** **Edge case and explanation:** Design `safe_ratio(numerator, denominator)` for a zero denominator. Choose between raising, returning `None`, or a default and justify it. **Progressive hint:** A reusable library function usually should not invent a numeric result. **Verify:** Test a nonzero ratio and a zero denominator; assert the chosen zero policy exactly and explain why no fabricated numeric answer leaks through.

**Reasoning before code:** Turn the ambiguous boundary into an explicit contract before coding. Test values immediately below, at, and above the boundary and explain how the result follows from branch selection, loop decisions, and narrow exception boundaries.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Return a sentinel only when absence is part of the function's contract; otherwise raise a specific exception and let the caller decide.

**Edge case:** Boundary values such as 0, 1, 59, 60, 89, 90, and 100 expose gaps and overlaps in ordered conditions.

**Solution evidence to inspect:** Test a nonzero ratio and a zero denominator; assert the chosen zero policy exactly and explain why no fabricated numeric answer leaks through.
<!-- END BEGINNER SOLUTION REVIEW -->

This guide walks through each exercise with line‑by‑line explanations and beginner‑friendly reasoning. Where useful, we show multiple correct approaches and discuss trade‑offs.

Prereqs
- You can run a Python script or a REPL cell.
- You know how to read error messages and fix simple typos.

Contents
- Exercise 1: FizzBuzz for 1..30 (with clear if/elif ordering)
- Exercise 2: Safe input parsing with try/except
- Exercise 3: Custom exception for negative numbers
- More Practice (from Companion Guide): parse_int with custom ParseError; robust file reading with helpful error messages

---

Exercise 1 — FizzBuzz for 1..30
Goal: For numbers 1..30, print:
- "fizzbuzz" if divisible by 3 and 5
- "fizz" if divisible by 3
- "buzz" if divisible by 5
- otherwise the number itself

Why the order matters: If you check 3 or 5 first, you’ll print "fizz" for 15 and never reach the 3-and-5 case. So check the most specific case (both) first.

Code
```python
for n in range(1, 31):                # 1) iterate n through 1..30
    if n % 15 == 0:                    # 2) combined case first (3*5 = 15)
        print("fizzbuzz")              # 3) divisible by both 3 and 5
    elif n % 3 == 0:                   # 4) divisible by 3 only
        print("fizz")
    elif n % 5 == 0:                   # 5) divisible by 5 only
        print("buzz")
    else:
        print(n)                       # 6) otherwise print the number
```
Notes
- n % 15 == 0 is equivalent to (n % 3 == 0 and n % 5 == 0) but a bit shorter.
- You could also build a string dynamically, which generalizes better:

Alternative (string build)
```python
for n in range(1, 31):
    out = ""                             # start empty
    if n % 3 == 0:
        out += "fizz"                    # append fizz when divisible by 3
    if n % 5 == 0:
        out += "buzz"                    # append buzz when divisible by 5
    print(out or n)                      # out if non-empty else n
```
Trade‑offs
- The if/elif chain is explicit and easy to read.
- The string‑build approach scales to more rules (just add more appends).

---

Exercise 2 — Wrap input parsing with try/except
Goal: Read a number from the user; handle non‑numeric input gracefully.

Key idea: EAFP (Easier to Ask Forgiveness than Permission). Try the parse; handle the error if it fails.

Code
```python
def read_int(prompt: str = "Enter an integer: ") -> int:
    while True:                          # 1) loop until we can return a valid int
        raw = input(prompt)              # 2) get a string from the user
        try:
            value = int(raw)             # 3) attempt the parse
        except ValueError:               # 4) happens when raw like 'abc'
            print("That wasn't an integer. Please try again.")
            continue                     # 5) go back to the start of the loop
        else:
            return value                 # 6) success path; exit the function

# Demo
x = read_int()
print("You entered:", x)
```
Line‑by‑line
- while True: is a common input loop pattern; we break/return when valid.
- int(raw) can raise ValueError; catching it lets us show a friendly message.
- continue restarts the loop; return exits with the parsed integer.

Variation: single attempt that falls back to a default
```python
def read_int_once(prompt: str = "Enter an integer: ", default: int | None = None) -> int | None:
    raw = input(prompt)
    try:
        return int(raw)
    except ValueError:
        print("Invalid integer.")
        return default
```

---

Exercise 3 — Custom exception for negative numbers
Goal: Create and use a domain‑specific exception that triggers when an input is negative.

Why custom exceptions: They make error intent obvious and are easy to catch specifically.

Code
```python
class NegativeNumberError(ValueError):
    """Raised when a negative number is encountered where it is not allowed."""


def ensure_non_negative(x: int | float) -> int | float:
    if x < 0:                                # 1) guard clause: fail fast on invalid input
        raise NegativeNumberError(f"Negative value not allowed: {x}")
    return x                                 # 2) otherwise pass the value through

# Demo usage
for val in [5, 0, -2]:
    try:
        ok = ensure_non_negative(val)
        print("OK:", ok)
    except NegativeNumberError as e:
        print("Error:", e)
```
Notes
- Subclassing ValueError communicates that this is a value‑related problem.
- Guard clauses keep the happy path unindented and readable.

---

More Practice (from Companion Guide)

A) parse_int(s) that raises a custom ParseError on failure
```python
class ParseError(ValueError):
    """Raised when parsing a string to an integer fails."""


def parse_int(s: str) -> int:
    try:
        return int(s)
    except ValueError as e:                   # 1) capture original error for context
        # 2) raise our domain error with actionable message and keep context via 'from'
        raise ParseError(f"Could not parse integer from {s!r}") from e

# Tests
assert parse_int("42") == 42
try:
    parse_int("forty-two")
except ParseError as pe:
    print("Caught ParseError:", pe)
```
Line‑by‑line
- !r prints the repr of the string, helpful for seeing spaces/escapes.
- raise ... from e keeps the original traceback for debugging.

B) Robust file read with helpful messages
```python
from pathlib import Path
import json


def load_json(path: str | Path) -> dict:
    try:
        text = Path(path).read_text(encoding="utf-8")        # 1) may raise FileNotFoundError/PermissionError
        return json.loads(text)                                # 2) may raise JSONDecodeError
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {path}")
    except PermissionError:
        raise PermissionError(f"Permission denied reading: {path}")
    except json.JSONDecodeError as e:
        # 3) show where parsing failed (line/column)
        raise ValueError(f"Invalid JSON in {path}: line {e.lineno}, col {e.colno}") from e

# Demo
# data = load_json("config.json")
```
Tips
- Catch the narrowest exception you can handle usefully.
- Provide messages that tell the user what to do next (fix path, fix JSON).

---

Check Your Understanding
- Why check the combined case first in FizzBuzz?
- When do you use try/except/else/finally?
- What benefits do custom exceptions provide in larger programs?

---

## Expanded mastery lab solutions

Make branch order and exception boundaries deliberate. Catch only the failure that the current layer can interpret or repair.

Read the reasoning before the code. Inline comments explain ownership, boundary choices, and why each check exists; assertions turn the stated contract into executable evidence.

### Practices 1–2 — Branch and exception traces

The combined-divisibility check must come first; otherwise values such as 12
are consumed by the even branch. On successful parsing, `else` and `finally`
run. On `ValueError`, `except` and `finally` run.

### Practices 3–5 — Explicit contracts

```python
def classify_score(score: float) -> str:
    """Classify a score whose valid domain is the closed interval 0..100."""

    if not 0 <= score <= 100:
        raise ValueError("score must be between 0 and 100")
    if score >= 80:
        return "distinction"
    if score >= 60:
        return "pass"
    return "fail"


assert classify_score(80) == "distinction"  # Boundary belongs to upper band.
assert classify_score(59.9) == "fail"


def parse_count(text: str) -> int | None:
    """Return None only when text is not a valid integer."""

    try:
        # Keep the try block narrow: later calculations may reveal real bugs.
        value = int(text)
    except ValueError:
        return None
    else:
        return value


def safe_ratio(numerator: float, denominator: float) -> float:
    """Return a ratio, rejecting an undefined zero-denominator operation."""

    if denominator == 0:
        raise ZeroDivisionError("denominator must be non-zero")
    return numerator / denominator


assert parse_count("12") == 12
assert parse_count("twelve") is None
assert safe_ratio(3, 4) == 0.75
```

Raising in `safe_ratio` preserves the fact that the result is undefined. A
calling application can translate that exception into `None` or a user message
if its own contract calls for one.
