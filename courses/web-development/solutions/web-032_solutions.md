# web-032: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

A value has a type that influences allowed operations and comparison behavior. PHP provides integers, floating-point numbers, strings, booleans, arrays, objects and null among its types. Null commonly represents absence, but its meaning belongs to the application's contract. Zero, an empty string and false are different values and should not be casually treated as interchangeable missing data.

Loose comparison can coerce values before comparison; strict comparison checks both type and value. The string '0' and integer 0 may look similar when printed but are different under strict equality. A form normally supplies strings, so validation and explicit conversion are necessary before treating them as trusted numeric data. Strict typing at function boundaries does not validate arbitrary request arrays.

Use `===` and `!==` when type distinctions are part of the contract. `get_debug_type` helps inspect the type. The null-coalescing operator `??` supplies a default for an absent or null value, while `array_key_exists` can distinguish a present null entry from a missing key. Floating-point values approximate many decimal fractions, so financial examples later use integer minor units.

## Exercise 1: Predict strict equality for '0', 0 and false.

Each has a different type, so cross-type strict comparisons are false.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Add a typed diagnostic to a value before converting it.

The output identifies the actual type rather than relying on its printed appearance.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Model an optional note without confusing missing, empty and null.

The program documents and checks the chosen interpretation of each state.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Repair a loose comparison that accepts an unintended type.

Use strict comparison after deliberate validation and conversion.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Test zero as a valid numeric boundary.

Zero is retained when the contract permits it, rather than discarded as generic falsy data.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain the limited scope of strict_types.

It affects relevant scalar call coercions; it does not replace runtime validation or static analysis.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
