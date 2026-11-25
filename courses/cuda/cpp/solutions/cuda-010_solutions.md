# cuda-010: explanatory solutions

## Mechanism review

RAII connects resource lifetime to an owning C++ object's lifetime. Its constructor establishes an invariant, and its destructor releases the resource. Copying a unique owner is usually forbidden; moving transfers ownership and leaves the source empty. This is important for CUDA allocations, streams and events because a copied raw handle does not represent an independent resource. A destructor should not throw during stack unwinding. Error reporting for explicit completion and release should happen in a deliberate path, while final cleanup remains a last safeguard. Asynchronous use adds a further obligation: do not destroy the owner while a queued operation still borrows the resource.

## Exercise 1

An operation acquires buffer A, then fails to acquire B. If A already belongs to an automatic owner, stack unwinding releases A. The event trace is acquire-A, acquire-B-failed, release-A. If A is only a raw pointer and cleanup exists only at the normal return, the failure path leaks A.

**Approach:** Trace the events: A is acquired, B fails, unwinding runs A's cleanup.

**Why it is correct:** An automatic owner's destructor runs during unwinding, so release does not depend on the normal return path.

**A plausible wrong approach:** Freeing A only at the end of the function skips that line when B throws, leaking A.

**How to verify:** The reference asserts events == ['acquire-A', 'acquire-B-failed', 'release-A'].

## Exercise 2

Moving owner A into owner B changes who releases the allocation. The moved-from A stores an empty handle; only B releases the original resource. A default copy that leaves two nonempty owners would lead to two releases. Neither a destructor nor a smart-sounding class name alone proves this invariant.

**Approach:** Move A into B, record that A now holds an empty handle, and release only through B.

**Why it is correct:** Moving transfers the single ownership, so exactly one release happens for one allocation.

**A plausible wrong approach:** A default member-wise copy duplicates the raw handle, and both destructors free the same memory.

**How to verify:** Delete the copy constructor and verify a copy attempt fails to compile while a move succeeds.

## Exercise 3

Each live nonempty allocation has exactly one owner; borrowers never release it, moves empty the source, and destruction happens after outstanding uses finish.

**Approach:** State one owner per allocation, borrower restrictions, move semantics and completion ordering.

**Why it is correct:** These rules together prevent leaks, double frees and freeing memory a kernel still reads.

**A plausible wrong approach:** Writing only 'the destructor frees memory' omits moves and outstanding GPU work.

**How to verify:** Check each rule against the move and two-stream scenarios in later exercises.

## Exercise 4

An exception during unwinding can terminate the process. Keep destructor cleanup nonthrowing and report operational failures through an explicit checked path.

**Approach:** Make the destructor noexcept and route release failures to a logged status instead of throwing.

**Why it is correct:** A second exception during unwinding calls std::terminate, ending the process before error reporting.

**A plausible wrong approach:** Throwing from the destructor to surface a free failure turns one error into an abort.

**How to verify:** Simulate a failing release in a test and confirm the original allocation error is still reported.

## Exercise 5

Nothing. Represent the empty state distinctly so partial initialization and moved-from objects are safe.

**Approach:** Check for the empty state at the top of release and return without calling the free function.

**Why it is correct:** Moved-from and partially constructed owners hold no allocation, so release must be a no-op.

**A plausible wrong approach:** Calling free on a stale handle in a moved-from owner releases memory now owned by someone else.

**How to verify:** Destroy a moved-from owner in a test and confirm the free counter does not increase.

## Exercise 6

Record both consumers' completion dependencies before freeing or reusing the buffer. Host scope exit alone does not prove GPU completion.

**Approach:** Record completion events from both streams and make release wait on both.

**Why it is correct:** Each stream may still read the buffer after the host leaves scope, so release needs both completions.

**A plausible wrong approach:** Freeing when the host wrapper goes out of scope can release memory a queued kernel still reads.

**How to verify:** Trace a schedule where one stream finishes late and confirm release happens after both events.

## Self-check answers

1. **What should a moved-from device buffer owner hold?** An empty handle, so its destructor releases nothing.
2. **In worked example 1, what releases buffer A when acquiring B fails?** Stack unwinding runs A's owner destructor, giving the trace acquire-A, acquire-B-failed, release-A.
3. **Why should a destructor report errors rather than throw?** Throwing during unwinding from another exception terminates the program.

## Numerical reference and its limits

The [CPU reference](../references/cuda-010_cpu.py) reproduces worked example 1 and prints `['acquire-A', 'acquire-B-failed', 'release-A']`.

## Transfer review

Record both consumers' completion dependencies before freeing or reusing the buffer. Host scope exit alone does not prove GPU completion.
