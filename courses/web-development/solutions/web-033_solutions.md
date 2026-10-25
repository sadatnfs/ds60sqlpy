# web-033: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

An expression produces a value. Arithmetic operators combine numbers, concatenation joins strings, and logical operators combine conditions. Parentheses make intended grouping clear when an expression mixes operations. Do not assume that familiar-looking operators have the same precedence in every language or version. A readable intermediate variable is often safer than a dense one-line formula.

Many decimal fractions cannot be represented exactly by binary floating point. For a small money example, represent amounts as integer cents and define rounding when converting from external decimal text. This avoids accidentally treating a display string as a precise numeric representation. Integer arithmetic still has limits: values outside the supported range need a different numeric representation or library.

Compute subtotal cents as unit cents times quantity, then add a fixed fee. Validate quantity before multiplication. Use intdiv for deliberate integer division and the remainder operator for the remaining cents. This lesson does not accept arbitrary decimal currency strings; that parser would need explicit scale, sign, range and rounding rules.

## Exercise 1: Predict 125 cents times three units.

The result is 375 cents.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Add a fixed 50-cent fee with a named intermediate value.

The new total is 425 cents and the unit remains explicit.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Implement a bounded quantity calculation and cents formatter.

Valid quantities produce exact integer totals and two-digit fractional display.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose a concatenation expression that hides arithmetic grouping.

Use parentheses or intermediate variables to express the intended computation.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Reject a negative quantity and test zero.

Invalid negative input is rejected; zero follows the declared contract.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain when integer cents are insufficient.

Different currency scales, huge ranges, exchange rates or fractional-unit pricing require an explicit broader numeric policy.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
