# Day 02 — Solutions: Variables and Core Types

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

## Exercise-by-exercise reference

Every numbered learner exercise has a matching entry here. The original
worked examples remain above; the expanded answers below add heavily
commented code, explicit reasoning, and executable checks.

### Exercise 1 — Original lesson practice

**Prompt:** Read two numbers with `input()` and print their sum. **Hint:** inspect `type(input(...))`, then convert both values before adding.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 2 — Original lesson practice

**Prompt:** Transform `" Data Science "` into lowercase text without surrounding spaces. **Hint:** string methods can be chained because each returns a new string.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 3 — Original lesson practice

**Prompt:** Convert `"3.14"` to a float and multiply it by two. **Hint:** do not change the original text just to make the calculation possible. For transfer practice, the separate solution uses parallel tasks: format a percentage, build a slug, and parse two numeric strings. Those are intentionally not line-for-line copies of the notebook answers.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 4 — Prediction

**Prompt:** Predict the value and type of `"7" * 2`, `7 / 2`, `7 // 2`, `bool("")`, and `bool("0")` before running them.

**Reasoning checkpoint:** Operators follow operand types; non-empty strings are truthy. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 5 — Tracing

**Prompt:** Trace `raw = ' 0042 '; cleaned = raw.strip(); number = int(cleaned)` and record the value/type after every assignment.

**Reasoning checkpoint:** String methods return new strings; conversion constructs an integer. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 6 — Implementation

**Prompt:** Implement `parse_temperature(text)` so surrounding whitespace is accepted and the result is a float, then format one decimal place.

**Reasoning checkpoint:** Keep parsing separate from f-string presentation. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 7 — Debugging

**Prompt:** Repair `enabled = bool(raw)` for inputs such as `"true"`, `"false"`, and `" FALSE "`. Reject unknown spellings.

**Reasoning checkpoint:** Normalize the text and compare explicit accepted tokens. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 8 — Edge case and explanation

**Prompt:** Model an optional discount where `None` means not supplied and `0.0` means supplied but zero. Explain why a truthiness check loses meaning.

**Reasoning checkpoint:** Use `is None` when absence is distinct from a numeric zero. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

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
