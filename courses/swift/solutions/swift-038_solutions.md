# swift-038: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-038_solution.swift](swift-038_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Compose report sections:** The builder supplies the combining mechanism; the block supplies domain content. Two expressions become an ordered array of sections.

**Include a conditional section:** The buildOptional method gives the conditional branch an explicit combination rule. The conditional contributes its section when true.

## Task answers

### Task 1: Predict and explain

Translate the first block into its builder calls.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
let manual = SectionBuilder.buildBlock(
  SectionBuilder.buildExpression("Overview"),
  SectionBuilder.buildExpression("Details"))
let built = sections {
  "Overview"
  "Details"
}
precondition(manual == built && manual == ["Overview", "Details"])
```

**Observe:** Calling buildExpression on each string and passing both to buildBlock gives the same [Overview, Details] as the builder block.

The compiler rewrites each expression statement into buildExpression and combines the results with buildBlock, which flattens the one-element arrays in order.

### Task 2: Guided modification

Set include to false and predict the result.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
let include = false
let report = sections {
  "Overview"
  if include { "Diagnostics" }
}
precondition(report == ["Overview"])
```

**Observe:** With include set to false, the report is just [Overview].

A false if passes nil to buildOptional, which returns an empty array, so the conditional contributes nothing.

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

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
let names = ["North", "South"]
let report = loopingSections {
  "Overview"
  for name in names { "Region \(name)" }
}
precondition(report == ["Overview", "Region North", "Region South"])
```

**Observe:** With buildArray available, the loop contributes Region North and Region South after Overview.

SectionBuilder has no buildArray, so swiftc rejects a for-in loop inside sections; the loop is legal only once the builder says how to combine one result per iteration.

### Task 5: Boundary evidence

Test an empty block and a false optional section.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
let empty = sections {}
precondition(empty.isEmpty)
let show = false
let hidden = sections {
  if show { "Hidden" }
}
precondition(hidden.isEmpty)
```

**Observe:** An empty block and a block with only a false conditional both produce [].

buildBlock with no components flattens to an empty array, and buildOptional(nil) also returns []; neither case needs a special path.

### Task 6: Transfer and justify

Explain why a domain-specific builder may be clearer or less clear than an ordinary array literal.

No single reference answer exists: several designs can satisfy this transfer task. Build yours from the task 3 answer above (Build a small report declaration using the existing builder) and the mechanism described below, and state one limitation of your choice.

## Solution reasoning

**Approach.** `SectionBuilder` is a result builder with three methods: `buildExpression` wraps a String in a one-element array, `buildBlock` flattens the arrays, and `buildOptional` turns a missing `if` branch into an empty array. `sections` applies the builder to a closure. Example A lists two strings; Example B adds an `if include` branch.

**Why it is correct.** The compiler rewrites Example A into roughly `buildBlock(buildExpression("Overview"), buildExpression("Details"))`, which flattens to `["Overview", "Details"]`. In Example B the `if` becomes `buildOptional(include ? buildBlock(buildExpression("Diagnostics")) : nil)`; with `include` true it contributes `["Diagnostics"]`. In task 3 the report contains Summary and Totals, and the Warnings section is omitted because its condition is false.

**A plausible wrong approach.** Writing `for name in names { name }` inside the block is the task 4 defect: without a `buildArray` method the compiler rejects the loop, and the error points inside the generated combination rather than at a missing method. Expecting the builder to accept an `if` with no `buildOptional` would also fail to compile.

**How to verify.** For task 2, set `include` to false and predict `["Overview"]`, since `buildOptional(nil)` returns an empty array. For task 5, an empty closure calls `buildBlock()` with no components and returns `[]`. When a type error appears, cut the block to one line to locate it.

## Mechanism and diagnostic reasoning

A result builder transforms a restricted-looking block of expressions into calls that combine intermediate results. SwiftUI uses this language feature to express view composition, but the feature itself is part of Swift and can be taught without Apple frameworks. Declarative syntax still has ordinary type and control-flow rules underneath.

Build only the operations the small language needs. Supporting conditionals, loops and optionals requires corresponding builder methods. A result builder should make a domain clearer rather than obscure evaluation or failure. The portable fixture constructs a list of report sections, while the later app project uses SwiftUI's own ViewBuilder.

`@resultBuilder` marks the builder. buildBlock combines expressions and buildOptional handles an if without else. A function parameter annotated with the builder accepts the transformed closure.

A result builder is not runtime reflection or arbitrary syntax parsing. Type errors can surface inside generated combinations, so reduce the block to a small failing expression. Do not reinvent SwiftUI ViewBuilder for ordinary views.

## Review before continuing

Run the reference and confirm that it prints `swift-038: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
