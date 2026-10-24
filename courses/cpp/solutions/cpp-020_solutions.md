# cpp-020: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A template describes a family of functions parameterized by types. Deduction selects a type from arguments. A concept is a compile-time requirement that determines which template candidates are valid. A constraint improves the interface boundary, but it does not automatically prove arithmetic safety.

## Detailed reasoning

Template deduction happens before any generated function runs. Equal int arguments select one specialization; int and long long arguments can produce conflicting deductions because this signature asks for one T. A concept rejects categories that lack the intended operations, often near the call site. It cannot make every admitted value safe. The overflow check in later lessons is still needed even though integral<int> is true.

<!-- depth:start -->
## Templates and constraints as interface documentation

A function template describes a family of functions parameterized by types or values. The compiler instantiates the needed specialization from a call. Generic syntax alone does not explain what operations are valid for a type, so constraints can make the intended domain visible before a deeply nested implementation error appears.

The integral constraint says that the type belongs to the language/library concept for integral types. The complete program instantiates identity_sum for integers and checks2+3=5. The second program uses static_assert to establish that double is not integral. That assertion is checked during compilation and produces no runtime branch. The actual negative exercise attempts a constrained call with double and retains the compiler diagnostic.

A syntactic constraint is not the whole semantic contract. Integral addition can still overflow for signed types, and mixing signed and unsigned arguments can affect deduction or conversions. A template constrained to integral types must still state supported value ranges and any overflow policy. Concepts should not be advertised as automatic arithmetic safety or proof of all algorithm assumptions.

Template argument deduction also requires compatible inputs. A function taking two values of the same template parameter may reject an int and long combination even when a programmer considers both numbers. An explicit conversion can resolve the call, but it should be deliberate because narrowing or sign changes can lose meaning. Inspect the inferred types when a call does not match expectations.

Good constraints describe the weakest capabilities the implementation actually needs. Requiring a random-access container for a one-pass accumulation unnecessarily excludes useful inputs. Conversely, accepting any type while relying on an undocumented operation shifts the error into the implementation. The aim is a readable contract and useful diagnostics, followed by ordinary value-boundary tests.

## Debugging the contract

If template errors are long, find the first failed constraint or mismatched deduced type rather than the final cascade. If a valid type produces a wrong numeric result, inspect values and conversions: type constraints do not prevent overflow. If an interface rejects an input range unnecessarily, compare the declared capability with the operations actually used. Do not weaken every constraint to make one call compile without reviewing the algorithm assumptions.
<!-- depth:end -->

## Worked example 1

```cpp
assert(identity_sum(2,3)==5);
```

Expected: Deduction selects int and the result is 5.

## Worked example 2

```cpp
static_assert(!std::integral<double>);
```

Expected: double does not satisfy this integral-only interface.

## Exercise 1: Read deduction

Call identity_sum with int values and long long values.

**Expected:** Result types int and long long respectively.

**Reasoning:** The argument types choose template instantiations.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Reject a category

Try identity_sum with two strings in a scratch file.

**Expected:** Constraint-related compile failure.

**Reasoning:** Strings do not satisfy integral.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Add a concept

Constrain a function to signed_integral.

**Expected:** int accepted; unsigned rejected.

**Reasoning:** A narrower category documents intent.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Repair mixed deduction

Call identity_sum(2, 3LL), then choose a deliberate common type.

**Expected:** Mixed call fails deduction; explicit long long arguments succeed.

**Reasoning:** Conflicting deductions need a policy, not an accidental conversion.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Inspect numeric boundary

Explain why INT_MAX+1 is still unsafe for integral T=int.

**Expected:** Concept accepts int but cannot make overflow valid.

**Reasoning:** Type eligibility is distinct from value validity.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer a generic test

Run zero-identity tests for int and long long.

**Expected:** sum(x, 0)==x for bounded x=7 in both types.

**Reasoning:** A reusable law should be checked across admitted types.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
