# Day 2 Solutions: Variables and Core Types

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

For each answer, follow the exact values from the learner contract through
each assignment to the assertion or printed output that proves the behavior.
Then change one input, such as the typed text or the discount, and make one
assertion fail once before accepting the answer.
<!-- END BEGINNER SOLUTION REVIEW -->

## Exercises 1-3: Worked answers

### Exercise 1: worked answer

**Learner contract:** Treat `left_text = "12.5"` and `right_text = "7.25"` as two values a user typed. Convert both to `float`, add them, and print `Sum: 19.75`. **Constraints:** keep the text values and the numbers in different names, and do not join the strings. **Verify:** show that `type(left_text).__name__` is `'str'` before conversion and assert that the sum equals `19.75`; then change the texts to `"12"` and `"7"` and confirm the output is `Sum: 19.0`.

**Reasoning:** The two strings stand in for what `input()` would return, so
the program must convert before it adds. Keeping `left_text` and `left` under
different names means the original text is still available when a value
looks wrong. The common wrong answer is `left_text + right_text`, which joins
the text into `'12.57.25'` instead of adding. Whole-number text such as `"12"`
still converts with `float()`, so the same steps print `Sum: 19.0`.

```python
left_text = "12.5"  # the exact type input() would return: str
right_text = "7.25"
print(type(left_text).__name__, type(right_text).__name__)

left = float(left_text)
right = float(right_text)
total = left + right
print(f"Sum: {total}")
assert total == 19.75
assert left_text + right_text == "12.57.25"  # joining text is not addition

left_text = "12"
right_text = "7"
total = float(left_text) + float(right_text)
print(f"Sum: {total}")
assert total == 19.0
```

**Expected output:**

```text
str str
Sum: 19.75
Sum: 19.0
```

**Why the answer does not call `input()`:** the classroom Run has no keyboard
attached, so `input()` raises `EOFError: EOF when reading a line` there. In an
interactive terminal, `left_text = input("First number: ")` produces the same
`str`, and every later line of this answer stays the same.

### Exercise 2: worked answer

**Learner contract:** Starting from `raw = ' Data Science '`, create a new value exactly equal to `'data science'`. **Constraints:** use string methods rather than slicing or a hard-coded replacement. **Verify:** assert the normalized result and show that `raw` itself is unchanged because strings are immutable.

**Reasoning:** `strip()` removes the surrounding spaces and `lower()` changes
the case. Each method returns a new string, so chaining them builds the answer
while `raw` keeps its original value. Slicing such as `raw[1:-1]` happens to
work for this exact input but breaks as soon as the number of spaces changes,
which is why the contract asks for string methods. A common slip is calling
`raw.strip()` on its own line without binding the result: the cleaned string
is created and immediately discarded.

```python
raw = " Data Science "
normalized = raw.strip().lower()

assert normalized == "data science"
assert raw == " Data Science "  # strings are immutable; raw is unchanged
print(repr(raw), "->", repr(normalized))
```

**Expected output:** `' Data Science ' -> 'data science'`.

### Exercise 3: worked answer

**Learner contract:** Convert the text `'3.14'` to a floating-point number, double it, and format the result as `6.28`. **Constraints:** keep the original text in one name and the numeric value in another. **Verify:** assert the parsed value has type `float` and explain why `'3.14' * 2` is not numeric multiplication.

**Reasoning:** `float("3.14")` builds a number from the text, the number is
doubled, and the format specification `:.2f` turns the result back into
display text. Separate names make the three stages visible: text in, number
for arithmetic, text out. The trap is `"3.14" * 2`: with a string on the left,
`*` means repetition and produces `"3.143.14"`. The exact comparison
`doubled == 6.28` is safe here only because doubling a binary float is exact;
for other calculations, compare the formatted text or allow a tolerance.

```python
raw_number = "3.14"
number = float(raw_number)
doubled = number * 2
displayed = f"{doubled:.2f}"

assert isinstance(number, float)
assert doubled == 6.28
assert displayed == "6.28"
assert raw_number == "3.14"
assert raw_number * 2 == "3.143.14"  # repetition, not multiplication
```

## Exercises 4-8: Expanded mastery answers

### Exercise 4: answer contract

**Learner contract:** **Prediction:** Predict the value and type of `"7" * 2`, `7 / 2`, `7 // 2`, `bool("")`, and `bool("0")` before running them. **Progressive hint:** Operators follow operand types; non-empty strings are truthy. **Verify:** Create a table of predicted/actual value and type for all five expressions; every row must match, including `bool('0') is True`.

**Reasoning:** Each operator takes its meaning from the operand types. With a
string on the left, `*` repeats text, so `"7" * 2` is `'77'`. `/` always
produces a `float` (`3.5`), while `//` is floor division and keeps two
integers as an `int` (`3`). `bool("")` is `False` because the string is empty,
and `bool("0")` is `True` because it contains one character; Python never
reads the character as the number zero. That last case is the prediction
learners most often get wrong.

```python
print(repr("7" * 2), type("7" * 2).__name__)
print(7 / 2, type(7 / 2).__name__)
print(7 // 2, type(7 // 2).__name__)
print(bool(""), bool("0"))
assert "7" * 2 == "77" and 7 / 2 == 3.5 and 7 // 2 == 3
assert bool("") is False and bool("0") is True
```

**Expected output:**

```text
'77' str
3.5 float
3 int
False True
```

### Exercise 5: answer contract

**Learner contract:** **Tracing:** Trace `raw = ' 0042 '; cleaned = raw.strip(); number = int(cleaned)` and record the value/type after every assignment. **Progressive hint:** String methods return new strings; conversion constructs an integer. **Verify:** Record `repr(value)` and `type(value).__name__` after `raw`, `cleaned`, and `number`; confirm the original string still contains spaces.

