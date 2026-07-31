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





<!-- BEGIN HOW TO RUN -->
## How to run this lesson

Work from the repository root. The rendered HTML lesson is a readable
preview; execute the real notebook in VS Code or JupyterLab.

1. Confirm the course environment before changing it:

   ```powershell
   # Windows PowerShell
   $CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
       (Resolve-Path .\.venv\Scripts\python.exe).Path
   } else {
       (Resolve-Path .\.venv\python.exe).Path
   }
   & $CoursePython scripts\course.py doctor
   ```

   ```bash
   # macOS/Linux
   .venv/bin/python scripts/course.py doctor
   ```

2. Read `python/ds-60day/companion-guides/day05_functions_type_hints.md`, then open `python/ds-60day/notebooks/day05_functions_type_hints.ipynb` from the repository
   folder in VS Code or JupyterLab.
3. Select **Python (ds60sqlpy)**. Do not run `%pip` in the notebook. If
   an import is missing, use the doctor and the catalog dependency label
   to repair the shared environment.
4. Restart the kernel and run from the first cell downward. Before every
   example, write a prediction; after it runs, compare the actual value,
   type, shape, or side effect with the stated observation.
5. Attempt each numbered exercise in its own work cell. Use the explicit
   verification as part of the task. Keep `solutions/` closed until you
   have a tested attempt or deliberately ask for help.

**Lesson outcome:** use day 5 — functions, docstrings, and type hints to practice function contracts, parameters, return values, scope, and type hints
and explain the evidence produced by your code.
<!-- END HOW TO RUN -->

<!-- BEGIN BEGINNER DEEP DIVE -->
## Beginner deep dive — build the idea before the syntax

### Start with one mental picture

A function gives a name to a reusable behavior. Its contract says which
inputs are accepted, what it returns, which failures it raises, and
whether it changes anything outside itself. Parameters are names in the
definition; arguments are actual values supplied by a caller.

A call creates a local scope. Names assigned there normally disappear
when the call returns. A `return` sends one value to the caller and
stops that call. Type hints document intended types and support static
tools, but Python does not enforce them automatically at runtime.
Defaults are evaluated once when `def` runs, so mutable defaults should
normally be replaced by `None` plus a fresh object inside the function.

### Vocabulary in plain language

- **function:** a named reusable block that can accept inputs and return a value.
- **parameter:** a name declared in a function signature.
- **argument:** a value supplied for a parameter during a call.
- **return value:** the object sent back to the caller.
- **scope:** the region in which a name can be resolved.
- **type hint:** machine-readable documentation of an intended type.

### Syntax anatomy

`def clamp(value: float, *, low: float, high: float) -> float:` begins
with `def`, gives the function a name, annotates three parameters, uses
`*` to make `low` and `high` keyword-only, and annotates the return.
The colon starts the indented body. A docstring is the first string in
that body and should state behavior that the signature cannot fully
express, especially errors and edge cases.

### Worked example 1 — Make validation part of the contract

Reject an invalid domain before doing the calculation. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
def mean(values: list[float]) -> float:
    """Return the arithmetic mean of a non-empty list."""
    if not values:
        raise ValueError("values must not be empty")
    return sum(values) / len(values)

mean([2.0, 4.0, 9.0])
```

**Expected observation**

```text
`5.0`. Empty input follows a deliberate exception path instead of dividing by zero accidentally.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### Worked example 2 — Use keyword-only parameters to make calls readable

A signature can prevent ambiguous positional calls. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
def discounted(price: float, *, rate: float = 0.0) -> float:
    if not 0 <= rate <= 1:
        raise ValueError("rate must be between 0 and 1")
    return price * (1 - rate)

discounted(80.0, rate=0.25)
```

**Expected observation**

```text
`60.0`. The call labels `rate`, making `0.25` hard to confuse with another quantity.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### A debugging routine for this topic

When the output differs from your prediction, use this order:

1. Read the signature and call side by side when arguments bind unexpectedly.
2. Check whether every path reaches an explicit `return`; falling off the end returns `None`.
3. Replace a mutable default such as `items=[]` with `items: list[...] | None = None`.
4. Use a type checker for hints, but still validate external runtime data at the boundary.

### Practice ramp

Work through the numbered exercises in five modes rather than treating all
of them as blank-code prompts:

1. **Prediction:** state the value, type, shape, rows, or side effect before
   execution.
2. **Guided modification:** change one part of a worked example and explain
   which part of the result must change.
3. **Independent application:** implement the same idea with a new input and
   an explicit contract.
