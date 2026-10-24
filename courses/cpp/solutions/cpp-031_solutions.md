# cpp-031: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

An atomic operation accesses one object without a data race. Memory ordering describes which other operations become visible across threads. A happens-before relation provides the reasoning chain for shared non-atomic data. Relaxed atomics are useful for independent counters but do not automatically publish surrounding objects.

## Detailed reasoning

Atomicity prevents torn or lost updates to the counter itself. Publication asks a broader question: may a consumer safely read an earlier non-atomic payload write? The release store and matching acquire load form that ordering bridge. Relaxed is adequate for independent counting followed by join, but replacing the publication pair with relaxed accesses would remove the required argument for the payload. The lesson tests an actual shared-data relationship, not only a final number.

<!-- depth:start -->
## Atomic counting and publishing related data

An atomic operation makes an access to that atomic object indivisible under its specified ordering. It does not automatically protect every nearby variable. Counting independent events and publishing a non-atomic payload are different problems, so the examples deliberately use two different synchronization arguments.

For the counter, each fetch_add contributes one increment. Two workers each add1000, and main joins both before checking2000. Relaxed ordering is enough for the counter's atomic updates because no additional payload visibility is being communicated through each increment. join supplies completion before the final observation. Replacing fetch_add with an unsynchronized read-modify-write on an ordinary int would permit lost updates and a data race.

Publication uses a separate payload and ready flag. The producer writes payload=7 and then performs a release store of true. The consumer loops until an acquire load observes that publication, then reads payload. The release/acquire relationship orders the earlier payload write before the consumer's later read. This is an inter-thread visibility argument, not merely a promise that the flag eventually changes.

Changing both flag operations to relaxed would retain atomicity of ready but remove this publication argument for payload. The fact that a particular machine often prints 7 is not a substitute for the language memory model. Likewise, volatile is not a general thread-synchronization mechanism. Start from the required happens-before relationship and choose operations that establish it.

Memory ordering is easy to overcomplicate. A mutex can be clearer when multiple fields form one invariant or when the design is not a simple publication pattern. Stronger ordering may be an acceptable starting point while the interface is developed. Weakening ordering for speed requires both a correct proof and a measurement showing the change matters. The lesson's bounded examples do not constitute a lock-free container design.

## Debugging the contract

If the counter is sometimes below2000, inspect whether every increment is one atomic read-modify-write and whether workers are joined. If the payload has no ordering relationship, do not trust repeated successful runs. Find the release store and the acquire load that actually observes it. If several fields must change consistently, consider a mutex instead of treating each field as an unrelated atomic and hoping the combined state is coherent.
<!-- depth:end -->

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
