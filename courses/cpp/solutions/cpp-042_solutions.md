# cpp-042: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

The bounded parallel analyzer combines parsing, ownership, concurrency and evidence. A serial oracle establishes the intended result independently of scheduling. A task budget controls worker count and input size. Failure accounting names rejected input and cancelled work rather than hiding them inside an apparently successful total.

## Detailed reasoning

The serial oracle supplies a simple independent answer, 21. The two workers read disjoint slices of one const vector and write separate subtotal variables, then the owner joins both before combining 6 and 15. The uneven five-row case exposes a partitioning bug that equal halves can hide. Extending this to parsed input adds another conservation rule: every original row is accepted or rejected, and every accepted task is completed or explicitly cancelled before a report is published.

<!-- depth:start -->
## Parallel analysis with conservation of work

The final product combines parsing, ownership, concurrency and reporting. Raw rows are either accepted or rejected under a strict grammar. Accepted values are then assigned to bounded work. Every accepted task must end as completed, cancelled or failed before the operation can describe its outcome. These conservation rules prevent plausible partial totals from hiding lost input or abandoned work.

The serial oracle sums [1, 2, 3, 4, 5, 6] to 21. The parallel example gives disjoint slices to two workers, producing6 and 15, then joins both before combining. The input vector remains alive and unchanged throughout. Each worker writes its own subtotal variable, so the example does not require competing updates to one shared accumulator. The owner reads those subtotals only after joins.

Partition boundaries need tests beyond an even-length input. An odd-sized vector can expose a dropped middle element or overlapping slice. Empty input can expose invalid first-element access. Repeated values can hide an overlap if only one aggregate is inspected, so retain counts and compare with the independent serial oracle. A faster wrong partition is not a successful parallel implementation.

The executable reference adds strict raw-string parsing, at most100 rows, two workers and an injected worker failure. On failure, it publishes no partial total. Scheduling can affect how much other work completed before the stop request was observed, so the expected cancelled count is not one fixed number. The invariant completed+cancelled+failed_tasks=accepted is stable across those schedules.

Cancellation is cooperative, and thread creation can itself fail. If the second thread cannot be started, the already created first worker must receive a stop request and be joined before the exception leaves the owner scope. Otherwise cleanup can terminate the process or leave borrowed state unsafe. Error handling around worker creation is part of the product, not only the worker loop.

The final evidence packet includes normal, malformed, empty, uneven, budget and injected-failure cases, plus source/build/runtime identity. The small in-memory admission vector is bounded, but it is not a production unbounded queue or distributed executor. Explain that limitation while defending the actual ownership, accounting and failure-publication behavior demonstrated by the reference.

## Debugging the contract

If the parallel total differs from serial, inspect slice coverage and overlap before changing arithmetic. If an injected failure still prints a normal partial total, repair the publication gate. If cancelled counts vary, check the conservation invariant rather than asserting one schedule. If thread creation throws after another worker starts, ensure that worker is stopped and joined. If malformed rows vanish from accounting, repair the parse boundary before analyzing concurrency.
<!-- depth:end -->

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

Compare two-worker total on [1, 2, 3, 4, 5, 6] with serial oracle.

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

Check zero rows and five rows [1, 2, 3, 4, 5].

**Expected:** Totals 0 and 15 with no lost tail.

**Reasoning:** Partition bounds must cover a half-open range exactly once.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Deliver reviewer packet

Include source, fixtures, serial oracle, failure test, build/run receipts and limits.

**Expected:** A second learner reproduces normal, empty, invalid and failure cases.

**Reasoning:** Production-quality evidence includes failure handling and platform limits, not a speed claim alone.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
