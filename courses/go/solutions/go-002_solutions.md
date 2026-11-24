# go-002: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

A type determines which values and operations are valid. int has an implementation-dependent width, while int64 and uint32 declare particular widths. A conversion changes representation; it is not a proof that the original value fits. Untyped numeric constants can retain exact values until context chooses a concrete type. Variables already have concrete types, so mixing integer and floating arithmetic requires an explicit decision. Integer division truncates toward zero. Floating-point values represent a finite set of approximations, and repeated calculations need a tolerance chosen from the domain. Never repair a numerical test with a tolerance large enough to hide a fundamentally wrong algorithm.

var n int64 fixes the variable's type. float64(n) converts the value; converting after integer division cannot restore a lost fraction. uint8 wraps values during nonconstant conversion modulo its range. A constant that cannot fit its target type is rejected by the compiler. math.Abs gives an absolute difference, and strconv.ParseInt returns both a value and an error when decoding external text.

## 1. Compare two divisions: change one input

Copy worked example 1 into a scratch pad and change `a := 7 / 2` to `a := 8 / 2`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.

The unchanged code is worked example 1:

```go
a := 7 / 2
b := float64(7) / 2
check(a == 3 && b == 3.5, "division")
```

**Expected:** The changed run panics with `division` because `a == 3 && b == 3.5` no longer holds. Restoring the original line brings back the worked observation: the results are 3 and 3.5.

Converting before division selects floating arithmetic. float64(7/2) would instead be 3.0 because integer division has already occurred.

**Approach.** Evaluate the edited line before the check: both operands of `8 / 2` are integers, so Go performs integer division and `a` becomes 4. Line `b := float64(7) / 2` is untouched and still holds 3.5.

**Why it holds here.** The check is a conjunction whose first operand is `a == 3`. With 4 in `a` that operand is false, so `check` panics with `division` no matter what `b` holds.

**A plausible wrong approach.** Expecting the original `7 / 2` to round to 4 and therefore predicting that the edit changes nothing. Go integer division truncates toward zero, so the original `a` is 3 and the edited `a` is 4, which is exactly why the check now fails.

**Verify.** Add `fmt.Println(a, b)` above the check. The edited run prints `4 3.5` and panics with `division`; after restoring `7 / 2` it prints `3 3.5` and then `Worked example checks passed.`

## 2. Expose narrowing: debug a regression

A regression changed one token in worked example 2, so one line now reads `n := 261`. Run worked example 2 with that line, use the failure to locate the defect and repair it without changing the check.

The unchanged code is worked example 2:

```go
n := 260
small := uint8(n)
check(small == 4, "narrowing")
```

**Expected:** Before the repair the program panics with `narrowing`; after it the line reads `n := 260` again and the narrowed value is 4.

The eight-bit unsigned result retains the value modulo 256. A direct constant assignment of 260 to uint8 would be rejected instead of silently accepted.

**Approach.** Narrow by hand before running: a `uint8` keeps only the low eight bits, which is the value modulo 256. For 260 that is 4, and for the regressed 261 it is 5.

**Why it holds here.** Because `n` is a variable rather than a constant, `uint8(n)` is a legal run-time conversion that wraps instead of failing, so the check sees 5 and panics with `narrowing`. Restoring 260 restores 4.

**A plausible wrong approach.** Repairing the program by writing `small := uint8(260)` or by changing the check to 5. The first is rejected at compile time because the constant 260 overflows `uint8`, and the second hides the regression by rewriting the claim to match the bug.

**Verify.** Print `small` with each input: 261 shows 5 and 260 shows 4. As an extra control, `n := 516` also yields 4 because 516 is 2 times 256 plus 4, which confirms that only the low byte survives.

## 3. Preserve a wide product

Multiply two explicitly int64 values of 50000.

```go
a, b := int64(50000), int64(50000)
check(a*b == 2500000000, "wide product")
```

**Expected:** The product is 2500000000.

Choose a width that can represent the result before the operation. Converting an already-overflowed result afterward cannot recover the mathematical value.

**Approach.** Give both operands the type `int64` before multiplying, so the multiplication itself runs in 64 bits and `a*b` is 2500000000.

**Why it holds here.** The product exceeds the `int32` maximum of 2147483647 but is far below the `int64` maximum of about 9.22e18, so no wraparound happens and the equality holds exactly.

