# Day 02 — Solutions: Variables and Core Types

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

The solution is not a typing template. Read the learner contract, predict
the result, then compare decisions and evidence. The central mental model is
**objects, names, built-in types, conversion, and truthiness**.

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

### Vocabulary used in the worked answers

- **object:** a runtime value with a type, identity, and supported operations.
- **name:** an identifier that refers to an object.
- **type:** the category that defines a value's operations and behavior.
- **literal:** source syntax that directly creates a value, such as `42` or `'hi'`.
- **conversion:** constructing a value of one type from another representation.
- **truthiness:** the rule Python uses when a value appears in a Boolean context.

### Reference pattern 1 — Parse, calculate, then format

Keep representation changes separate from arithmetic.

```python
raw_quantity = " 3 "
raw_price = "4.50"
quantity = int(raw_quantity.strip())
price = float(raw_price)
total = quantity * price
(quantity, price, total, f"${total:.2f}")
```

**Expected observation:** `(3, 4.5, 13.5, '$13.50')`. The final string is presentation; `total` remains numeric.

### Reference pattern 2 — Make Boolean parsing explicit

Do not confuse a non-empty spelling with a Boolean value.

```python
raw_enabled = " FALSE "
normalized = raw_enabled.strip().lower()
enabled = normalized == "true"
(normalized, enabled, bool(raw_enabled))
```

**Expected observation:** `('false', False, True)`. `bool(raw_enabled)` is `True` because the original string contains characters.

## Exercise-by-exercise reasoning map

The numbering and learner contracts below match the guide and notebook.
Each entry explains what to reason about, how to inspect the worked code,
an alternative, an edge case, and the evidence required for completion.

### Exercise 1 — reasoning, alternatives, and proof

**Learner contract:** Prompt twice with `input()` for numbers such as `12.5` and `7.25`, convert both strings to `float`, and print `19.75`. **Constraints:** display a short label with the result and do not concatenate the raw strings. **Verify:** first show that `type(input(...))` is `str`, then test whole-number and decimal text.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies objects, names, built-in types, conversion, and truthiness.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Explicit conversions are usually clearer than relying on implicit coercion; a small parsing function is useful when accepted spellings form a real input contract.

**Edge case:** Empty text, whitespace-only text, `None`, zero, and non-ASCII text often reveal assumptions hidden by happy-path examples.

**Solution evidence to inspect:** first show that `type(input(...))` is `str`, then test whole-number and decimal text.

### Exercise 2 — reasoning, alternatives, and proof

**Learner contract:** Starting from `raw = ' Data Science '`, create a new value exactly equal to `'data science'`. **Constraints:** use string methods rather than slicing or a hard-coded replacement. **Verify:** assert the normalized result and show that `raw` itself is unchanged because strings are immutable.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies objects, names, built-in types, conversion, and truthiness.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Explicit conversions are usually clearer than relying on implicit coercion; a small parsing function is useful when accepted spellings form a real input contract.

**Edge case:** Empty text, whitespace-only text, `None`, zero, and non-ASCII text often reveal assumptions hidden by happy-path examples.

**Solution evidence to inspect:** assert the normalized result and show that `raw` itself is unchanged because strings are immutable.

### Exercise 3 — reasoning, alternatives, and proof

**Learner contract:** Convert the text `'3.14'` to a floating-point number, double it, and format the result as `6.28`. **Constraints:** keep the original text in one name and the numeric value in another. **Verify:** assert the parsed value has type `float` and explain why `'3.14' * 2` is not numeric multiplication.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies objects, names, built-in types, conversion, and truthiness.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Explicit conversions are usually clearer than relying on implicit coercion; a small parsing function is useful when accepted spellings form a real input contract.

**Edge case:** Empty text, whitespace-only text, `None`, zero, and non-ASCII text often reveal assumptions hidden by happy-path examples.

**Solution evidence to inspect:** assert the parsed value has type `float` and explain why `'3.14' * 2` is not numeric multiplication.

### Exercise 4 — reasoning, alternatives, and proof

