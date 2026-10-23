# cpp-032: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

Bounded parallel work limits simultaneous workers and queued items. Backpressure slows producers when the system has no capacity. Failure propagation carries a worker error to the owner instead of silently producing partial success. Cancellation and joining are part of the resource contract, not optional cleanup.

## Worked example 1

```cpp
auto f=std::async(std::launch::async,checked_square,3); assert(f.get()==9);
```

Expected: The future yields 9 and waits for completion if necessary.

## Worked example 2

```cpp
auto f=std::async(std::launch::async,checked_square,-1); // get rethrows
```

Expected: The worker failure is observed by the caller through get.

## Exercise 1: Set a budget

Define maximum workers 2 and queued tasks 4.

**Expected:** Both bounds documented independently.

**Reasoning:** Limiting workers alone can still allow an unbounded queue.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Compare serial results

Square 3 and 4 serially and in two futures.

**Expected:** Exact total 25 in both paths.

**Reasoning:** Parallelism must preserve the correctness contract.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Propagate a failure

Include task -1 and call get.

**Expected:** invalid_argument reaches the owner.

**Reasoning:** A future carries exceptions as well as values.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Repair fire-and-forget

Review discarded futures and missing result accounting.

**Expected:** Observe every result or exception and join owned work.

**Reasoning:** Unhandled failure cannot be labeled successful completion.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Test empty workload

Run no tasks through the serial/reference contract.

**Expected:** Empty results and total 0.

**Reasoning:** Do not create unnecessary workers for no input.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer backpressure

Sketch a capacity-4 queue for ten tasks and two consumers.

**Expected:** At most 2 running plus 4 queued, remaining producer work blocked.

**Reasoning:** Admission and completion counts provide inspectable bounds.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
