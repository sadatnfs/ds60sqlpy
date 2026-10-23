# cpp-029: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A thread executes a function concurrently with its caller. Joining waits for that function to finish before borrowed state is destroyed. Cancellation is a request that cooperative code checks, not a forced kill. C++20 jthread adds joining destruction and stop_token support, while std::thread requires explicit joining on every path.

## Detailed reasoning

Thread startup, cancellation request and completion are separate events. The promise reports startup, the atomic flag requests cancellation and join confirms completion. A fixed delay cannot replace any of these events because scheduling may be slower or faster than expected. A reference capture borrows a local variable, so scope must not end first. jthread adds automatic joining and stop support, but cooperative code still has to inspect its token.

<!-- depth:start -->
## Thread lifetime and cooperative cancellation

Starting a thread creates another flow of execution; it does not wait for that work to finish. A reference capture borrows an object from the creating scope. The owner must keep that object alive until the worker's last access. In the first program, answer belongs to main, the thread writes42, and join completes before main reads the result or ends the scope. The join is part of the correctness argument, not an optional delay.

A thread object that remains joinable at destruction is a serious lifecycle error for std::thread. Every path after successful creation needs an ownership decision: join the work or deliberately transfer its management. Detaching makes lifetime reasoning harder because the creating scope can disappear while the worker still uses borrowed state. The course examples retain and join every worker instead.

Cancellation is a request, not an asynchronous kill. The second example uses a promise/future to establish that the worker reached its startup point, then an atomic flag to request stop. The worker repeatedly observes the flag and exits its loop. join confirms actual completion. A fixed sleep would prove neither startup nor completion and can fail on a slower or more heavily loaded machine.

The memory used for the flag must support concurrent access. A plain bool read and written by different threads without synchronization would introduce a data race. Atomic access makes the flag communication defined. That does not imply every other shared object is safe; each shared value needs its own ownership or synchronization argument.

std::jthread can automate joining and provide a stop token, but cooperative work still has to check the request at useful points. A blocking operation that never returns may prevent timely cancellation. Production design therefore needs bounded I/O, a shutdown deadline and a policy for unresponsive work. The tiny fixture teaches the request/observation/join sequence without pretending to solve arbitrary thread interruption.

## Debugging the contract

If a test occasionally reads0 instead of 42, inspect whether it observes completion before reading shared state. If shutdown hangs, locate the next cancellation check or blocking call rather than adding a longer sleep. If a function exits while a thread borrows its locals, fix the ownership scope. If thread creation can throw after another worker starts, join the already created worker during the failure path before propagating the exception.
<!-- depth:end -->

## Worked example 1

```cpp
int answer=0; std::thread t([&]{answer=42;}); t.join(); assert(answer==42);
```

Expected: After join the result is 42 and the borrowed local is still alive.

## Worked example 2

```cpp
std::atomic<bool> stop{false}; // worker checks stop; owner requests and joins
```

Expected: A stop flag requests cooperation; the owner still waits for termination.

## Exercise 1: Trace lifetimes

Draw result, worker creation, write, join and scope exit.

**Expected:** The owner remains alive until after join.

**Reasoning:** The reference capture borrows local state.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Read after joining

Compute 42 on one worker and read afterward.

**Expected:** 42, with a documented join before access.

**Reasoning:** join establishes completion and synchronization.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Request cancellation

Run the supplied ready handshake then set stop and join.

**Expected:** Worker terminates without a sleep-based timing assumption.

**Reasoning:** The promise proves startup before cancellation.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Repair detach

Review detaching a worker that captures a local by reference.

**Expected:** Reject detached borrow; keep ownership until join.

**Reasoning:** Detached lifetime can outlast the referenced variable.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Translate to jthread

On a qualified C++20 library use jthread and stop_token.

**Expected:** request_stop followed by scope exit joins; record compiler/library support.

**Reasoning:** A stop request only works if the body checks the token.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer failure cleanup

Add an owner-side early return and keep joining mandatory.

**Expected:** No joinable thread reaches destructor; no dangling capture.

**Reasoning:** RAII joining or a scope guard must cover exceptional paths.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
