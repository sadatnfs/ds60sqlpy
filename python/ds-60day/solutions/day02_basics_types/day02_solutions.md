# Day 02 — Solutions: Variables and Core Types

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

These worked answers demonstrate **objects, names, built-in types, conversion, and truthiness**. Predict each named
result before comparing your attempt with its matching assertions.

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

### How to compare an answer

For this lesson's **objects, names, built-in types, conversion, and truthiness** model, follow the exact values from each learner contract through its function or expression to the assertion that proves the expected behavior; then change one boundary input and make that assertion fail once before accepting the answer.
<!-- END BEGINNER SOLUTION REVIEW -->

## Exercises 1–3 — Worked answers

### Exercise 1 — worked answer

**Learner contract:** Prompt twice with `input()` for numbers such as `12.5` and `7.25`, convert both strings to `float`, and print `19.75`. **Constraints:** display a short label with the result and do not concatenate the raw strings. **Verify:** first show that `type(input(...))` is `str`, then test whole-number and decimal text.

**Reasoning:** Implement this exact contract as written: Prompt twice with `input()` for numbers such as `12.5` and `7.25`, convert both strings to `float`, and print `19.75`. Constraints: display a short label with the result and do not concatenate the raw strings. Keep the prompt's named data and constraints visible in the code, then establish this specific result: first show that `type(input(...))` is `str`, then test whole-number and decimal text. That connects the answer to objects, names, built-in types, conversion, and truthiness.

```python
from collections.abc import Callable


def add_input_numbers(left_text: str, right_text: str) -> float:
    left = float(left_text.strip())
    right = float(right_text.strip())
    return left + right


def prompt_for_sum(read: Callable[[str], str] = input) -> float:
    left_text = read("First number: ")
    right_text = read("Second number: ")
    assert type(left_text) is str and type(right_text) is str
    result = add_input_numbers(left_text, right_text)
    print(f"Sum: {result}")
    return result


decimal_answers = iter(["12.5", "7.25"])
whole_answers = iter(["12", "7"])
assert prompt_for_sum(lambda _: next(decimal_answers)) == 19.75
assert prompt_for_sum(lambda _: next(whole_answers)) == 19.0
```

Calling `prompt_for_sum()` without an argument uses real `input()` twice.
Injecting a tiny reader supplies deterministic text during verification
while proving that parsing occurs before numeric addition.

**Verification evidence:** first show that `type(input(...))` is `str`, then test whole-number and decimal text.

### Exercise 2 — worked answer

**Learner contract:** Starting from `raw = ' Data Science '`, create a new value exactly equal to `'data science'`. **Constraints:** use string methods rather than slicing or a hard-coded replacement. **Verify:** assert the normalized result and show that `raw` itself is unchanged because strings are immutable.

**Reasoning:** Implement this exact contract as written: Starting from `raw = ' Data Science '`, create a new value exactly equal to `'data science'`. Constraints: use string methods rather than slicing or a hard-coded replacement. Keep the prompt's named data and constraints visible in the code, then establish this specific result: assert the normalized result and show that `raw` itself is unchanged because strings are immutable. That connects the answer to objects, names, built-in types, conversion, and truthiness.

```python
raw = "  Data Science  "
normalized = raw.strip().lower()

assert normalized == "data science"
assert raw == "  Data Science  "
```

Both methods return new strings. Rebinding `normalized` preserves the
raw evidence.

**Verification evidence:** assert the normalized result and show that `raw` itself is unchanged because strings are immutable.

### Exercise 3 — worked answer

**Learner contract:** Convert the text `'3.14'` to a floating-point number, double it, and format the result as `6.28`. **Constraints:** keep the original text in one name and the numeric value in another. **Verify:** assert the parsed value has type `float` and explain why `'3.14' * 2` is not numeric multiplication.

**Reasoning:** Implement this exact contract as written: Convert the text `'3.14'` to a floating-point number, double it, and format the result as `6.28`. Constraints: keep the original text in one name and the numeric value in another. Keep the prompt's named data and constraints visible in the code, then establish this specific result: assert the parsed value has type `float` and explain why `'3.14' * 2` is not numeric multiplication. That connects the answer to objects, names, built-in types, conversion, and truthiness.

```python
raw_number = "3.14"
number = float(raw_number)
doubled = number * 2
displayed = f"{doubled:.2f}"

assert isinstance(number, float)
assert doubled == 6.28
assert displayed == "6.28"
assert raw_number == "3.14"
```

By contrast, `"3.14" * 2` repeats text and returns `"3.143.14"`.

**Verification evidence:** assert the parsed value has type `float` and explain why `'3.14' * 2` is not numeric multiplication.

## Exercises 4–8 — Expanded mastery answers

### Exercise 4 — answer contract

**Learner contract:** **Prediction:** Predict the value and type of `"7" * 2`, `7 / 2`, `7 // 2`, `bool("")`, and `bool("0")` before running them. **Progressive hint:** Operators follow operand types; non-empty strings are truthy. **Verify:** Create a table of predicted/actual value and type for all five expressions; every row must match, including `bool('0') is True`.

