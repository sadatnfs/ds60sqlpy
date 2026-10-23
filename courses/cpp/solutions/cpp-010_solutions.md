# cpp-010: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A struct groups related fields into one value. An enum class defines a closed vocabulary of named states and prevents accidental integer mixing. An invariant describes combinations that make sense, such as a settled payment carrying nonnegative cents. Domain names make invalid combinations visible at the boundary.

## Detailed reasoning

Data fields are useful only together with their meaning. An ID answers which payment this is, cents answers how much, and Status answers its business state. Two distinct IDs with the same amount are not automatically duplicates. A pending payment contributes no settled revenue but still exists in an audit ledger. A negative amount violates this lesson's model even if a branch would otherwise ignore it, so the invariant check happens before state-specific contribution.

## Worked example 1

```cpp
Payment p{7,200,Status::paid}; assert(settled(p)==200);
```

Expected: A paid record contributes 200 cents.

## Worked example 2

```cpp
Payment p{8,200,Status::pending}; assert(settled(p)==0);
```

Expected: Pending contributes zero to settled revenue while retaining its original amount.

## Exercise 1: Read the record

Describe each field of Payment{7,200,paid}.

**Expected:** Identity 7, integer cents 200, named state paid.

**Reasoning:** Identity and amount serve different purposes.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Filter state

Aggregate paid 200 and pending 200 records.

**Expected:** Settled total 200, input count 2.

**Reasoning:** Filtering contribution does not delete input evidence.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Add a named state

Add refunded and specify a zero settled contribution policy.

**Expected:** paid 200 plus refunded 200 contributes 200.

**Reasoning:** Define behavior for every named state.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Reject an invalid amount

Construct paid amount -1 and call settled.

**Expected:** invalid_argument before returning revenue.

**Reasoning:** Validate amounts independently of state filtering.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Retain zero payments

Inspect paid 0.

**Expected:** Valid paid record contributing 0.

**Reasoning:** Zero is a valid amount, not invalid data.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer identity

Use two paid records with equal 200 amounts and distinct IDs.

**Expected:** Total 400 and two identities.

**Reasoning:** Value equality does not imply duplicate business events.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
