# Day 5 — Functions, Docstrings, and Type Hints

**Level:** Beginner

A function is a named contract: given valid inputs, it returns a documented
result or raises a documented exception.

## Learning objectives

By the end of this lesson, you can:

- design a function with parameters, defaults, and a return value;
- use `*args` and `**kwargs` only when variable inputs are part of the contract;
- write a docstring that documents behavior and edge cases;
- annotate inputs and outputs with Python 3.11-compatible type hints; and
- validate values at runtime instead of assuming annotations enforce them.

## Prerequisites

Complete Day 4 (`python-04`): collections, iteration, and generators.

## Vocabulary and mental model

- **Parameter:** the name in a function definition; **argument:** a value passed
  at a call site.
- **Signature:** the function name, parameter kinds, defaults, and annotations.
- **Scope:** where a name can be resolved.
- **Pure function:** returns a result without changing external state.
- **Type hint:** machine-readable documentation used by tools such as mypy.
  Python does not enforce hints automatically.
- **Docstring:** runtime-accessible documentation immediately inside a
  function, class, or module.

## Worked example

```python
def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    """Return value restricted to the inclusive range [low, high].

    Raises:
        ValueError: If low is greater than high.
    """
    if low > high:
        raise ValueError("low must not exceed high")
    return min(max(value, low), high)
```

The annotation describes intended types; the branch enforces a relationship
between values that a basic type checker cannot express.

## Exercises and progressive hints

1. Write an annotated function that computes the mean and population standard
   deviation of a list of numbers. **Hint:** calculate the mean once, then use
   each value's squared distance from that mean.
2. Add a docstring that states the return shape and empty-input behavior.
   **Hint:** decide on the contract before coding: return a sentinel or raise a
   specific exception.
3. Reject invalid inputs with `ValueError`. **Hint:** validate the collection
   and its values near the function boundary; do not catch errors the function
   cannot repair.

## Self-check

- What is the difference between a default argument and a return default?
- Why are mutable defaults such as `items=[]` dangerous?
- What can mypy detect that runtime execution may not, and vice versa?
- When is `*args` clearer than accepting a collection?

Expected behavior: normal numeric input returns two floats, the empty case
matches the docstring, and invalid values fail with a useful message.

## Common pitfalls and diagnosis

- **A list default retains old values:** use `None`, then create the list inside
  the function.
- **A function prints but returns `None`:** inspect whether every intended path
  has `return`.
- **A local assignment unexpectedly hides an outer name:** pass dependencies as
  parameters instead of relying on globals.
- **`float | None` is treated as a float:** narrow it with an explicit
  `is None` check before arithmetic.
- **A type hint seems to validate input:** call the function with a wrong value
  to confirm that validation requires code (or a validation library).

## Continue

- [Open the learner notebook](../notebooks/day05_functions_type_hints.ipynb)
- [Check the separate solution](../solutions/day05_functions_type_hints/day05_solutions.md)
- [Next: Day 6 — Core data structures](day06_data_structures.md)
