# web-034: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

Control flow determines which statements execute and how often. A branch chooses among alternatives, while a loop repeats a body for a sequence or condition. A loop needs a termination argument: a bounded collection, an advancing counter or another condition that is guaranteed to change. The classroom enforces execution limits, but a good program should still have its own understandable bound.

Guard clauses reject invalid conditions before the main computation. They reduce nesting and make accepted input clearer. A match expression compares strictly and returns a value; it differs from a switch statement's traditional loose comparison behavior and fall-through possibilities. Use the construct whose semantics fit the task rather than choosing the shortest spelling.

A foreach loop visits array values and can also expose keys. A for loop makes initialization, condition and update explicit. In a match expression, each arm maps a condition to a result, and a default arm handles other values when that is appropriate. Do not silently map invalid input to a valid default if the contract requires rejection.

## Exercise 1: Trace the accumulator after each iteration.

It progresses through 20, 50 and 65.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Add a guard against negative durations.

Invalid values fail before they enter the total.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build a bounded weekly-duration summary with a route label.

The total and label follow the declared cases and terminate predictably.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose a while loop whose condition never changes.

Identify the missing progress step and replace it with a bounded iteration where possible.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Test an empty collection.

The total is zero without a special invalid array access.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain match versus switch for a typed mapping.

Match returns a value and compares strictly; switch has different comparison and fall-through rules.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