4. **Debugging and edge cases:** reproduce a failure, identify the violated
   assumption, and prove the repair at a boundary.
5. **Retrieval:** close the guide and explain the core model from memory
   before moving on.

**Useful alternative:** A tuple can return several related values; a dataclass becomes clearer when those values need durable names and behavior.

**Boundary to remember:** Empty input, mismatched lengths, zero total weight, invalid numeric ranges, and Unicode/whitespace normalization need written policy.
<!-- END BEGINNER DEEP DIVE -->

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

Each item is a complete mini-contract. Before writing code, copy its input,
expected behavior, constraints, and verification into your work cell. A
result is not complete merely because it “looks right”; run the stated
assertion or inspection and explain what it proves.

1. Implement `describe(values: list[float]) -> tuple[float, float]` returning the arithmetic mean and **population** standard deviation. **Input:** `[2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]`.
   **Expected result:** `(5.0, 2.0)`. **Constraints:** compute the mean once, use squared distances, and do not import a statistics helper that performs the whole task.
   **Verify:** Use `math.isclose` to confirm mean `5.0` and population standard deviation `2.0`, then show empty input follows the documented failure path.

2. Add a docstring to `describe` that states accepted input, the two tuple fields in order, and the empty-input policy. **Constraint:** choose and document one explicit behavior—this lesson's reference raises `ValueError`.
   **Verify:** `help(describe)` communicates the contract without reading the body.

3. Validate `describe` near its boundary: reject an empty list and any non-finite value such as `float('nan')` with a useful `ValueError`.
   **Verify:** show the normal result and use two separate `try`/`except ValueError` checks for the invalid cases; do not catch errors inside the function that it cannot repair.

### Additional mastery practice

Design functions from their contracts: accepted inputs, return value, failure behavior, side effects, and boundary cases.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

4. **Prediction:** Predict the result of calling a function with `items=[]` as a default three times when it appends on each call. Explain shared defaults.
   **Progressive hint:** Default objects are created once when `def` executes.
   **Verify:** Call the faulty function three times and record cumulative state, then assert the `None`-sentinel repair returns independent one-item lists on every call.
5. **Tracing:** Trace a local variable that shadows a global of the same name. Which binding changes, and when would `global` be required?
   **Progressive hint:** Assignment makes a name local unless explicitly declared otherwise.
   **Verify:** Record local/global values before, during, and after the call; confirm ordinary local assignment leaves the global unchanged.
6. **Implementation:** Implement typed `weighted_mean(values, weights)` with length, empty, and zero-total-weight validation.
   **Progressive hint:** State every invalid condition before calculating.
   **Verify:** Assert a known weighted mean and separately assert empty, length-mismatch, and zero-total-weight inputs raise the documented errors.
7. **Debugging:** Repair a function whose `*items` argument is accidentally passed as one list instead of unpacked individual items.
   **Progressive hint:** Compare `f(values)` with `f(*values)`.
   **Verify:** Capture arguments received by `f(values)` and `f(*values)`; assert the repaired call presents individual items rather than one nested list.
8. **Edge case and explanation:** Write a docstring for a name-normalization function and test empty, whitespace-only, and Unicode input.
   **Progressive hint:** Document whether empty normalized output is valid or an error.
   **Verify:** Test ordinary, empty, whitespace-only, and Unicode names against the docstring's stated contract; every behavior must match the documentation.

Before opening the reference solution, write one sentence explaining
which contract or mental model each result confirms.

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

## Ask Codex about this lesson

Codex coaching is optional; the guide and notebook above contain the full
lesson. If you want a patient tutor, copy this prompt from the repository
root:

```text
Use $guide-ds60sqlpy-learning to tutor me through `python-05`
(Day 5 — Functions, Docstrings, and Type Hints). I am a complete beginner. Emphasize function contracts, parameters, return values, scope, and type hints.
Read `python/ds-60day/companion-guides/day05_functions_type_hints.md` and use the learner notebook
`python/ds-60day/notebooks/day05_functions_type_hints.ipynb`. Do not open or quote anything under `solutions/` unless
I explicitly ask after making an honest attempt. Use these visible phases:
Explain, Predict, Attempt, Hint, Evidence, and Retrieval. First explain one
concept in plain language, then ask me to predict a small example and wait
for my attempt. Give only one progressive hint at a time. Help me run or
inspect my actual notebook evidence, adapt commands to my operating system,
and do not treat the rendered HTML preview as executable. Finish with 2-3
retrieval questions and one next step. Done when I can explain the mental
model without the guide, complete one independent exercise, and show the
prompt's verification evidence from my notebook.
```
