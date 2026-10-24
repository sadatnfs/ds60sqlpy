# cpp-030: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A mutex serializes access to shared state. A condition variable lets a thread wait for a state predicate while releasing the mutex. A queue invariant describes valid states such as size at most capacity. Notifications are hints to recheck state because wakes can be spurious or another thread can consume the item first.

## Detailed reasoning

The queue and closed flag describe one state machine. Empty/open means wait, nonempty means consume, and empty/closed means terminate. All three decisions use the same mutex so the predicate corresponds to the protected data. The predicate overload handles spurious wakes by rechecking rather than assuming a notification means an item exists. A capacity limit adds another state condition: the producer can accept work only when there is room.

<!-- depth:start -->
## Condition variables coordinate a state machine

A condition variable is a waiting mechanism, not the shared condition itself. The real condition is expressed in protected state. This queue has a sequence of pending integers and a closed flag. Empty/open means there is currently no work but more may arrive. Nonempty means the consumer can take an item. Empty/closed means no more work can arrive and the consumer should finish.

The mutex protects both the queue and the closed flag. The consumer holds a unique_lock and calls the predicate overload of wait. Waiting releases the mutex so a producer can change the state, then reacquires it before the predicate is evaluated again. A wakeup alone does not guarantee an item exists: spurious wakeups and other consumers can change the situation. The predicate is the source of truth.

The first program enqueues2 and 3, then closes the queue while holding the mutex. The consumer drains the existing items even though closed is true, because nonempty still means work exists. Only empty and closed together terminate the loop. Exiting immediately on closed would discard accepted work. Waiting only for nonempty would hang after the last item because closure would not satisfy the condition.

The second program starts with an already empty, closed queue. The predicate is immediately true, so no notification is needed to make progress. This demonstrates why notifications should not be treated as stored messages. State persists; a notification may occur before another thread begins waiting. Rechecking the state under the same mutex avoids depending on an exact notification schedule.

A bounded queue adds a capacity predicate for producers. When full, the interface must choose whether to wait, reject or cancel a submission. That policy belongs to the product contract and should be tested separately from consumer wakeup. The small reference has a fixed two-item input; it demonstrates correct draining and closure, not a production executor with backpressure and arbitrary task scheduling.

## Debugging the contract

If the consumer hangs after processing all items, inspect whether closed participates in the wait predicate. If items disappear during shutdown, check whether the loop exits before draining a nonempty closed queue. If state is read outside the mutex, a notification cannot repair the race. Keep every predicate variable under the same synchronization contract and test empty/open, nonempty and empty/closed separately.
<!-- depth:end -->

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
