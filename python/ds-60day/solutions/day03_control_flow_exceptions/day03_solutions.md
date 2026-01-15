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
