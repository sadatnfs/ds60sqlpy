# cpp-029: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A thread executes a function concurrently with its caller. Joining waits for that function to finish before borrowed state is destroyed. Cancellation is a request that cooperative code checks, not a forced kill. C++20 jthread adds joining destruction and stop_token support, while std::thread requires explicit joining on every path.

## Detailed reasoning

Thread startup, cancellation request and completion are separate events. The promise reports startup, the atomic flag requests cancellation and join confirms completion. A fixed delay cannot replace any of these events because scheduling may be slower or faster than expected. A reference capture borrows a local variable, so scope must not end first. jthread adds automatic joining and stop support, but cooperative code still has to inspect its token.

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
