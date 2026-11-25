# csharp-002: explanation and comparison

Reference program: [csharp-002_solution.cs](csharp-002_solution.cs), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Division depends on operand types:** Converting after integer division would preserve the already truncated result. Operand conversion must happen before division. The integer result is 3 and the floating result is 3.5.

**Parse an external representation:** The success flag carries information that a default integer cannot. Validation belongs where text becomes a typed value. 42 parses successfully; words fail without an exception.

## Task answers

### Task 1: Predict and explain

Predict the type and value of 7/2, 7/2.0 and (double)(7/2).

**Written answer.** `7/2` is an `int` with value 3. `7/2.0` is a `double` with value 3.5. `(double)(7/2)` is a `double` with value 3.0: the parentheses force the integer division first, and the cast converts the already truncated 3.

**Why it is correct.** The operand types choose the operator. Two `int` operands select integer division, which discards the remainder. One `double` operand promotes the other, so division keeps the fraction. A cast applies to the expression it is written on, so its position decides whether it runs before or after the truncation.

**Plausible wrong approach.** Expecting `(double)(7/2)` to give 3.5 assumes the cast reaches inside the parentheses. It does not: the cast receives the integer 3, and converting 3 to `double` cannot bring back the missing half.

**How to verify.** Add `Check(7 / 2 == 3, ...)`, `Check(7 / 2.0 == 3.5, ...)` and `Check((double)(7 / 2) == 3.0, ...)` to Example A. Hovering each expression in an editor also shows its static type.

### Task 2: Guided modification

Change the operands to 8 and 2 and explain why that input hides the truncation difference.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```csharp
int whole = 8 / 2;
double fraction = (double)8 / 2;
Check(whole == 4 && fraction == 4.0, "even operands agree");
Check(7 / 2 != (double)7 / 2, "odd operands expose truncation");
```

**Observe:** With 8 and 2 both divisions give 4, while 7 and 2 still give 3 and 3.5.

8 is an exact multiple of 2, so the remainder that integer division throws away is 0. Both kinds of division therefore produce 4, and a test using only these inputs cannot tell correct code from code that truncates. The second check keeps the odd case that exposes the difference.

**Plausible wrong approach.** Replacing the lesson's test data with 8 and 2 and seeing all checks pass suggests the conversion is right. The same passing run would appear for `(double)(a / b)`, which is wrong for every odd numerator.

**How to verify.** Change the operands to 9 and 2: `whole` must become 4 and `fraction` 4.5, and the first check now fails, showing that only remainder-producing inputs reveal truncation.

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

**Written answer.** In `double average = (double)(total / count);` with `total = 7` and `count = 2`, the division runs on two `int` values and yields 3, and the cast then produces 3.0. The correct average is 3.5. Fix it by converting an operand before dividing: `double average = (double)total / count;`.

**Why it is correct.** The cast in the faulty line is applied to the result of `total / count`, after the fraction is gone. Casting `total` first makes the division a `double` division, so the remainder survives as `.5`.

**Plausible wrong approach.** Testing with `total = 6` and `count = 2` gives 3.0 from both versions, so the bug passes. A fractional counterexample needs a total that the count does not divide, such as 7 and 2.

**How to verify.** Check `(double)(7 / 2) == 3.0` to reproduce the bug and `(double)7 / 2 == 3.5` for the fix. Then try `total = 1`, `count = 3` and confirm the fixed version gives about 0.333, not 0.

### Task 5: Boundary evidence

Test empty text, zero, a negative number and a number outside the int range.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```csharp
bool TryCount(string text, out int count) {
  var style = NumberStyles.Integer;
  var culture = CultureInfo.InvariantCulture;
  bool parsed = int.TryParse(text, style, culture, out count);
  return parsed && count >= 0;
}
Check(!TryCount("", out _), "empty text rejected");
Check(TryCount("0", out int zero) && zero == 0, "zero accepted");
Check(!TryCount("-5", out _), "negative rejected");
Check(!TryCount("2147483648", out _), "beyond int range rejected");
Check(TryCount("2147483647", out int max) && max == int.MaxValue,
      "largest int accepted");
```

**Observe:** Empty text, -5 and 2147483648 are rejected; 0 and 2147483647 are accepted.

Each input tests a different rule. `""` has no digits, so `TryParse` fails. `"0"` is the smallest valid quantity. `"-5"` parses, so the separate `count >= 0` test must reject it. `"2147483648"` is `int.MaxValue + 1`, so `TryParse` reports failure instead of wrapping, while `"2147483647"` sits exactly on the boundary and is accepted.

**Plausible wrong approach.** Checking only that `TryParse` returned true accepts `-5` as a quantity. Using `int.Parse` instead turns the empty and oversized inputs into `FormatException` and `OverflowException`, which a caller has to catch separately.

**How to verify.** Add `TryCount(" 7", out _)` and decide the policy: `NumberStyles.Integer` allows surrounding spaces, so it is accepted. If quantities must be bare digits, switch to `NumberStyles.None` and confirm the check flips.

### Task 6: Transfer and justify

Design an input boundary for a percentage and document its accepted textual and numeric ranges.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Mechanism and diagnostic reasoning

A type describes the values an expression may hold and the operations available on those values. `int` represents a bounded whole number; `double` represents a binary floating-point approximation; `bool` represents a logical decision. A variable is a named storage location. Reassigning a variable changes its stored value, not its declared type.

`var` asks the compiler to infer a static type from the initializer. It does not make the variable dynamically typed. Conversions deserve attention because they can widen a range, lose fractional information, or fail. Put conversion at a visible boundary rather than scattering casts through a formula. First choose the meaning and units of the result, then choose its type.

`int count = 7` declares and initializes. `var inferred = 7` also produces an int. `(double)count` converts before an operator uses the value. `int.TryParse(text, out int parsed)` returns success separately from the output value; a failed parse must not silently mean a real zero.

An inferred type is still static. A cast is not a validation policy. `TryParse` alone accepts negative integers, so domain rules such as nonnegative quantities need a second condition.

## Review before continuing

Run the reference and confirm it prints `csharp-002: passed`, then rerun the guide's counterexample.
