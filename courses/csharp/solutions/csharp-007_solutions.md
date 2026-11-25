# csharp-007: explanation and comparison

Reference program: [csharp-007_solution.cs](csharp-007_solution.cs), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Return a transformed value:** The parameter receives a value. Returning a transformed value does not reassign the caller variable. The result is 14 and the caller still holds 7.

**Expose rejection as part of the contract:** A precise function name and guard prevent accidental truncation from masquerading as a valid result. 12 divided by 3 returns 4; the exact-integer contract rejects 7 divided by 2.

## Task answers

### Task 1: Predict and explain

Trace the caller and parameter values through Double.

**Written answer.** The caller evaluates `original`, which is 7, and passes a copy to `Double`. Inside, the parameter `value` is 7 and the method returns `checked(7 * 2)`, which is 14. That return value is assigned to `result`. `original` is still 7, because the method only received a copy. `Double(0)` binds `value` to 0 and returns 0.

**Why it is correct.** `int` is a value type and the parameter is not `ref` or `out`, so passing it copies the value. Assigning to `value` inside the method could not affect `original`, and the method communicates only through its return value.

**Plausible wrong approach.** Expecting `original` to become 14 treats the call as if it modified its argument in place. That would require a `ref int` parameter, and the call would have to say `ref` explicitly.

**How to verify.** Example A already checks `result == 14 && original == 7`. Add a line inside `Double` that assigns `value = 100` before returning and confirm `original` is still 7.

### Task 2: Guided modification

Add a Triple function and test zero and a negative input.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```csharp
int Triple(int value) => checked(value * 3);
Check(Triple(0) == 0, "zero stays zero");
Check(Triple(-4) == -12, "negative input keeps its sign");
Check(Triple(5) == 15, "positive input");
```

**Observe:** Triple returns 0 for 0, -12 for -4 and 15 for 5.

Multiplying by 3 maps 0 to itself and keeps the sign of other inputs, so the expected values can be worked out independently: 0, -12 and 15. `checked` matches `Double`, so an input above `int.MaxValue / 3` throws instead of wrapping.

**Plausible wrong approach.** Implementing `Triple` as `value + value + value` passes these checks but skips `checked` unless it is added, so `Triple(int.MaxValue)` would wrap silently. Testing only 5 cannot tell a correct `Triple` from `value + 10`.

**How to verify.** Add a check that `Triple(1_000_000_000)` throws `OverflowException`, since 3 billion is above `int.MaxValue`, and that `Triple(-715_827_882) == -2_147_483_646` still fits.

### Task 3: Independent construction

Write a method computing an area from validated nonnegative dimensions.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
int Area(int width, int height) {
  if (width < 0 || height < 0) {
    throw new ArgumentOutOfRangeException(nameof(width));
  }
  return checked(width * height);
}
Check(Area(3, 4) == 12 && Area(0, 9) == 0, "valid dimensions");
bool rejected = false;
try {
  Area(-1, 2);
} catch (ArgumentOutOfRangeException) {
  rejected = true;
}
Check(rejected, "negative dimension rejected");
```

**Observe:** 3 by 4 gives 12, a zero side gives 0, and a negative side throws.

Validation happens before the calculation, and checked multiplication turns an overflow into an exception instead of a wrapped area.

### Task 4: Diagnose a defect

Diagnose a function whose name promises exact division but silently truncates.

**Written answer.** `int DivideExactly(int value, int divisor) => value / divisor;` returns 3 for `DivideExactly(7, 2)`. The name promises an exact quotient, but integer division drops the remainder 1, so every caller receives a value that is not exact and no error tells them. Either enforce the promise with `if (value % divisor != 0) throw new ArgumentException(...)`, as Example B does, or rename the method `DivideTruncating`.

**Why it is correct.** The method name is part of the contract a caller reads. When the body does something weaker than the name says, the mismatch spreads into every call site, and the remainder test makes the hidden case explicit.

**Plausible wrong approach.** Returning 0 or -1 for non-divisible input creates a sentinel that looks like a valid quotient, the pattern the pitfalls warn about. Changing the return type to `double` changes what the method does without changing its misleading name.

**How to verify.** Check that the faulty version returns 3 for `(7, 2)`. With the fix, check that `(12, 3)` still returns 4 and `(7, 2)` throws `ArgumentException`.

### Task 5: Boundary evidence

Test zero divisors and non-divisible inputs separately.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```csharp
int DivideExact(int value, int divisor) {
  if (divisor == 0)
    throw new DivideByZeroException();
  if (value % divisor != 0)
    throw new ArgumentException("not an exact quotient");
  return value / divisor;
}
bool zeroRejected = false;
try {
  DivideExact(6, 0);
} catch (DivideByZeroException) {
  zeroRejected = true;
}
bool remainderRejected = false;
try {
  DivideExact(7, 2);
} catch (ArgumentException) {
  remainderRejected = true;
}
Check(zeroRejected, "zero divisor has its own failure");
Check(remainderRejected, "remainder has its own failure");
Check(DivideExact(-12, 3) == -4, "exact negative quotient");
```

**Observe:** A zero divisor throws DivideByZeroException, 7 by 2 throws ArgumentException and -12 by 3 returns -4.

The two failures have different causes, so each gets its own exception and its own test. The zero test runs first because `value % 0` would itself throw before the remainder test could explain anything. Testing them separately proves that each guard works on its own instead of one catch block hiding which rule fired.

**Plausible wrong approach.** Putting both calls in one `try` block and catching `Exception` stops at the first throw, so the `(7, 2)` call never runs and a missing remainder guard goes unnoticed.

**How to verify.** Delete the remainder guard and confirm the second check fails because `DivideExact(7, 2)` returns 3. Deleting the zero guard instead still passes, since `6 % 0` throws the same exception type; compare the exception messages to see which line raised it.

### Task 6: Transfer and justify

Extract one computation from a larger program and state its input, output, mutation and failure contract.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Mechanism and diagnostic reasoning

A method gives a computation a name and a boundary. Its contract states accepted inputs, its result, state changes and failure behavior. Splitting code into methods helps only when those boundaries expose meaning. A helper that secretly edits unrelated state is harder to reason about than one returning a clearly defined result.

C# normally passes arguments by value. For a value type, that means a copied value; for an object reference, it means a copied reference to the same object. The distinction becomes important later. Start with small pure methods, which depend only on arguments and return a result without observable mutation. They are easy to test because the same inputs produce the same outputs.

`int Double(int value) => value * 2` declares a local function with a typed parameter and return. `return` ends the current method. `ref` and `out` are explicit parameter passing modes, not decorations; prefer ordinary return values until shared mutation is required.

A method name is part of the interface. A generic catch returning zero can make rejected input indistinguishable from a valid zero result. Prefer one clear responsibility over a long list of optional switches.

## Review before continuing

Run the reference and confirm it prints `csharp-007: passed`, then rerun the guide's counterexample.