**Learner contract:** **Prediction:** Predict the value and type of `"7" * 2`, `7 / 2`, `7 // 2`, `bool("")`, and `bool("0")` before running them. **Progressive hint:** Operators follow operand types; non-empty strings are truthy. **Verify:** Create a table of predicted/actual value and type for all five expressions; every row must match, including `bool('0') is True`.

**Reasoning before code:** Evaluate the expression or state transition by hand first. Name the input state, the next operation, and the exact evidence that would falsify the prediction while applying objects, names, built-in types, conversion, and truthiness.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Explicit conversions are usually clearer than relying on implicit coercion; a small parsing function is useful when accepted spellings form a real input contract.

**Edge case:** Empty text, whitespace-only text, `None`, zero, and non-ASCII text often reveal assumptions hidden by happy-path examples.

**Solution evidence to inspect:** Create a table of predicted/actual value and type for all five expressions; every row must match, including `bool('0') is True`.

### Exercise 5 — reasoning, alternatives, and proof

**Learner contract:** **Tracing:** Trace `raw = ' 0042 '; cleaned = raw.strip(); number = int(cleaned)` and record the value/type after every assignment. **Progressive hint:** String methods return new strings; conversion constructs an integer. **Verify:** Record `repr(value)` and `type(value).__name__` after `raw`, `cleaned`, and `number`; confirm the original string still contains spaces.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the objects, names, built-in types, conversion, and truthiness model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Explicit conversions are usually clearer than relying on implicit coercion; a small parsing function is useful when accepted spellings form a real input contract.

**Edge case:** Empty text, whitespace-only text, `None`, zero, and non-ASCII text often reveal assumptions hidden by happy-path examples.

**Solution evidence to inspect:** Record `repr(value)` and `type(value).__name__` after `raw`, `cleaned`, and `number`; confirm the original string still contains spaces.

### Exercise 6 — reasoning, alternatives, and proof

**Learner contract:** **Implementation:** Implement `parse_temperature(text)` so surrounding whitespace is accepted and the result is a float, then format one decimal place. **Progressive hint:** Keep parsing separate from f-string presentation. **Verify:** Assert whitespace inputs such as `' 32.5 '` return `32.5` and format as `'32.5'`; prove invalid text follows the documented exception path.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies objects, names, built-in types, conversion, and truthiness.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Explicit conversions are usually clearer than relying on implicit coercion; a small parsing function is useful when accepted spellings form a real input contract.

**Edge case:** Empty text, whitespace-only text, `None`, zero, and non-ASCII text often reveal assumptions hidden by happy-path examples.

**Solution evidence to inspect:** Assert whitespace inputs such as `' 32.5 '` return `32.5` and format as `'32.5'`; prove invalid text follows the documented exception path.

### Exercise 7 — reasoning, alternatives, and proof

**Learner contract:** **Debugging:** Repair `enabled = bool(raw)` for inputs such as `"true"`, `"false"`, and `" FALSE "`. Reject unknown spellings. **Progressive hint:** Normalize the text and compare explicit accepted tokens. **Verify:** Assert accepted case/whitespace variants map to the intended Booleans and that an unknown token such as `'yes-ish'` raises a specific `ValueError`.

**Reasoning before code:** Reproduce the bad behavior on the smallest input, state the violated contract, make one repair, and rerun both the failing boundary and a normal case. Keep the diagnosis grounded in objects, names, built-in types, conversion, and truthiness.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Explicit conversions are usually clearer than relying on implicit coercion; a small parsing function is useful when accepted spellings form a real input contract.

**Edge case:** Empty text, whitespace-only text, `None`, zero, and non-ASCII text often reveal assumptions hidden by happy-path examples.

**Solution evidence to inspect:** Assert accepted case/whitespace variants map to the intended Booleans and that an unknown token such as `'yes-ish'` raises a specific `ValueError`.

### Exercise 8 — reasoning, alternatives, and proof

