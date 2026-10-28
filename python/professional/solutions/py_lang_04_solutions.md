# python-lang-04: Explained solutions

The [executable reference](py_lang_04_solution.py) implements the six contracts and
contains independent expected-value, failure, and lifetime assertions. Read the
[learner guide](../companion-guides/py_lang_04.md) for the complete run workflow and
attempt each [learner function](../lessons/py_lang_04.py) before comparing. The
reference runs entirely offline in the prepared Docker Python classroom; its
assertions are behavioral evidence for these fixtures, not a claim about unseen
learner work or external system acceptance.

## Exercise 1: Return ordered structured results

**Inputs:** A small finite tuple of integer values and an asynchronous operation for each value.

**Expected:** Create one child per value inside asyncio.TaskGroup, await group exit, and return results in input order regardless of completion order. Empty input returns (). A child Exception must propagate as an ExceptionGroup after sibling cleanup; do not return partial success or leave child tasks running.

**Verify:** Operations deliberately released in reverse order for (1, 2, 3) still return (10, 20, 30). An injected child failure cancels a waiting sibling and its finally block runs before the group exits.

ordered_group retains task objects in the same order as values while the TaskGroup owns their execution. Successful exit establishes that every child has completed, so reading result at that point is valid. Completion order does not affect presentation order. The failure fixture makes one child wait after signalling readiness and another raise only after that readiness signal. This proves the first child entered its finally-protected region before cancellation. Group exit raises an ExceptionGroup, and both finally observations must be present before the caller handles it. Returning whatever results happen to be available would silently change the promised all-success tuple. Empty input creates no children and returns an empty tuple. These semantics apply to cooperative tasks in a single loop; they do not imply CPU parallelism or automatically cancel effects already performed by external systems.

## Exercise 2: Limit active work with cleanup

**Inputs:** A small finite tuple, an async operation, an exact positive integer limit, and an event list.

**Expected:** Use a TaskGroup plus a Semaphore so at most limit operation calls are active. Record ("start", value) after acquisition and ("finish", value) in finally before releasing the slot. Preserve input result order and propagate group failure/caller cancellation after cleanup. Reject invalid limits with ValueError even for empty input. This bounds active calls, not the number of scheduled tasks.

**Verify:** Six yielding operations with limit 2 return their six squares. Walk the event transcript to prove active work never exceeds 2 and ends at zero. Under failure every recorded start has a matching finish.

The semaphore belongs to one invocation, so separate runs do not accidentally share a capacity budget. Each child acquires a slot before its start event and before calling the operation. Its finish event is in a finally block inside the semaphore context, ensuring it is recorded before the slot becomes available again. A transcript walk increments on start and decrements on finish, checking every intermediate count rather than only a final total. This independently demonstrates a ceiling of two and a final count of zero. TaskGroup supplies sibling cancellation and awaited cleanup after failure. The input is deliberately small and finite: a semaphore limits active operations, while this implementation still schedules one child for every input. For a large or unbounded stream the prerequisite's bounded queue is the appropriate ownership and backpressure extension.

## Exercise 3: Put a deadline around owned work

**Inputs:** A factory for one awaitable and a finite strictly positive int or float deadline in seconds, excluding bool.

**Expected:** Validate the deadline before calling the factory. Use asyncio.timeout to return success or raise TimeoutError after timed-out work has finished its finally cleanup. A cancellation from the caller remains asyncio.CancelledError; an operation ValueError remains ValueError. Do not manufacture fallback values.

**Verify:** An immediately completing operation returns 7. A blocked local Event wait times out and records closed before TimeoutError is observed. Reject zero, negative, True, infinity, and NaN without calling the factory.

The deadline is checked before the factory is invoked, so invalid configuration cannot create an abandoned coroutine. The timeout context owns cancellation associated with its deadline and exposes TimeoutError outside that context after unwinding. The blocked fixture waits on a local Event and records closed in finally; the caller checks that marker when it observes timeout. No assertion depends on exactly twenty milliseconds having elapsed. A fast operation returns seven unchanged. Ordinary ValueError from the operation and caller-requested CancelledError must keep their original categories. Catching all failures and returning zero would conflate success, malformed data, and cancellation. A cooperative timeout cannot stop an event loop blocked in synchronous work, and this example does not claim to interrupt threads or remote operations. The timeout belongs around awaited work under an explicit local owner.

