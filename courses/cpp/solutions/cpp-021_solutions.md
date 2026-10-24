# cpp-021: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A strong type wraps a representation in a domain name so unrelated values cannot be mixed accidentally. An explicit constructor blocks implicit conversions. A value API should obey simple laws, such as addition identity and equality symmetry. Domain restrictions must be enforced at construction or operation boundaries.

## Detailed reasoning

The wrapper's job is to stop accidental unit mixing before runtime. A count and an amount may both use long long storage, but only the domain-approved operations should exist. Equality and addition laws give clients predictable behavior. Those laws apply only within the declared numeric domain: overflowing signed arithmetic is not an exotic counterexample to the law, it is an operation outside the program contract. A checked addition API should preserve that distinction.

<!-- depth:start -->
## Strong domain types and operator meaning

Two integers can have incompatible meanings even when their machine representation is identical. A Cents type makes a monetary unit visible at function boundaries. It can prevent a caller from accidentally passing a raw row count where a price is expected, provided its constructors and conversions preserve that separation. This is a domain-model benefit rather than a different arithmetic engine.

An overloaded operator should preserve a familiar, documented meaning. Adding two Cents values produces a Cents result; comparing two values compares their amounts. The complete examples check125=25+100 and the zero identity. They do not establish currency conversion, rounding policy or overflow handling. Those requirements would need distinct types or explicit functions and tests.

The zero value is useful because it supplies an identity for accumulation. If price+zero changes price, either the operator or the type invariant is wrong. Equality should compare the semantic value represented by the type, not an incidental address. In a richer money type, currency would also matter: equal numeric amounts in different currencies should not be casually added.

Operator syntax can hide cost and failure. A small Cents addition is simple, while an overloaded plus that performs network I/O or mutates unrelated state would violate ordinary reader expectations. Prefer explicit named operations when behavior is surprising or requires a policy argument. The goal is clearer code, not making every business action look like arithmetic.

Construction is the boundary where invalid states should be considered. If negative cents are forbidden in one domain but valid for a signed balance in another, one universal wrapper may be misleading. State the type's invariant and choose names accordingly. The lesson uses a tiny representation so the learner can separate unit correctness from the later checked-arithmetic policy.

## Debugging the contract

If raw integers slip into a Cents API unexpectedly, inspect implicit constructors and conversion operators. If an operator mutates its left input when it is expected to return a new value, compare the intended value semantics with the implementation. If a large amount wraps or overflows, strong typing alone is not enough: add the numeric range policy. Keep unit tests distinct from arithmetic-boundary tests.
<!-- depth:end -->

## Worked example 1

```cpp
Cents price{125}; Cents discount{25}; assert((discount+Cents{100})==price);
```

Expected: The API retains cents units and produces 125 cents.

## Worked example 2

```cpp
assert((Cents{125}+Cents{0})==Cents{125});
```

Expected: Zero is the addition identity for this bounded domain.

## Exercise 1: Name the units

Compare Cents{125} with item count 125.

**Expected:** Equal representation, different domain meaning.

**Reasoning:** Names prevent treating every integer as interchangeable.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Test identity

Add zero to Cents{125}.

**Expected:** Cents{125}.

**Reasoning:** The operation should preserve the value at the identity.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Construct a separate type

Add struct ItemCount and avoid mixed addition.

**Expected:** Cents+ItemCount has no valid overload.

**Reasoning:** Omitting meaningless operations is an interface feature.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Repair implicit conversion

Review a non-explicit raw integer constructor.

**Expected:** Use explicit construction at the domain boundary.

**Reasoning:** Implicit conversion can silently cross units.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Check equality laws

Compare a=125, b=125, c=125.

**Expected:** Reflexive, symmetric and transitive equality for these values.

**Reasoning:** Default member equality implements the value contract.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer safety

Specify checked addition when values approach LLONG_MAX.

**Expected:** Reject overflow before calculating a+b.

**Reasoning:** Strong naming does not prevent representation overflow.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
