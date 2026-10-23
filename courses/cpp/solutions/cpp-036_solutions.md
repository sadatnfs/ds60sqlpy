# cpp-036: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

constexpr permits a function or object to participate in constant evaluation when its inputs and operations allow it. consteval requires a call to be evaluated during compilation. Compile-time computation moves work into the build and can inflate build time or binary size. It is useful for bounded validation rather than unlimited metaprogramming.

## Detailed reasoning

Constant evaluation moves computation to a different phase rather than making it free. A static_assert cannot wait for user input, while an ordinary call to a constexpr function can use a runtime variable. consteval deliberately forbids that runtime choice. Large generated tables may increase compilation work and binary size even if runtime lookups become simple. Keep both the mathematical input range and the build resource budget explicit.

## Worked example 1

```cpp
static_assert(square(4)==16);
```

Expected: The compiler validates the expression before an executable exists.

## Worked example 2

```cpp
int runtime=5; assert(square(runtime)==25);
```

Expected: The same constexpr function may be evaluated during program execution.

## Exercise 1: Distinguish phases

Classify static_assert(square(4)==16) and square(runtime).

**Expected:** First compile-time requirement; second runtime-capable call.

**Reasoning:** constexpr permits rather than universally forces compile time.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Add a lookup table

Build squares for indices 0 through 4 with constexpr data.

**Expected:** [0,1,4,9,16].

**Reasoning:** Small bounded tables can replace repeated work.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Force constant evaluation

Create a consteval limit function and call with constant input.

**Expected:** Build succeeds with a constant result.

**Reasoning:** Immediate functions require compile-time evaluation.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Diagnose runtime argument

Pass an input read at runtime to a consteval function.

**Expected:** Compilation fails; use constexpr when runtime calls are needed.

**Reasoning:** The phase requirement is part of the interface.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Check a numeric boundary

Limit table inputs so multiplication cannot overflow int.

**Expected:** Declared bound and safe result range documented.

**Reasoning:** Compile-time evaluation still obeys arithmetic rules.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer build budget

Compare bounded table sizes 16 and 256 in an owned host build.

**Expected:** Record compile duration and artifact size without asserting a universal ratio.

**Reasoning:** Build-time work is a resource that also needs a budget.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