## Exercise 4: Make cancellation cleanup observable

**Inputs:** Two Events in the running loop and an observation list. The ready signal lets a controller know acquisition has happened.

**Expected:** Append acquired, set ready, then await release and return released. Append closed in finally on success or cancellation; allow CancelledError to propagate. The controller owns the created task and must await it after cancelling. Do not use sleeps to guess whether acquisition occurred.

**Verify:** Wait for ready, cancel the task, await it, and require CancelledError with events ["acquired", "closed"]. With release already set, the result is released and the same balanced event list appears.

cancellable_wait puts acquisition, readiness, waiting, and cleanup in a visible sequence. The ready Event is set only after acquired has been recorded, so a controller that awaits ready knows cancellation will target a task that entered the resource region. The controller then requests cancellation and awaits the task; only after that await can it assert closed. The implementation uses finally without catching the control signal, allowing TaskGroup or another owner to observe the cancellation accurately. A second fixture begins with release already set, exercising successful completion through the same cleanup region. Both routes produce acquired and closed, but one returns released while the other raises CancelledError. Observing only the event list would miss that difference. Sleeps are unnecessary for coordination and would make the test sensitive to machine scheduling.

## Exercise 5: Inspect every grouped failure

**Inputs:** An ExceptionGroup, possibly containing nested ExceptionGroups and ValueError subclasses alongside other ordinary Exceptions.

**Expected:** Return (value_error_messages, other_messages), traversing leaves depth first in their original order within each category. Classify using isinstance(error, ValueError); preserve each leaf message, including duplicates. Do not flatten by stringifying group summary text or classify BaseException control signals as ordinary failures.

**Verify:** A nested group containing ValueError("bad"), RuntimeError("disk"), and ValueError("bad") gives (("bad", "bad"), ("disk",)). An all-other group gives an empty first tuple.

The failure inspector walks nested ExceptionGroup objects recursively and classifies only leaves. It preserves traversal order within each output category and retains duplicate messages because equal text can come from distinct failures. isinstance recognizes ValueError subclasses as intended. Stringifying the outer group would only produce a summary and lose the individual evidence. The nested fixture contains bad, disk, and another bad, so the result must have two bad entries and one disk entry. A group of only TypeError produces an empty first category. The accepted type is an ordinary ExceptionGroup, which cannot contain BaseException control signals such as CancelledError. A broader BaseExceptionGroup API would need an explicit cancellation policy and is outside this task. An except-star handler can be useful for acting on matched subgroups, but this function reports them without claiming to recover.

## Exercise 6: Restore task-local request context

**Inputs:** A nonempty string request label and an async operation. Use the module ContextVar REQUEST_ID with default outside.

**Expected:** Set REQUEST_ID for the operation, return its result, and reset the exact token in finally on success, ordinary failure, or caller cancellation. Child tasks inherit a copy of the current context. Concurrent requests must not overwrite each other; invalid labels raise ValueError before invoking the operation.

**Verify:** Concurrent request labels north and south each remain visible across an await and in their own child task. The calling context is outside afterward. Repeat with an injected ValueError and cancellation and inspect restoration in the same task.

scoped_request stores the token returned by REQUEST_ID.set and resets that token in finally. Resetting to a hardcoded outside string would fail when nested inside a context whose previous label was already meaningful. Concurrent tasks inherit separate contexts, so north and south can yield and each still observe its own label. A child task sees the context copied at creation; later changes in its parent do not become a shared mutable global binding. The reference checks context before and after an await and inside a child, then verifies outside in the caller. Failure and cancellation are tested separately, with restoration inspected in the same task that entered the scope. Looking only at the controller's context after cancelling another task would be insufficient because those contexts were already separate. Invalid labels fail before the operation factory runs.

The following compact check runs in the executable reference namespace after its function definitions:

```python
errors = ExceptionGroup("batch", [ValueError("bad"), RuntimeError("disk")])
assert describe_failures(errors) == (("bad",), ("disk",))
```

Run the complete reference from fresh process state when comparing results. A change to an input policy must be deliberate and reflected in its assertions; merely suppressing an exception or deleting a cleanup check does not satisfy the original contract.
