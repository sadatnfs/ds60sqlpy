# Day 3 Solutions: Control Flow, Truthiness, and Exceptions

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

These worked answers demonstrate **branch selection, truthiness in conditions, and narrow exception boundaries**. Predict each named
result before comparing your attempt with its matching assertions.

Control flow is the route execution takes through a program. An
`if`/`elif`/`else` chain chooses exactly one branch: Python tests from
top to bottom and stops at the first true condition. Put narrow or more
specific rules before broader ones, and validate impossible inputs
before classifying valid ones.

Exceptions separate a normal return path from a failure path. A `try`
block should contain only the operation expected to fail, while
`except` names the failure the current layer can interpret. Catching
every exception hides programming bugs. `else` runs after a successful
`try`; `finally` runs whether success or failure occurred.

### Vocabulary used in the worked answers

- **condition:** an expression evaluated for truthiness.
- **branch:** one possible block selected by a condition.
- **guard clause:** an early check that rejects or handles an invalid case.
- **exception:** an object representing a failure that interrupts normal flow.
- **raise:** to deliberately signal an exception.
- **handler:** an `except` block for a named exception type.

### How to compare an answer

For each answer, follow the input value through every condition or `try`
clause to the printed output or assertion that proves the behavior. Then
change the input to a boundary value, such as 59.49 or `"seven"`, predict the
new path, and rerun before accepting the answer.
<!-- END BEGINNER SOLUTION REVIEW -->

## Exercises 1-3: Worked answers

### Exercise 1: worked answer

**Learner contract:** Given `number = 15`, write one ordered `if`/`elif`/`else` chain that sets `label` to `"FizzBuzz"` for multiples of both 3 and 5, `"Fizz"` for multiples of 3 only, `"Buzz"` for multiples of 5 only, and `str(number)` otherwise. **Constraints:** test divisibility with `%` and keep all four outcomes in one chain. **Verify:** rerun with `number` set to 3, 5, 15, 16, and 30 and assert the labels `"Fizz"`, `"Buzz"`, `"FizzBuzz"`, `"16"`, and `"FizzBuzz"`. Day 4 repeats this decision for 1 through 30 with a `for` loop.

**Reasoning:** The combined rule must come first. Fifteen is also a multiple of
3, so if `number % 3 == 0` were tested first, 15 would stop at `"Fizz"` and
never reach `"FizzBuzz"`. Testing `number % 15 == 0` is the same as "divisible
by 3 and by 5" because 3 and 5 share no factor; `number % 3 == 0 and
number % 5 == 0` says it more literally. `str(number)` keeps every label a
string, so `"16"` and `"Fizz"` have the same type. Writing four separate `if`
statements is the usual mistake: 15 then satisfies three of them, and the
label is whichever assignment happened to run last.

```python
number = 15

if number % 15 == 0:
    label = "FizzBuzz"
elif number % 3 == 0:
    label = "Fizz"
elif number % 5 == 0:
    label = "Buzz"
else:
    label = str(number)

print(number, label)
assert label == "FizzBuzz"
```

**Expected output:** `15 FizzBuzz`. Rerunning with `number` set to 3, 5, 16,
and 30 prints `Fizz`, `Buzz`, `16`, and `FizzBuzz`. Day 4 places the same chain
inside `for number in range(1, 31):` to produce all thirty labels in one run.

### Exercise 2: worked answer

**Learner contract:** Given `text = " 7 "`, put only `int(text)` inside `try`, set `age` to the integer on success, and set `age = None` when `ValueError` is raised. **Constraints:** do not use a bare `except`; use an `else` block to record success. **Verify:** run with `"42"`, `" 7 "`, and `"seven"` and assert that `age` is `42`, `7`, and `None`; explain which runs execute the `else` block.

**Reasoning:** `int()` ignores surrounding whitespace, so `" 7 "` converts
directly; only text that is not an integer, such as `"seven"`, raises
`ValueError`. Keeping only `int(text)` inside `try` means a typo elsewhere in
the cell, such as a misspelled name, still produces its own error instead of
silently becoming `None`. The `else` block runs for `"42"` and `" 7 "` but not
for `"seven"`. A bare `except:` is never the narrow choice: it also catches
real bugs and even a keyboard interrupt.

```python
text = " 7 "

try:
    age = int(text)
except ValueError:
    age = None
    print("not an integer:", repr(text))
else:
    print("parsed:", age)

