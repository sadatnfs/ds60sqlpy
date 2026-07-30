# Day 03 — Solutions: Control Flow, Truthiness, and Exceptions

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

## Exercise-by-exercise reference

Every numbered learner exercise has a matching entry here. The original
worked examples remain above; the expanded answers below add heavily
commented code, explicit reasoning, and executable checks.

### Exercise 1 — Original lesson practice

**Prompt:** Print FizzBuzz for 1 through 30. **Hint:** test the most specific case (divisible by both numbers) before either individual case.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 2 — Original lesson practice

**Prompt:** Parse user input while handling `ValueError`. **Hint:** keep only the conversion inside `try`; code outside should not be accidentally swallowed.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 3 — Original lesson practice

**Prompt:** Define an exception for negative inputs and raise it when encountered. **Hint:** subclass `ValueError` because the type is acceptable but its value violates the function's contract.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 4 — Prediction

**Prompt:** Predict which branch handles 0, 9, and 12 when checks are ordered as `x % 2 == 0`, `x % 3 == 0`, then both. Explain the bug.

**Reasoning checkpoint:** Only the first true branch runs; test the most specific rule first. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 5 — Tracing

**Prompt:** Trace `try/except/else/finally` for a successful integer parse and for invalid text. Which clauses run in each path?

**Reasoning checkpoint:** `else` follows success; `finally` runs in both cases. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 6 — Implementation

**Prompt:** Implement `classify_score(score)` returning fail/pass/distinction and reject scores outside 0–100 with `ValueError`.

**Reasoning checkpoint:** Validate the domain before choosing a result branch. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 7 — Debugging

**Prompt:** Replace a bare `except:` around parsing and calculation with the narrowest useful handler, while allowing programming errors to surface.

**Reasoning checkpoint:** Keep only the conversion inside the protected block. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 8 — Edge case and explanation

**Prompt:** Design `safe_ratio(numerator, denominator)` for a zero denominator. Choose between raising, returning `None`, or a default and justify it.

**Reasoning checkpoint:** A reusable library function usually should not invent a numeric result. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

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