**Reasoning:** Predict this named state change before running it: Prediction: Predict the value and type of `"7" * 2`, `7 / 2`, `7 // 2`, `bool("")`, and `bool("0")` before running them. Progressive hint: Operators follow operand types; non-empty strings are truthy. Then compare the prediction with this proof target: Create a table of predicted/actual value and type for all five expressions; every row must match, including `bool('0') is True`. This makes objects, names, built-in types, conversion, and truthiness observable instead of relying on intuition.

**Evidence to locate in the grouped implementation:** Create a table of predicted/actual value and type for all five expressions; every row must match, including `bool('0') is True`.

### Exercise 5 — answer contract

**Learner contract:** **Tracing:** Trace `raw = ' 0042 '; cleaned = raw.strip(); number = int(cleaned)` and record the value/type after every assignment. **Progressive hint:** String methods return new strings; conversion constructs an integer. **Verify:** Record `repr(value)` and `type(value).__name__` after `raw`, `cleaned`, and `number`; confirm the original string still contains spaces.

**Reasoning:** Trace the concrete values in this contract one step at a time: Tracing: Trace `raw = ' 0042 '; cleaned = raw.strip(); number = int(cleaned)` and record the value/type after every assignment. Progressive hint: String methods return new strings; conversion constructs an integer. Record the named value, shape, label, or iterator position needed to establish: Record `repr(value)` and `type(value).__name__` after `raw`, `cleaned`, and `number`; confirm the original string still contains spaces. The trace exposes objects, names, built-in types, conversion, and truthiness directly.

**Evidence to locate in the grouped implementation:** Record `repr(value)` and `type(value).__name__` after `raw`, `cleaned`, and `number`; confirm the original string still contains spaces.

### Exercise 6 — answer contract

**Learner contract:** **Implementation:** Implement `parse_temperature(text)` so surrounding whitespace is accepted and the result is a float, then format one decimal place. **Progressive hint:** Keep parsing separate from f-string presentation. **Verify:** Assert whitespace inputs such as `' 32.5 '` return `32.5` and format as `'32.5'`; prove invalid text follows the documented exception path.

**Reasoning:** Implement this exact contract as written: Implementation: Implement `parse_temperature(text)` so surrounding whitespace is accepted and the result is a float, then format one decimal place. Progressive hint: Keep parsing separate from f-string presentation. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Assert whitespace inputs such as `' 32.5 '` return `32.5` and format as `'32.5'`; prove invalid text follows the documented exception path. That connects the answer to objects, names, built-in types, conversion, and truthiness.

**Evidence to locate in the grouped implementation:** Assert whitespace inputs such as `' 32.5 '` return `32.5` and format as `'32.5'`; prove invalid text follows the documented exception path.

### Exercise 7 — answer contract

**Learner contract:** **Debugging:** Repair `enabled = bool(raw)` for inputs such as `"true"`, `"false"`, and `" FALSE "`. Reject unknown spellings. **Progressive hint:** Normalize the text and compare explicit accepted tokens. **Verify:** Assert accepted case/whitespace variants map to the intended Booleans and that an unknown token such as `'yes-ish'` raises a specific `ValueError`.

**Reasoning:** Reproduce the exact failure described here before changing code: Debugging: Repair `enabled = bool(raw)` for inputs such as `"true"`, `"false"`, and `" FALSE "`. Reject unknown spellings. Progressive hint: Normalize the text and compare explicit accepted tokens. Preserve that failing case, repair the violated rule, and rerun the evidence named here: Assert accepted case/whitespace variants map to the intended Booleans and that an unknown token such as `'yes-ish'` raises a specific `ValueError`. The diagnosis depends on objects, names, built-in types, conversion, and truthiness.

**Evidence to locate in the grouped implementation:** Assert accepted case/whitespace variants map to the intended Booleans and that an unknown token such as `'yes-ish'` raises a specific `ValueError`.

### Exercise 8 — answer contract

**Learner contract:** **Edge case and explanation:** Model an optional discount where `None` means not supplied and `0.0` means supplied but zero. Explain why a truthiness check loses meaning. **Progressive hint:** Use `is None` when absence is distinct from a numeric zero. **Verify:** Test `None`, `0.0`, and `0.25` separately; assert the first is absent while the latter two remain supplied numeric discounts.

**Reasoning:** Make this boundary unambiguous in code: Edge case and explanation: Model an optional discount where `None` means not supplied and `0.0` means supplied but zero. Explain why a truthiness check loses meaning. Progressive hint: Use `is None` when absence is distinct from a numeric zero. Values below, at, and above the named boundary must produce the evidence Test `None`, `0.0`, and `0.25` separately; assert the first is absent while the latter two remain supplied numeric discounts. Those cases show how objects, names, built-in types, conversion, and truthiness behaves at its edge.

**Evidence to locate in the grouped implementation:** Test `None`, `0.0`, and `0.25` separately; assert the first is absent while the latter two remain supplied numeric discounts.

## Expanded mastery lab solutions

Separate parsing, calculation, and presentation. Predict a value's type before relying on an operator or truthiness rule.

### Shared implementation for Exercise 4 — Prediction

`"7" * 2` is the string `"77"`; `7 / 2` is the float `3.5`; `7 // 2` is
the integer `3`; `bool("")` is false; and `bool("0")` is true because the
string is non-empty.

### Shared implementation for Exercises 5–8 — Parse first, calculate second, present last

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
