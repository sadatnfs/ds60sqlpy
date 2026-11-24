# swift-017: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-017_solution.swift](swift-017_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Use a capability:** The interface preserves units and result meaning while hiding representation. The consumer calls the pricing capability without needing its storage details.

**Substitute another policy:** Substitution allows variation within the documented contract, not arbitrary semantic disagreement. Two conforming policies produce different valid prices.

## Task answers

### Task 1: Predict and explain

Trace the protocol call to each concrete implementation.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
let prices: [any Pricer] = [FlatPrice(unit: 3), CappedPrice(unit: 3, cap: 10)]
precondition(type(of: prices[0]) == FlatPrice.self)
precondition(type(of: prices[1]) == CappedPrice.self)
precondition(prices[0].cost(units: 4) == 3 * 4)
precondition(prices[1].cost(units: 4) == min(3 * 4, 10))
```

**Observe:** The first element is a FlatPrice that returns 12, and the second is a CappedPrice that returns min(12, 10) = 10.

The call cost(units:) is written once against any Pricer; at run time it dispatches to the conforming type stored in each box, so the same line reaches FlatPrice.cost and then CappedPrice.cost.

### Task 2: Guided modification

Add a second flat price without changing the consumer.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
func totals(_ prices: [any Pricer], units: Int) -> [Int] {
  prices.map { $0.cost(units: units) }
}
let prices: [any Pricer] = [FlatPrice(unit: 3), CappedPrice(unit: 3, cap: 10), FlatPrice(unit: 5)]
precondition(totals(prices, units: 4) == [12, 10, 20])
```

**Observe:** Adding FlatPrice(unit: 5) yields a third total of 20 while the first two stay 12 and 10.

totals depends only on the Pricer requirement, so a new conforming value is accepted without editing the consumer.

### Task 3: Independent construction

Define a protocol for a deterministic label formatter.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
let formatter: any LabelFormatter = PluralFormatter()
precondition(formatter.label(for: 1) == "1 item")
precondition(formatter.label(for: 3) == "3 items")
precondition(formatter.label(for: 3) == formatter.label(for: 3))
```

**Observe:** The formatter produces 1 item and 3 items, identically on every call.

The protocol states the contract and the conforming type depends only on its input, so its labels are deterministic.

### Task 4: Diagnose a defect

Diagnose two conformers using incompatible units.

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
struct DollarPrice: Pricer {
  let dollars: Int
  func cost(units: Int) -> Int { dollars * units }
}
let cents: any Pricer = FlatPrice(unit: 300)
let dollars: any Pricer = DollarPrice(dollars: 3)
precondition(cents.cost(units: 2) == 600 && dollars.cost(units: 2) == 6)
let fixed: any Pricer = FlatPrice(unit: 3 * 100)
precondition(fixed.cost(units: 2) == cents.cost(units: 2))
```

**Observe:** For the same price, one conformer returns 600 (cents) and the other 6 (dollars); converting before conforming makes them agree.

Both types satisfy the signature, so the compiler accepts them, but the protocol never stated the unit. The fix is a documented contract (cost is in cents) that every conformer honors.

### Task 5: Boundary evidence

Test zero units and the exact cap.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
let capped = CappedPrice(unit: 3, cap: 12)
precondition(capped.cost(units: 0) == 0)
precondition(capped.cost(units: 4) == 12)
precondition(capped.cost(units: 5) == 12)
precondition(FlatPrice(unit: 3).cost(units: 0) == 0)
```

**Observe:** Zero units cost 0 for both policies, 4 units hit the cap of 12 exactly, and 5 units stay capped at 12.

min(unit * units, cap) returns the product at the boundary where the two are equal, so the exact-cap case and the zero case both behave like the flat price.

### Task 6: Transfer and justify

Choose a dependency worth abstracting in the importer and explain why a protocol helps.

No single reference answer exists: several designs can satisfy this transfer task. Build yours from the task 3 answer above (Define a protocol for a deterministic label formatter) and the mechanism described below, and state one limitation of your choice.

## Solution reasoning

**Approach.** The `Pricer` protocol declares one requirement, `cost(units:)`, and two structs conform to it: `FlatPrice` multiplies, and `CappedPrice` multiplies then applies `min` with a cap. Example A calls the capability through `any Pricer`; Example B maps an array of both conformers over 4 units. The task 3 answer defines a deterministic label formatter protocol.

**Why it is correct.** Both conformers agree on the contract that units are a count and the result is a price in the same currency unit. Flat pricing gives 3 times 4, which is 12. The capped policy computes 12 and then takes `min(12, 10)`, giving 10. The consumer sees `[12, 10]` without knowing either struct's stored fields. The task 3 formatter produces 1 item and 3 items on every call.

**A plausible wrong approach.** A second conformer that interprets `units` as grams, or returns cents instead of whole units, still satisfies the compiler because the signature matches. The consumer would then add incompatible numbers. Task 4 is about exactly this: protocols check shape, not meaning, so the meaning must be documented and tested.

**How to verify.** For task 5, compute `CappedPrice(unit: 3, cap: 12).cost(units: 4)` and confirm the exact cap returns 12, and confirm zero units returns 0 for both policies. Add a third flat price to the array without touching the `map` call.

## Mechanism and diagnostic reasoning

A protocol declares capabilities that a conforming type must supply. It lets a consumer depend on a behavior rather than one storage representation. Both structs and classes can conform, which separates the choice of value or reference semantics from the public capability.

A conforming type must preserve the behavioral contract, not just compile with the right method names. Specify units, invalid inputs and mutation. Protocol extensions can share default behavior, but dispatch differences matter when a method is not a protocol requirement. Begin with explicit requirements and test the consumer with distinct implementations.

`protocol Pricer` declares a required method. A type lists conformance after a colon. `any Pricer` is an existential container that can hold differing conforming concrete types behind the protocol interface.

A protocol is not automatically a good abstraction for every type. Default extension methods not declared as requirements can have surprising static dispatch. Preserve behavior and error semantics across conformers.

## Review before continuing

Run the reference and confirm that it prints `swift-017: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