assert age == 7
```

**Expected output:** `parsed: 7`. With `text = "seven"` the output is
`not an integer: 'seven'` and `age` is `None`.

### Exercise 3: worked answer

**Learner contract:** Given `measurement = -0.1`, raise `ValueError` with the message `measurement must be non-negative, got -0.1` when the value is negative, and leave non-negative values unchanged. **Constraints:** check the sign with an `if` before any calculation uses the value. **Verify:** run once with `2.5` (no error, value unchanged) and once with `-0.1`; then wrap the check in `try`/`except ValueError as exc` and assert that `str(exc)` equals the exact message. Day 12 shows how to define a dedicated exception type such as `NegativeMeasurementError`.

**Reasoning:** The sign check happens before anything uses the value, so a
negative reading can never flow into later arithmetic. Putting the value in
the message (`got -0.1`) tells the reader which input failed without a rerun.
Catching `ValueError` in the same cell only demonstrates that the exact
message arrives; in real code the `raise` sits in the checking code and the
`try` in the code that decides what to do next. Writing `measurement <= 0`
instead of `< 0` would wrongly reject a legitimate zero reading.

```python
measurement = -0.1

try:
    if measurement < 0:
        raise ValueError(f"measurement must be non-negative, got {measurement}")
    print("accepted:", measurement)
except ValueError as exc:
    message = str(exc)
    print("rejected:", message)

assert message == "measurement must be non-negative, got -0.1"
```

**Expected output:** `rejected: measurement must be non-negative, got -0.1`.
With `measurement = 2.5` the `if` is false, nothing is raised, and the output
is `accepted: 2.5`.

## Exercises 4-8: Expanded mastery answers

### Exercise 4: answer contract

**Learner contract:** **Prediction:** Predict which branch handles 0, 9, and 12 when checks are ordered as `x % 2 == 0`, `x % 3 == 0`, then both. Explain the bug. **Progressive hint:** Only the first true branch runs; test the most specific rule first. **Verify:** Record the branch selected for `0`, `9`, and `12` before/after reordering; confirm the repaired `12` reaches the combined rule.

**Reasoning:** Only the first true condition runs. Any number that passes the
combined test also passes `x % 2 == 0`, so with the combined test last it can
never be selected: 12 stops at `"even"`. Moving the combined test to the top
repairs 12 and also changes 0, because `0 % 2` and `0 % 3` are both 0 (zero is
a multiple of every nonzero integer). Nine is odd, so the reorder does not
affect it.

| Value | Original order (even, multiple of 3, both) | Repaired order (both first) |
|---|---|---|
| 0 | even | multiple of 6 |
| 9 | multiple of 3 | multiple of 3 |
| 12 | even | multiple of 6 |

```python
x = 12

if x % 2 == 0 and x % 3 == 0:
    branch = "multiple of 6"
elif x % 2 == 0:
    branch = "even"
elif x % 3 == 0:
    branch = "multiple of 3"
else:
    branch = "other"

print(x, branch)
assert branch == "multiple of 6"
```

### Exercise 5: answer contract

**Learner contract:** **Tracing:** Trace `try/except/else/finally` for a successful integer parse and for invalid text. Which clauses run in each path? **Progressive hint:** `else` follows success; `finally` runs in both cases. **Verify:** Use a four-column trace for `try`, `except`, `else`, and `finally` on valid/invalid text; each clause's executed flag must match the language rules.

**Reasoning:** `try` always starts. When the conversion succeeds, Python skips
`except`, runs `else`, then runs `finally`. When it fails, the rest of the
`try` block is skipped, the matching `except` runs, `else` is skipped, and
`finally` still runs. Printing a line in every clause turns that rule into
visible evidence. The common wrong prediction is that `finally` runs only
after an error; it runs on both paths.

```python
text = "12"

try:
    print("try: converting", repr(text))
    value = int(text)
except ValueError:
    print("except: not an integer")
else:
    print("else: parsed", value)
finally:
    print("finally: always runs")