**A plausible wrong approach.** Multiplying two `int32` variables and converting the result: `x, y := int32(50000), int32(50000)` followed by `int64(x*y)` gives -1794967296, because the product wrapped modulo 2 to the 32nd before the conversion. Writing the same thing with constants does not even compile, since the constant product overflows `int32`.

**Verify.** Run the case and confirm the success line. Then print `int64(x*y)` for the `int32` variables beside `a*b`; seeing -1794967296 next to 2500000000 shows why the width must be chosen before the operation.

## 4. Check approximate arithmetic

Add floating variables 0.1 and 0.2 and compare with a 1e-15 tolerance.

```go
a, b := 0.1, 0.2
check(math.Abs((a+b)-0.3) < 1e-15, "rounding")
```

**Expected:** The absolute difference from 0.3 is below 1e-15.

The tolerance applies to this tiny calculation, not every numerical problem. Relative scale, accumulated error and NaN handling matter in larger algorithms.

**Approach.** Store 0.1 and 0.2 in `float64` variables, add them, and compare the absolute difference from 0.3 with the tolerance `1e-15` instead of testing equality.

**Why it holds here.** Neither 0.1 nor 0.2 is exactly representable in binary, so `a+b` is 0.30000000000000004. Its distance from the stored 0.3 is about 5.55e-17, far below `1e-15`, so the check passes for this one addition.

**A plausible wrong approach.** Testing `a+b == 0.3`, which is false for the variables. A subtler mistake is checking `0.1+0.2 == 0.3` written as literals: Go evaluates untyped constant expressions exactly, so that line is true and hides the `float64` rounding the variables expose.

**Verify.** Print `a+b` and `math.Abs((a+b)-0.3)`: the output is `0.30000000000000004` and `5.551115123125783e-17`. The `rounding` check then passes and the success line appears.

## 5. Reject invalid numeric text

Parse the text 12x as a base-ten signed integer.

```go
_, err := strconv.ParseInt("12x", 10, 64)
check(err != nil, "invalid number")
```

**Expected:** Parsing returns a non-nil error.

Ignoring the error can turn malformed input into a misleading default or partial result. Validation belongs at the boundary where text becomes a numeric value.

**Approach.** Call `strconv.ParseInt("12x", 10, 64)` and treat the returned `err` as the result that matters; the numeric value is discarded with `_`.

**Why it holds here.** `ParseInt` must consume the whole string as a base-ten integer. The trailing `x` is not a digit, so it returns 0 and a `*strconv.NumError` wrapping `strconv.ErrSyntax`, and `err != nil` holds.

**A plausible wrong approach.** Reading the text with `fmt.Sscanf("12x", "%d", &n)`. It scans the leading `12`, stops at `x` and reports no error for the unread tail, so the program would silently accept 12 from malformed input.

**Verify.** Print `err`: it reads `strconv.ParseInt: parsing "12x": invalid syntax`, and `errors.Is(err, strconv.ErrSyntax)` is true. Changing the text to `12` makes `err` nil, which shows the check distinguishes valid from invalid input.

## 6. Transfer signed division

Divide -7 by 2 and compute its remainder.

```go
q, r := -7/2, -7%2
check(q == -3 && r == -1 && q*2+r == -7, "signed division")
```

**Expected:** The quotient is -3 and the remainder is -1.

Truncation toward zero differs from floor division for negative operands. The reconstruction identity confirms the relationship between quotient and remainder.

**Approach.** Compute `-7/2` and `-7%2` with Go's rule that integer division truncates toward zero, giving -3 and -1, and confirm the reconstruction `q*2+r == -7`.

**Why it holds here.** Truncating -3.5 toward zero gives -3, and the remainder must satisfy `q*2 + r == -7`, so it is -1 and takes the sign of the dividend. All three conjuncts hold.

**A plausible wrong approach.** Expecting floor division as in Python, which gives -4 and remainder 1. The reconstruction identity still holds for that pair, but `q == -3` fails, so a port of Python code that relies on floor semantics would compute different buckets for negative inputs.

**Verify.** Print `q, r`: the output is `-3 -1`. For a floor-style result you would need `math.Floor(float64(-7) / 2)`, which prints -4 and makes the difference visible.

## Transfer after comparison

Repeat the lesson with new numbers in your own pad. Predict `9 / 4` as 2 and `float64(9) / 4` as 2.25, narrow a variable holding 300 to `uint8` and predict 44, and divide -9 by 4 to predict -2 with remainder -1. Write one check per claim, then explain which check a rounding, floor-division or constant-narrowing implementation would fail.
