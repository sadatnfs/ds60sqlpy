# cpp-042: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

The bounded parallel analyzer combines parsing, ownership, concurrency and evidence. A serial oracle establishes the intended result independently of scheduling. A task budget controls worker count and input size. Failure accounting names rejected input and cancelled work rather than hiding them inside an apparently successful total.

## Worked example 1

```cpp
const std::vector<int> rows{1,2,3,4,5,6}; assert(serial_total(rows)==21);
```

Expected: The independent serial oracle is exactly 21.

## Worked example 2

```cpp
a.join(); b.join(); assert(first==6 && second==15);
```

Expected: Two disjoint partitions combine to 21 after both workers finish.

## Exercise 1: Define budgets

Declare at most 2 workers, 100 input rows and 16 characters per integer field.

**Expected:** Three limits plus rejection behavior documented.

**Reasoning:** The capstone must bound input, concurrency and parsing work.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Prove serial parity

Compare two-worker total on [1,2,3,4,5,6] with serial oracle.

**Expected:** Subtotals 6 and 15; total 21.

**Reasoning:** Partitioning cannot drop or duplicate a row.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Account for bad rows

Add strings bad and 3x through the strict parser.

**Expected:** Six accepted, two rejected, accepted total 21.

**Reasoning:** Whole-field validation preserves the original ledger.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Inject worker failure

Make one partition report an error before publication.

**Expected:** No successful combined report; error and completed/cancelled work accounted.

**Reasoning:** Partial totals must not be mislabeled complete.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Test empty and uneven work

Check zero rows and five rows [1,2,3,4,5].

**Expected:** Totals 0 and 15 with no lost tail.

**Reasoning:** Partition bounds must cover a half-open range exactly once.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Deliver reviewer packet

Include source, fixtures, serial oracle, failure test, build/run receipts and limits.

**Expected:** A second learner reproduces normal, empty, invalid and failure cases.

**Reasoning:** Production-quality evidence includes failure handling and platform limits, not a speed claim alone.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
