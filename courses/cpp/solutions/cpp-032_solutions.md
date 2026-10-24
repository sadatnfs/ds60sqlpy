# cpp-032: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

Bounded parallel work limits simultaneous workers and queued items. Backpressure slows producers when the system has no capacity. Failure propagation carries a worker error to the owner instead of silently producing partial success. Cancellation and joining are part of the resource contract, not optional cleanup.

## Detailed reasoning

The two-task future example makes a fixed worker bound visible and propagates failure through get. It is deliberately smaller than a production executor. A real executor also needs a queue capacity, an admission policy and a rule for accepted work when one task fails. The owner must observe each result or exception and account for pending/cancelled work before publishing a total. Discarded exceptions and partial aggregates are not successful parallel execution.

<!-- depth:start -->
## Futures, launch policy and bounded work ownership

A future represents a result that may become available later. It carries either a value or an exception from the asynchronous operation. Calling get waits as needed and retrieves that outcome. A valid future is normally consumed once by get; treating it as a reusable result object can produce a no-state error on a later call.

The examples use std::launch::async explicitly so the operation is launched asynchronously rather than leaving a deferred policy choice to the implementation. That still does not define a production thread pool. Launching one async task per row in a very large input can create an unacceptable amount of concurrency or resource pressure. The lesson uses a fixed small number of tasks so the ownership and result flow are visible.

The success program computes the square of 3 and observes9 through get. The failure program launches a task with -1, where checked_square throws invalid_argument. The exception is stored and rethrown when main calls get. A flag confirms that the specific error was observed. Ignoring the future or never retrieving its outcome can hide a failed task from the application report.

When combining multiple tasks, define whether one failure aborts the whole result or whether partial results have a valid meaning. A total assembled from successful tasks alone can look plausible while silently omitting failures. Keep accepted, completed, failed and cancelled work accounting explicit. Cancellation of pending work also needs a mechanism; future by itself is not a general cancel operation.

A real executor has at least worker count, queue capacity, submission policy, result ownership and shutdown behavior. Those are separate choices. The fixed-two-task example illustrates result propagation but does not implement every executor feature. The final capstone returns to bounded admission and conservation of work so that a failed parallel computation cannot publish an unexplained partial total.

## Debugging the contract

If an asynchronous error never appears, inspect whether every accepted task has its future observed. If too many threads appear, check whether input size is directly controlling async launch count. If get is called twice, store the first returned value rather than reusing a consumed future. If a partial aggregate is printed after one task fails, repair the publication and accounting policy before discussing performance.
<!-- depth:end -->

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
