# csharp-002: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-002_solution.cs](csharp-002_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Division depends on operand types:** Converting after integer division would preserve the already truncated result. Operand conversion must happen before division. The integer result is 3 and the floating result is 3.5.

**Parse an external representation:** The success flag carries information that a default integer cannot. Validation belongs where text becomes a typed value. 42 parses successfully; words fail without an exception.

## Task answers

### Task 1: Predict and explain

Predict the type and value of 7/2, 7/2.0 and (double)(7/2).

No separate reference answer has been written for this task. Example A is the evidence to compare with: Converting after integer division would preserve the already truncated result. Operand conversion must happen before division. The integer result is 3 and the floating result is 3.5.

### Task 2: Guided modification

Change the operands to 8 and 2 and explain why that input hides the truncation difference.

No separate reference answer has been written for this task. Start from Example B: The success flag carries information that a default integer cannot. Validation belongs where text becomes a typed value. 42 parses successfully; words fail without an exception.

### Task 3: Independent construction

Write a TryParse-based validator accepting only nonnegative whole-number quantities.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
bool TryQuantity(string text, out int quantity) {
  var style = NumberStyles.None;
  var culture = CultureInfo.InvariantCulture;
  return int.TryParse(text, style, culture, out quantity);
}
Check(TryQuantity("42", out int count) && count == 42, "accepted");
Check(!TryQuantity("-1", out _), "negative rejected");
Check(!TryQuantity("4.5", out _), "fraction rejected");
Check(!TryQuantity("", out _), "empty rejected");
```

**Observe:** 42 is accepted; -1, 4.5 and empty text are rejected without an exception.

NumberStyles.None admits digits only, so a sign, a decimal point or whitespace makes TryParse return false. The caller receives a separate success flag instead of a sentinel quantity.

### Task 4: Diagnose a defect

Diagnose a conversion performed after integer division. Produce a fractional counterexample.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: An inferred type is still static. A cast is not a validation policy. `TryParse` alone accepts negative integers, so domain rules such as nonnegative quantities need a second condition.

### Task 5: Boundary evidence

Test empty text, zero, a negative number and a number outside the int range.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Division depends on operand types) and Example B (Parse an external representation).

### Task 6: Transfer and justify

Design an input boundary for a percentage and document its accepted textual and numeric ranges.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Static type**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A type describes the values an expression may hold and the operations available on those values. `int` represents a bounded whole number; `double` represents a binary floating-point approximation; `bool` represents a logical decision. A variable is a named storage location. Reassigning a variable changes its stored value, not its declared type.

`var` asks the compiler to infer a static type from the initializer. It does not make the variable dynamically typed. Conversions deserve attention because they can widen a range, lose fractional information, or fail. Put conversion at a visible boundary rather than scattering casts through a formula. First choose the meaning and units of the result, then choose its type.

`int count = 7` declares and initializes. `var inferred = 7` also produces an int. `(double)count` converts before an operator uses the value. `int.TryParse(text, out int parsed)` returns success separately from the output value; a failed parse must not silently mean a real zero.

An inferred type is still static. A cast is not a validation policy. `TryParse` alone accepts negative integers, so domain rules such as nonnegative quantities need a second condition.

## Review before continuing

Run the reference and confirm that it prints `csharp-002: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