**Reasoning:** Three names refer to three different objects: `raw` keeps the
original `' 0042 '`, `cleaned` refers to the new string `'0042'`, and `number`
refers to the integer `42` that `int()` built from that text. `repr()` makes
the spaces visible, which plain `print()` would hide. The leading zeros
disappear only at the conversion step, because an integer does not remember
how it was written. The usual mistake is expecting `strip()` to change `raw`
in place.

```python
raw = " 0042 "
cleaned = raw.strip()
number = int(cleaned)
print(repr(raw), type(raw).__name__)
print(repr(cleaned), type(cleaned).__name__)
print(repr(number), type(number).__name__)
assert (raw, cleaned, number) == (" 0042 ", "0042", 42)
```

**Expected output:**

```text
' 0042 ' str
'0042' str
42 int
```

### Exercise 6: answer contract

**Learner contract:** **Implementation:** Given `raw_temperature = " 32.5 "`, create a `float` named `temperature` and a display string named `shown` with one decimal place. Then run `float("warm")` once to see what invalid text does. **Progressive hint:** `float()` ignores surrounding spaces; formatting with `:.1f` produces text, not a new number. **Verify:** Assert `temperature == 32.5`, `type(temperature) is float`, and `shown == "32.5"`; record the last line of the `float("warm")` error, `ValueError: could not convert string to float: 'warm'`. Day 3 shows how to handle that error.

**Reasoning:** `float()` already accepts surrounding whitespace, so
`float(" 32.5 ")` is `32.5`; calling `strip()` first is harmless and makes the
cleaning step explicit. `f"{temperature:.1f}"` creates the separate string
`'32.5'` and leaves the number unchanged, so later arithmetic still uses a
`float`. Invalid text such as `"warm"` makes `float()` raise
`ValueError: could not convert string to float: 'warm'`; on Day 2 the job is to
read that message, and Day 3 adds `try`/`except` to handle it on purpose. A
frequent slip is comparing the display text with a number: `shown == 32.5` is
always `False` because `shown` is a string.

```python
raw_temperature = " 32.5 "
temperature = float(raw_temperature.strip())
shown = f"{temperature:.1f}"
print(temperature, type(temperature).__name__, repr(shown))
assert temperature == 32.5 and type(temperature) is float
assert shown == "32.5"

# Remove the comment marker to see the failure; the run stops on this line:
# float("warm")  # ValueError: could not convert string to float: 'warm'
```

**Expected output:** `32.5 float '32.5'`.

### Exercise 7: answer contract

**Learner contract:** **Debugging:** `enabled = bool(raw)` gives `True` for `raw = " FALSE "` because any non-empty string is truthy. Repair the conversion so `"true"`, `"false"`, and `" FALSE "` map to the intended Booleans, and flag any other spelling as unknown. **Progressive hint:** Normalize with `strip()` and `lower()`, then compare the result with `==`. **Verify:** Compute `enabled = normalized == "true"` and `is_known = normalized == "true" or normalized == "false"`; assert that `"true"` gives `enabled is True`, `" FALSE "` gives `enabled is False` with `is_known is True`, and `"yes-ish"` gives `is_known is False`. Day 3 shows how to reject unknown text with an exception.

**Reasoning:** `bool(raw)` only asks whether the string is empty, so every
non-empty spelling, including `" FALSE "`, becomes `True`. The repair
normalizes the text first and then compares it with the exact accepted words.
`normalized == "true"` gives the Boolean value, and `is_known` records whether
the text was one of the two accepted spellings, so `"yes-ish"` is flagged
instead of quietly meaning "disabled". Day 3 turns that flag into a raised
`ValueError` so that unknown text cannot continue.

```python
raw = " FALSE "
normalized = raw.strip().lower()
enabled = normalized == "true"
is_known = normalized == "true" or normalized == "false"
print(repr(normalized), enabled, is_known)
assert bool(raw) is True  # the original bug: any non-empty text is truthy
assert enabled is False and is_known is True

raw = "true"
normalized = raw.strip().lower()
assert normalized == "true"

raw = "yes-ish"
normalized = raw.strip().lower()
is_known = normalized == "true" or normalized == "false"
assert is_known is False
```

**Expected output:** `'false' False True`.

### Exercise 8: answer contract

**Learner contract:** **Edge case and explanation:** Model an optional discount where `None` means not supplied and `0.0` means supplied but zero. Explain why a truthiness check loses meaning. **Progressive hint:** `discount is None` asks about absence; `bool(discount)` asks about truthiness. **Verify:** For `discount` set to `None`, `0.0`, and `0.25`, record `discount is None` and `bool(discount)`; assert that `is None` is `True` only for `None`, while `bool()` is `False` for both `None` and `0.0`.

**Reasoning:** `None` and `0.0` answer different questions: "was a discount
supplied?" and "how large is it?". `bool()` treats both as false, so a
truthiness test would handle a deliberate zero discount as if nothing had
been supplied. `discount is None` checks for the single `None` object and is
`True` only when the value is absent, so `0.0` and `0.25` stay supplied
numbers. Using `discount == 0` as an absence test fails the same way, because
it also catches the real zero.

```python
discount = None
print(discount is None, bool(discount))
discount = 0.0
print(discount is None, bool(discount))
discount = 0.25
print(discount is None, bool(discount))
```

**Expected output:**

```text
True False
False False
False True
```

Only the first line has `is None` equal to `True`, while `bool()` gives `False`
for both `None` and `0.0`. Day 3 uses `if discount is None:` to choose
different messages for the two states.