**Learner contract:** **Edge case and explanation:** Model an optional discount where `None` means not supplied and `0.0` means supplied but zero. Explain why a truthiness check loses meaning. **Progressive hint:** Use `is None` when absence is distinct from a numeric zero. **Verify:** Test `None`, `0.0`, and `0.25` separately; assert the first is absent while the latter two remain supplied numeric discounts.

**Reasoning before code:** Turn the ambiguous boundary into an explicit contract before coding. Test values immediately below, at, and above the boundary and explain how the result follows from objects, names, built-in types, conversion, and truthiness.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Explicit conversions are usually clearer than relying on implicit coercion; a small parsing function is useful when accepted spellings form a real input contract.

**Edge case:** Empty text, whitespace-only text, `None`, zero, and non-ASCII text often reveal assumptions hidden by happy-path examples.

**Solution evidence to inspect:** Test `None`, `0.0`, and `0.25` separately; assert the first is absent while the latter two remain supplied numeric discounts.
<!-- END BEGINNER SOLUTION REVIEW -->

This solution provides code and commentary for each exercise.

Exercise 1: percent(n, total) -> '37.5%'

Why: Formatting is presentation logic; protect against division by zero; use round or format spec.

```python
def percent(n: float, total: float) -> str:
    if total == 0:
        return '0.0%'
    pct = (n / total) * 100
    return f"{pct:.1f}%"

assert percent(3, 8) == '37.5%'
assert percent(0, 10) == '0.0%'
```

Exercise 2: Slugify '  Data Science  ' to 'data-science'

Why: Normalize whitespace and case before replacement; strings are immutable so each method returns a new string.

```python
s = '  Data Science  '
slug = s.strip().lower().replace(' ', '-')
assert slug == 'data-science'
```

Exercise 3: Read two numbers as strings, convert safely, print sum/product

Why: Defensive parsing—report invalid inputs rather than crashing; f-strings for readable output.

```python
def to_int(s: str) -> int | None:
    try:
        return int(s)
    except ValueError:
        return None

raw_a, raw_b = '12', '7'  # replace with input() in interactive flows
A, B = to_int(raw_a), to_int(raw_b)
if A is None or B is None:
    print('Invalid number input')
else:
    print(f"sum={A + B}")
    print(f"product={A * B}")
```

Stretch: safe_float

```python
import math

def safe_float(s: str, default: float = math.nan) -> float:
    try:
        return float(s)
    except ValueError:
        print(f"bad float input: {s!r}")
        return default
```

---

## Expanded mastery lab solutions

Separate parsing, calculation, and presentation. Predict a value's type before relying on an operator or truthiness rule.

Read the reasoning before the code. Inline comments explain ownership, boundary choices, and why each check exists; assertions turn the stated contract into executable evidence.

### Practice 1 — Prediction

`"7" * 2` is the string `"77"`; `7 / 2` is the float `3.5`; `7 // 2` is
the integer `3`; `bool("")` is false; and `bool("0")` is true because the
string is non-empty.

### Practices 2–5 — Parse first, calculate second, present last

```python
raw = " 0042 "
cleaned = raw.strip()       # "0042" is still text; raw is unchanged.
number = int(cleaned)       # int parses the compatible text as 42.
assert (raw, cleaned, number) == (" 0042 ", "0042", 42)


def parse_temperature(text: str) -> float:
    """Parse temperature text; ValueError honestly reports invalid input."""

    return float(text.strip())


temperature = parse_temperature(" 21.25 ")
label = f"{temperature:.1f} °C"  # Formatting does not alter temperature.
assert label == "21.2 °C"


def parse_bool(text: str) -> bool:
    """Accept a deliberately small, documented boolean vocabulary."""

    normalized = text.strip().casefold()
    if normalized in {"true", "yes", "1"}:
        return True
    if normalized in {"false", "no", "0"}:
        return False
    raise ValueError(f"unknown boolean value: {text!r}")


assert parse_bool(" FALSE ") is False

discount: float | None = 0.0
if discount is None:
    status = "not supplied"
else:
    status = f"supplied: {discount:.1%}"
assert status == "supplied: 0.0%"
```

`if discount:` would group `0.0` with absence, even though those states have
different business meanings.
