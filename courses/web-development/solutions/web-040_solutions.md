# web-040: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

A class defines a kind of object, and an object combines state with behavior. Use an object when it makes a domain boundary clearer, not merely because the program has grown. A constructor establishes the initial state. An invariant is a condition that should remain true throughout the object's useful lifetime, such as a nonempty topic and nonnegative duration.

Publicly mutable properties can let callers bypass a carefully checked constructor. A small immutable value object can preserve its contract by validating once and exposing readonly data. Readonly does not make every nested object deeply immutable, and it does not replace validation. Understand the specific language guarantee rather than treating the keyword as a complete architecture.

Constructor property promotion can declare and initialize properties directly in the parameter list. Use explicit types and meaningful names. A method can derive a display label from the stored values without changing them. Prefer composition of small responsibilities over a deep inheritance hierarchy built before requirements are known.

## Exercise 1: Name the invariant enforced by the constructor.

A successfully constructed duration cannot begin with negative minutes.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Add a method that formats the duration.

Formatting derives from state without changing it.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build a validated study-session value object.

Its topic and duration satisfy explicit constructor checks and remain readonly.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose a setter that allows invalid state after construction.

Every mutation boundary must preserve the invariant, or mutation should be removed.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Test an empty topic and zero duration.

The topic is rejected while zero follows the declared nonnegative policy.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain shallow readonly versus deep immutability.

A readonly property cannot be reassigned, but referenced mutable objects can have their own changing state.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
