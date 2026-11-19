# swift-038: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-038_solution.swift](swift-038_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Compose report sections:** The builder supplies the combining mechanism; the block supplies domain content. Two expressions become an ordered array of sections.

**Include a conditional section:** The buildOptional method gives the conditional branch an explicit combination rule. The conditional contributes its section when true.

## Task answers

### Task 1: Predict and explain

Translate the first block into its builder calls.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The builder supplies the combining mechanism; the block supplies domain content. Two expressions become an ordered array of sections.

### Task 2: Guided modification

Set include to false and predict the result.

No separate reference answer has been written for this task. Start from Example B: The buildOptional method gives the conditional branch an explicit combination rule. The conditional contributes its section when true.

### Task 3: Independent construction

Build a small report declaration using the existing builder.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
let hasWarnings = false
let report = sections {
  "Summary"
  "Totals"
  if hasWarnings { "Warnings" }
}
precondition(report == ["Summary", "Totals"])
```

**Observe:** The report contains Summary and Totals; the Warnings section is omitted.

The builder turns each expression into a section and the if statement into an optional component, so the declaration reads like the report it builds.

### Task 4: Diagnose a defect

Diagnose a loop in a builder that lacks buildArray support.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A result builder is not runtime reflection or arbitrary syntax parsing. Type errors can surface inside generated combinations, so reduce the block to a small failing expression. Do not reinvent SwiftUI ViewBuilder for ordinary views.

### Task 5: Boundary evidence

Test an empty block and a false optional section.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Compose report sections) and Example B (Include a conditional section).

### Task 6: Transfer and justify

Explain why a domain-specific builder may be clearer or less clear than an ordinary array literal.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Result builder**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A result builder transforms a restricted-looking block of expressions into calls that combine intermediate results. SwiftUI uses this language feature to express view composition, but the feature itself is part of Swift and can be taught without Apple frameworks. Declarative syntax still has ordinary type and control-flow rules underneath.

Build only the operations the small language needs. Supporting conditionals, loops and optionals requires corresponding builder methods. A result builder should make a domain clearer rather than obscure evaluation or failure. The portable fixture constructs a list of report sections, while the later app project uses SwiftUI's own ViewBuilder.

`@resultBuilder` marks the builder. buildBlock combines expressions and buildOptional handles an if without else. A function parameter annotated with the builder accepts the transformed closure.

A result builder is not runtime reflection or arbitrary syntax parsing. Type errors can surface inside generated combinations, so reduce the block to a small failing expression. Do not reinvent SwiftUI ViewBuilder for ordinary views.

## Review before continuing

Run the reference and confirm that it prints `swift-038: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
