# cpp-038: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

Integer overflow and floating-point rounding are different correctness problems. Signed overflow is undefined; floating values approximate many decimal fractions. A tolerance defines acceptable numerical error for a specific scale. Stable algorithms reduce accumulated error, but exact money and identity arithmetic should use exact representations whenever possible.

## Detailed reasoning

The integer guard is arranged to avoid evaluating the dangerous sum. Because inputs are nonnegative, max-b is safe and can be compared with a before adding. Floating addition follows a different model: rounding can make different parenthesizations of [1e16, 1, -1e16] produce different results. Use exact arithmetic for integer cents and justify approximate tolerances using scale and units. A loose tolerance must not conceal an incorrect algorithm.

<!-- depth:start -->
## Integer overflow and floating-point error are different

Integer arithmetic and floating-point arithmetic have different contracts. Signed integer overflow is not a defined wraparound policy in C++. A checked-add function must establish that the result is representable before evaluating the dangerous addition. Checking whether the sum became negative after overflow is too late because the invalid operation already occurred.

For nonnegative a and b, the guard a>max-b detects whether a+b would exceed the maximum. max-b is safe under the stated nonnegative supported range. Only after that guard passes should the addition be evaluated. If negative operands are allowed, the guard logic must cover underflow and other sign combinations separately. A formula valid for one restricted domain is not automatically a general checked-add implementation.

Floating-point values represent a finite set of numbers with rounding. Decimal0.1 and 0.2 do not generally have exact finite binary representations, so their sum can differ slightly from the stored approximation of 0.3. The complete example uses a small tolerance for this specific comparison. That does not justify one universal tolerance for every scale or unit.

Addition order can matter because intermediate rounding occurs. Summing [1e16, 1, -1e16] in one order can lose the small contribution, while another grouping can preserve it. Parallel reduction can change grouping, so exact bitwise equality may require a stronger reproducibility design. For integer cents within a checked range, exact comparison remains appropriate; do not introduce approximate tolerances to hide a wrong integer result.

Choose numeric representation from the domain. Money may use checked integer minor units or a deliberate decimal representation. Measurements may need floating-point with error bounds, scale-aware comparison and stable algorithms. More precision can reduce some error but cannot substitute for an explicit contract or eliminate every conditioning problem.

## Debugging the contract

If a checked sum computes a+b before its guard, the protection is ineffective. If a nonnegative-only helper receives negative input, reject it or implement the broader signed contract. If a floating test fails at a different scale, review absolute versus relative tolerance and units. If a parallel total differs slightly, inspect grouping and rounding before assuming a race, while still checking synchronization independently.
<!-- depth:end -->

## Worked example 1

```cpp
assert(!safe_add(std::numeric_limits<int>::max(), 1));
```

Expected: The operation rejects the input before evaluating an overflowing sum.

## Worked example 2

```cpp
assert(std::abs((0.1 + 0.2) - 0.3) < 1e-12);
```

Expected: The binary floating result is close within this declared absolute tolerance.

## Exercise 1: Keep exact units

Add 100 and 25 integer cents.

**Expected:** Exactly 125 cents.

**Reasoning:** No approximate representation is needed.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Reject overflow

Try INT_MAX plus 1.

**Expected:** Absent result without evaluating overflow.

**Reasoning:** A check after overflow is too late.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Inspect rounding

Print 0.1+0.2 with sufficient precision.

**Expected:** Possible difference from 0.3 is recorded with a suitable tolerance.

**Reasoning:** Decimal fractions may lack finite binary representations.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Repair one-size tolerance

Explain why epsilon=0.1 is poor for both tiny and huge measurements.

**Expected:** A scale-aware absolute/relative policy stated.

**Reasoning:** Tolerance depends on units and error budget.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Check zero boundary

Run safe_add(0, 0) and safe_add(-1, 2).

**Expected:** Present 0 and rejected negative input.

**Reasoning:** The subtraction-based guard assumes nonnegative inputs.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer stability

Compare sums [1e16, 1, -1e16] under different groupings.

**Expected:** Floating sums can differ; exact expected mathematical total is 1.

**Reasoning:** Associativity is not guaranteed by floating arithmetic.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
