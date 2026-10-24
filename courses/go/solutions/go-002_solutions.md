# go-002: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

A type determines which values and operations are valid. int has an implementation-dependent width, while int64 and uint32 declare particular widths. A conversion changes representation; it is not a proof that the original value fits. Untyped numeric constants can retain exact values until context chooses a concrete type. Variables already have concrete types, so mixing integer and floating arithmetic requires an explicit decision. Integer division truncates toward zero. Floating-point values represent a finite set of approximations, and repeated calculations need a tolerance chosen from the domain. Never repair a numerical test with a tolerance large enough to hide a fundamentally wrong algorithm.

var n int64 fixes the variable's type. float64(n) converts the value; converting after integer division cannot restore a lost fraction. uint8 wraps values during nonconstant conversion modulo its range. A constant that cannot fit its target type is rejected by the compiler. math.Abs gives an absolute difference, and strconv.ParseInt returns both a value and an error when decoding external text.

## 1. Compare two divisions

Compute 7/2 and float64(7)/2.

```go
a := 7 / 2
b := float64(7) / 2
check(a == 3 && b == 3.5, "division")
```

**Expected:** The results are 3 and 3.5.

Converting before division selects floating arithmetic. float64(7/2) would instead be 3.0 because integer division has already occurred.

## 2. Expose narrowing

Convert a variable holding 260 to uint8.

```go
n := 260
small := uint8(n)
check(small == 4, "narrowing")
```

**Expected:** The narrowed value is 4.

The eight-bit unsigned result retains the value modulo 256. A direct constant assignment of 260 to uint8 would be rejected instead of silently accepted.

## 3. Preserve a wide product

Multiply two explicitly int64 values of 50000.

```go
a, b := int64(50000), int64(50000)
check(a*b == 2500000000, "wide product")
```

**Expected:** The product is 2500000000.

Choose a width that can represent the result before the operation. Converting an already-overflowed result afterward cannot recover the mathematical value.

## 4. Check approximate arithmetic

Add floating variables 0.1 and 0.2 and compare with a 1e-15 tolerance.

```go
a, b := 0.1, 0.2
check(math.Abs((a+b)-0.3) < 1e-15, "rounding")
```

**Expected:** The absolute difference from 0.3 is below 1e-15.

The tolerance applies to this tiny calculation, not every numerical problem. Relative scale, accumulated error and NaN handling matter in larger algorithms.

## 5. Reject invalid numeric text

Parse the text 12x as a base-ten signed integer.

```go
_, err := strconv.ParseInt("12x", 10, 64)
check(err != nil, "invalid number")
```

**Expected:** Parsing returns a non-nil error.

Ignoring the error can turn malformed input into a misleading default or partial result. Validation belongs at the boundary where text becomes a numeric value.

## 6. Transfer signed division

Divide -7 by 2 and compute its remainder.

```go
q, r := -7/2, -7%2
check(q == -3 && r == -1 && q*2+r == -7, "signed division")
```

**Expected:** The quotient is -3 and the remainder is -1.

Truncation toward zero differs from floor division for negative operands. The reconstruction identity confirms the relationship between quotient and remainder.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
