# cpp-021: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A strong type wraps a representation in a domain name so unrelated values cannot be mixed accidentally. An explicit constructor blocks implicit conversions. A value API should obey simple laws, such as addition identity and equality symmetry. Domain restrictions must be enforced at construction or operation boundaries.

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

Compare a=125,b=125,c=125.

**Expected:** Reflexive, symmetric and transitive equality for these values.

**Reasoning:** Default member equality implements the value contract.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer safety

Specify checked addition when values approach LLONG_MAX.

**Expected:** Reject overflow before calculating a+b.

**Reasoning:** Strong naming does not prevent representation overflow.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
