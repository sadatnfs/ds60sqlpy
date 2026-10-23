# cpp-030: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A mutex serializes access to shared state. A condition variable lets a thread wait for a state predicate while releasing the mutex. A queue invariant describes valid states such as size at most capacity. Notifications are hints to recheck state because wakes can be spurious or another thread can consume the item first.

## Detailed reasoning

The queue and closed flag describe one state machine. Empty/open means wait, nonempty means consume, and empty/closed means terminate. All three decisions use the same mutex so the predicate corresponds to the protected data. The predicate overload handles spurious wakes by rechecking rather than assuming a notification means an item exists. A capacity limit adds another state condition: the producer can accept work only when there is room.

## Worked example 1

```cpp
cv.wait(lock,[&]{return !q.empty()||closed;});
```

Expected: The consumer proceeds only when work exists or shutdown has been published.

## Worked example 2

```cpp
if(q.empty() && closed) break;
```

Expected: A closed empty queue ends consumption; closure does not discard queued work.

## Exercise 1: State the invariant

List queue state protected by m.

**Expected:** Queue contents and closed flag share one mutex.

**Reasoning:** Protecting related fields separately can violate their relationship.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Drain before exit

Produce 2 and 3 then close.

**Expected:** Total 5 with both items consumed.

**Reasoning:** Close means no future work, not erase pending work.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Bound the queue

Add capacity 2 and a producer wait predicate.

**Expected:** Observed size never exceeds 2.

**Reasoning:** Producers wait for room while consumers notify after pop.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Repair naked wait

Replace cv.wait(lock) with predicate waiting.

**Expected:** Spurious notifications cannot trigger front on empty queue.

**Reasoning:** A wake does not prove the condition is true.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Test empty close

Close before enqueueing any items.

**Expected:** Consumer exits with total 0.

**Reasoning:** The predicate includes closed to allow termination.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer cancellation

Define whether cancellation drains or discards pending work.

**Expected:** Chosen policy accounts for every accepted item and joins all workers.

**Reasoning:** Shutdown semantics belong in the queue contract.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
