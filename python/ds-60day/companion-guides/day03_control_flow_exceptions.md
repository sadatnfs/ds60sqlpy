# Day 3 — Control Flow, Truthiness, and Exceptions (Companion Guide)

This guide provides in‑depth context for Day 3.

## Learning objectives
- Master `if/elif/else` and understand Python’s truthiness rules
- Write robust loops (`for`, `while`) and know when to break/continue
- Handle errors with `try/except/else/finally` and raise your own exceptions
- Design user‑friendly error messages and input validation patterns

## Why this matters
Control flow is how you express logic. Good exception handling prevents silent failures and turns confusing stack traces into helpful guidance. Robust apps validate and fail fast with clear messages.

## Mental models
- EAFP vs LBYL: Python favors EAFP (Easier to Ask Forgiveness than Permission). Try the operation; catch exceptions if it fails.
- Exceptions as control flow: Don’t abuse them for normal branching, but use them to signal error states and invalid assumptions clearly.
- Guard clauses: Validate at the top of functions, raise early with informative messages.

## Conditionals and truthiness
```python
# Truthiness recap
if '':
    ...   # falsy
if 'hi':
    ...   # truthy
if 0:
    ...   # falsy
if 42:
    ...   # truthy

# Chained comparisons
if 0 < x < 10:
    ...
```
Prefer clear boolean expressions; avoid double negatives.

## Loops and patterns
```python
# Iterate over sequences
for item in items:
    ...

# Enumerate with indices
for i, item in enumerate(items):
    ...

# While loop with sentinel
while line := read():   # Python 3.8+ walrus
    process(line)

# Early exit
for x in xs:
    if predicate(x):
        result = x
        break
else:
    result = None  # runs when loop completes without break
```
Use `for … else` to detect the “not found” case without a separate flag.

## Exceptions: catching and raising
```python
def safe_divide(a: float, b: float) -> float:
    if b == 0:
        raise ZeroDivisionError("b must not be 0")
    return a / b

try:
    y = safe_divide(10, 0)
except ZeroDivisionError as e:
    print(f"Error: {e}")
else:
    print("OK, result:", y)
finally:
    print("Cleanup (if needed)")
```
Use `else` for code that should run only if no exception was raised.

## Custom exceptions and validation
Create domain‑specific exceptions for clarity:
```python
class InvalidEmailError(ValueError):
    """Raised when an email fails minimum validation."""

def validate_email(email: str) -> None:
    if "@" not in email:
        raise InvalidEmailError("Missing @ in email")
```
Give actionable messages (what was wrong + how to fix). Avoid swallowing exceptions silently.

## Logging vs printing
- Use `logging` for operational messages; `print` for quick demos
- Log levels: DEBUG < INFO < WARNING < ERROR < CRITICAL

## Common pitfalls
- Catching broad `Exception` everywhere: narrows diagnostics. Catch the narrowest type you can.
- Empty bare `except:` blocks: dangerous; they catch `KeyboardInterrupt` and more.
- Using exceptions for normal logic (e.g., exiting loops) when a boolean is clearer.

## Practice exercises
1) FizzBuzz with a twist: print “fizz” for multiples of 3, “buzz” for 5, “fizzbuzz” for 15, else the number, for 1..50.
2) Write a function `parse_int(s) -> int` that returns an `int` or raises a custom `ParseError` with the bad substring.
3) Wrap file reading in `try/except` and surface helpful messages (missing file, permission denied, invalid JSON).

## Stretch goals
- Write a context manager for timing a code block and logging the duration.
- Implement retry logic with exponential backoff for a flaky operation (e.g., simulated network call).

## Check your understanding
- When should you use `else` and `finally` in `try` blocks?
- Give an example where EAFP is nicer than LBYL (fewer race conditions / cleaner code).
- Why are bare `except:` blocks discouraged?

## Further reading
- Exceptions: https://docs.python.org/3/tutorial/errors.html
- Logging: https://docs.python.org/3/library/logging.html
