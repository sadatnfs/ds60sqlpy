# swift-038: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-038_solution.swift](swift-038_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Compose report sections:** The builder supplies the combining mechanism; the block supplies domain content. Two expressions become an ordered array of sections.

**Include a conditional section:** The buildOptional method gives the conditional branch an explicit combination rule. The conditional contributes its section when true.

## Reason through the six tasks

1. **Predict and explain.** Translate the first block into its builder calls.

2. **Guided modification.** Set include to false and predict the result.

3. **Independent construction.** Build a small report declaration using the existing builder.

4. **Diagnose a defect.** Diagnose a loop in a builder that lacks buildArray support.

5. **Boundary evidence.** Test an empty block and a false optional section.

6. **Transfer and justify.** Explain why a domain-specific builder may be clearer or less clear than an ordinary array literal.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A result builder transforms a restricted-looking block of expressions into calls that combine intermediate results. SwiftUI uses this language feature to express view composition, but the feature itself is part of Swift and can be taught without Apple frameworks. Declarative syntax still has ordinary type and control-flow rules underneath.

Build only the operations the small language needs. Supporting conditionals, loops and optionals requires corresponding builder methods. A result builder should make a domain clearer rather than obscure evaluation or failure. The portable fixture constructs a list of report sections, while the later app project uses SwiftUI's own ViewBuilder.

`@resultBuilder` marks the builder. buildBlock combines expressions and buildOptional handles an if without else. A function parameter annotated with the builder accepts the transformed closure.

A result builder is not runtime reflection or arbitrary syntax parsing. Type errors can surface inside generated combinations, so reduce the block to a small failing expression. Do not reinvent SwiftUI ViewBuilder for ordinary views.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
