# web-036: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

A function gives a named operation explicit inputs and an output. A useful contract states accepted values, returned meaning and failure behavior. Type declarations communicate and enforce part of that contract at runtime, but a positive duration requirement needs an explicit value check in addition to an int type. Small pure functions are easy to test because their result depends on inputs rather than hidden global state.

A closure is a function value that can be passed to another function. Arrow functions capture variables from their surrounding scope by value automatically, while ordinary anonymous functions use an explicit use clause for capture. Avoid hidden mutable dependencies when a simple parameter would make the relationship clearer.

Separate formatting from calculation so each can be tested independently. Return values are not the same as echo output. A function that echoes a result may be difficult to compose, while a function that returns a value lets a caller choose how to display it. Use exceptions for invalid inputs when the contract treats them as errors, and document predictable alternate results when absence is normal.

## Exercise 1: Explain the difference between returning and echoing a value.

Returning supplies data to the caller; echo writes output as a side effect.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Add a value-range guard to a typed function.

The function rejects invalid integers even though they satisfy the declared type.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build reusable duration calculation and display functions.

Calculations can be tested without capturing output, then formatted at the boundary.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose a result depending on an undocumented global.

Pass the dependency explicitly or isolate the stateful boundary.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Test zero, a normal value and a negative input.

Each follows the stated contract and the failure is intentional.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain when a closure improves a transformation.

A short callback can express a local operation while keeping its inputs and captured context clear.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
