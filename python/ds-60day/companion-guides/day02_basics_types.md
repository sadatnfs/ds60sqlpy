# Day 2 — Variables and Core Types

**Level:** Beginner

Python values have types; variable names refer to those values. This lesson
turns text input into useful values and formats results clearly.

## Learning objectives

By the end of this lesson, you can:

- distinguish `str`, `int`, `float`, `bool`, and `None`;
- convert compatible values deliberately instead of relying on guesswork;
- use comparisons, truthiness, string methods, and f-strings; and
- explain why an input value is text until it is parsed.

## Prerequisites

Complete Day 1 (`python-01`): run the course environment and a notebook cell.

## Vocabulary and mental model

- **Value:** data such as `42`, `3.5`, or `"Ada"`.
- **Type:** the rules and operations associated with a value.
- **Variable:** a name bound to a value; assignment does not copy every object.
- **Conversion:** constructing one type from a compatible value, such as
  `float("3.14")`.
- **Truthiness:** the boolean interpretation of a value. Empty strings and
  containers are false; non-empty ones are true.
- **Immutable:** unable to change in place. String methods return new strings.

## Worked example

```python
raw_celsius = "21.5"
celsius = float(raw_celsius)
fahrenheit = celsius * 9 / 5 + 32
label = "  Indoor Sensor  ".strip().lower()

print(f"{label}: {fahrenheit:.1f} °F")
```

Trace the types after each line. Parsing and presentation are separate steps:
the calculation uses numbers, while the f-string creates display text.

## Exercises and progressive hints

1. Read two numbers with `input()` and print their sum. **Hint:** inspect
   `type(input(...))`, then convert both values before adding.
2. Transform `"  Data Science  "` into lowercase text without surrounding
   spaces. **Hint:** string methods can be chained because each returns a new
   string.
3. Convert `"3.14"` to a float and multiply it by two. **Hint:** do not change
   the original text just to make the calculation possible.

For transfer practice, the separate solution uses parallel tasks: format a
percentage, build a slug, and parse two numeric strings. Those are intentionally
not line-for-line copies of the notebook answers.

## Self-check

- What is the difference between `"8" + "2"` and `8 + 2`?
- Why does `bool("False")` evaluate to `True`?
- What does `None` communicate that `0` does not?
- Which format specifier would show one digit after the decimal point?

Expected behavior: numeric addition produces a number, text cleanup leaves the
original string unchanged, and formatted output is readable.

## Common pitfalls and diagnosis

- **Numbers concatenate:** print their types; one or both values are strings.
- **`ValueError` during conversion:** show the original value with `repr(...)`
  to reveal spaces or unexpected characters. Day 3 adds recovery logic.
- **Unexpected integer result assumptions:** `/` returns a float; `//` performs
  floor division, which differs from truncation for negative numbers.
- **Variable names shadow built-ins:** avoid names such as `str`, `list`, and
  `sum`; restarting the kernel clears accidental rebinding.
- **Floating-point output looks imprecise:** binary floats approximate many
  decimal fractions; format for display rather than comparing display strings.

## Continue

- [Open the learner notebook](../notebooks/day02_basics_types.ipynb)
- [Check the separate transfer solutions](../solutions/day02_basics_types/day02_solutions.md)
- [Next: Day 3 — Control flow and exceptions](day03_control_flow_exceptions.md)
