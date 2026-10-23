# cpp-031: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

An atomic operation accesses one object without a data race. Memory ordering describes which other operations become visible across threads. A happens-before relation provides the reasoning chain for shared non-atomic data. Relaxed atomics are useful for independent counters but do not automatically publish surrounding objects.

## Detailed reasoning

Atomicity prevents torn or lost updates to the counter itself. Publication asks a broader question: may a consumer safely read an earlier non-atomic payload write? The release store and matching acquire load form that ordering bridge. Relaxed is adequate for independent counting followed by join, but replacing the publication pair with relaxed accesses would remove the required argument for the payload. The lesson tests an actual shared-data relationship, not only a final number.

## Worked example 1

```cpp
count.fetch_add(1,std::memory_order_relaxed);
```

Expected: Each increment is indivisible; two workers making 1000 increments produce 2000 after join.

## Worked example 2

```cpp
payload=7; ready.store(true,std::memory_order_release);
```

Expected: An acquire load observing this store can safely read the preceding payload write.

## Exercise 1: Count atomic work

Run two workers with 1000 increments each.

**Expected:** Final count 2000 after both joins.

**Reasoning:** Atomic read-modify-write prevents lost increments.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Explain relaxed

State why relaxed suffices for the isolated counter.

**Expected:** No payload publication relies on counter ordering.

**Reasoning:** Atomicity and visibility ordering solve different problems.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Trace publication

Draw payload write, release store, acquire load and payload read.

**Expected:** A synchronization chain orders the payload access.

**Reasoning:** The acquire must observe the relevant release.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Reject a data race

Review plain shared int increments without synchronization.

**Expected:** Reject as undefined behavior; do not normalize a lucky total.

**Reasoning:** Observed success cannot legalize a data race.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Test zero workers

Set work count to zero and inspect the counter.

**Expected:** 0 without a publication claim.

**Reasoning:** Initial atomic state is a valid boundary.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer multiple fields

Publish two fields behind one ready release/acquire pair.

**Expected:** Both earlier writes visible after the matching acquire.

**Reasoning:** Do not mutate the payload again without a new protocol.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