```

| Clause | `text = "12"` | `text = "twelve"` |
|---|---|---|
| `try` | runs | runs (stops at `int`) |
| `except` | skipped | runs |
| `else` | runs | skipped |
| `finally` | runs | runs |

### Exercise 6: answer contract

**Learner contract:** **Implementation:** A grader records scores as floats. Policy: from 89.5 to 100 is `"distinction"`, from 59.5 up to (but not including) 89.5 is `"pass"`, from 0 up to 59.5 is `"fail"`, and any score outside 0 to 100 raises `ValueError`. Given `score = 59.5`, write the chain. **Progressive hint:** Validate the range first, then test the thresholds from highest to lowest with `>=`. **Verify:** Rerun with `59.49`, `59.5`, `89.49`, `89.5`, `100.0`, and `100.5`; assert `"fail"`, `"pass"`, `"pass"`, `"distinction"`, `"distinction"`, and a `ValueError` for `100.5`.

**Reasoning:** The policy states half-point thresholds, so the code compares
the float directly instead of rounding first. That matters because Python's
`round()` sends halves to the nearest even number: `round(59.5)` is `60`, but
`round(58.5)` is `58`, so a rounding-based rule would treat equal half-point
margins differently. Testing from the highest threshold down with `>=` gives
each boundary to the higher grade: 89.5 is a distinction and 89.49 a pass.
Validating the range first means 100.5 raises instead of being reported as a
distinction.

```python
score = 59.5

if not 0 <= score <= 100:
    raise ValueError(f"score must be between 0 and 100, got {score}")
if score >= 89.5:
    grade = "distinction"
elif score >= 59.5:
    grade = "pass"
else:
    grade = "fail"

print(score, grade)
assert grade == "pass"
```

**Expected output:** `59.5 pass`. Reruns give `59.49 fail`, `89.49 pass`,
`89.5 distinction`, `100.0 distinction`, and, for `100.5`,
`ValueError: score must be between 0 and 100, got 100.5`.

### Exercise 7: answer contract

**Learner contract:** **Debugging:** A cell wraps both `count = int(raw_count)` and `total_cost = count * unit_price` in one `try` block followed by a bare `except:` that sets `total_cost = 0`, and `unit_price` was never defined. Rebuild it so only the conversion is protected and only `ValueError` is caught. **Progressive hint:** Keep only the conversion inside the protected block and move the calculation after it. **Verify:** With `raw_count = "twelve"` the handler reports invalid text; with `raw_count = "12"` the `NameError` for `unit_price` now appears instead of a silent `0`; after defining `unit_price = 2.5`, assert `total_cost == 30.0`.

**Reasoning:** The original bare `except:` caught the `NameError` for
`unit_price` and replaced it with `0`, so a programming mistake looked like a
legitimate zero cost. Protecting only `int(raw_count)` and catching only
`ValueError` keeps a handler for the failure you expect (bad text) and lets
every other error stop the run with its own traceback. Run the repaired cell
once before the `unit_price` line exists to watch the `NameError` appear; that
visible failure is the point of the repair.

```python
raw_count = "12"
unit_price = 2.5  # the definition the bare except had been hiding

try:
    count = int(raw_count)
except ValueError:
    count = None
    print("invalid count text:", repr(raw_count))

if count is not None:
    total_cost = count * unit_price
    print("total:", total_cost)
    assert total_cost == 30.0
```

**Expected output:** `total: 30.0`. With `raw_count = "twelve"` the output is
`invalid count text: 'twelve'` and no total is computed.

### Exercise 8: answer contract

**Learner contract:** **Edge case and explanation:** Given `numerator = 3` and `denominator = 0`, choose a zero-denominator policy: raise `ZeroDivisionError` with a clear message, or set `ratio = None` and record why. Justify the choice. **Progressive hint:** Code that other people reuse usually should not invent a numeric answer such as `0.0`. **Verify:** With `denominator = 4`, assert `ratio == 0.75`; with `denominator = 0`, assert your chosen outcome exactly and explain why `0.0` would be a fabricated answer.

**Reasoning:** Division by zero has no numeric answer, so the policy must
either stop or mark the result as missing; `0.0` would be a fabricated value
that later sums and averages would silently include. This answer sets
`ratio = None` with a recorded reason because a report can still show the
other ratios; code that cannot continue without a ratio should raise
`ZeroDivisionError("denominator must not be zero")` instead. Checking
`denominator == 0` before dividing is clearer here than catching the error,
because the condition is easy to test directly.

```python
numerator = 3
denominator = 0

if denominator == 0:
    ratio = None
    reason = "denominator is zero, so the ratio is undefined"
else:
    ratio = numerator / denominator
    reason = "computed"

print(ratio, reason)
assert ratio is None
```

**Expected output:** `None denominator is zero, so the ratio is undefined`.
With `denominator = 4` the output is `0.75 computed`.
