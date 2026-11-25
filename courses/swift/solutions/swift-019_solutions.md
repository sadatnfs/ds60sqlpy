# swift-019: explanation and comparison

Reference program: [swift-019_solution.swift](swift-019_solution.swift), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Retain a produced type:** The associated type relationship survives through the generic function. The generic consumer knows the produced value is an Int.

**Hide representation with an opaque result:** The function selects one underlying result type while exposing its element relationship. The caller uses sequence behavior without naming the concrete array type.

## Task answers

### Task 1: Predict and explain

Trace the associated Item type through read.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
let produced = read(IntegerSource())
precondition(type(of: produced) == Int.self)
let doubled = produced * 2
precondition(doubled == 14)
```

**Observe:** read returns an Int, so it can be multiplied directly to give 14.

IntegerSource.produce returns Int, which fixes Item = Int; read returns P.Item, so the caller receives Int without any cast.

### Task 2: Guided modification

Add a String-producing conformance.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
struct NameSource: Producer {
  func produce() -> String { "pear" }
}
let name = read(NameSource())
precondition(name.uppercased() == "PEAR")
precondition(read(IntegerSource()) == 7)
```

**Observe:** read on NameSource returns the String pear, while IntegerSource still returns 7.

Each conformance chooses its own Item from the produce return type, and the same generic read preserves whichever type that is.

### Task 3: Independent construction

Write a generic transformation preserving the producer item type.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
func transformed<P: Producer>(_ producer: P, _ change: (P.Item) -> P.Item) -> P.Item {
  change(producer.produce())
}
let value: Int = transformed(IntegerSource()) { $0 + 1 }
precondition(value == 8)
```

**Observe:** Transforming the produced 7 gives 8, still an Int.

The signature uses P.Item for both input and output, so the compiler guarantees the item type is preserved.

### Task 4: Diagnose a defect

Explain why returning unrelated concrete types from one opaque-return function is invalid.

**Written answer.** A function declared -> some Sequence<String> promises one hidden concrete type for every call. Returning an array on one branch and a Set on another makes swiftc report that the return statements do not have matching underlying types. Either convert every branch to the same type (for example Array), or return an existential any Sequence<String> when the caller truly does not need a fixed type.

### Task 5: Boundary evidence

Test empty and nonempty opaque sequences.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
precondition(Array(makeNoLabels()).isEmpty)
var count = 0
for _ in makeLabels() { count += 1 }
precondition(count == 2)
```

**Observe:** The empty opaque sequence produces no elements, and iterating makeLabels counts 2.

Callers use only Sequence behavior, so an empty array and a two-element array both work behind some Sequence<String> without exposing their type.

### Task 6: Transfer and justify

Choose opaque output or existential storage for an API and document the preserved relationships.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Solution reasoning

**Approach.** The `Producer` protocol has an associated type `Item`, `IntegerSource` produces an Int, and the generic `read` function returns `P.Item`. Example A reads a 7 into a variable typed as Int. Example B returns `some Sequence<String>` from `makeLabels`. The task 3 answer transforms the produced value while preserving its type.

**Why it is correct.** When `read(source)` is called, `P` is inferred as `IntegerSource`, so `P.Item` is Int and assigning the result to `let value: Int` compiles without a cast. The opaque return hides the concrete array type but still promises String elements, so `Array(labels)` gives `["a", "b"]`. Adding one to the produced 7 in task 3 gives 8, still an Int.

**A plausible wrong approach.** Writing `makeLabels` so that one branch returns an array and another returns a `Set` fails to compile, because `some` means one hidden type chosen by the function, not any type per return. Storing producers as `[any Producer]` and expecting `read` to return Int loses the associated type relationship.

**How to verify.** Add a `StringSource` conformance returning "seven" for task 2 and confirm `let text: String = read(StringSource())` compiles while `let n: Int = read(StringSource())` does not. Check that an empty opaque sequence materializes as `[]`.

## Mechanism and diagnostic reasoning

An associated type names a type relationship inside a protocol. A producer can declare the type of item it produces without fixing that type for every conformer. A generic consumer retains this relationship. Opaque `some` results hide a concrete implementation while preserving one consistent underlying type selected by the function.

Existential `any` values erase more concrete information and can hold different conforming types. These tools solve different problems. Use generics or opaque types when preserving relationships helps the compiler and consumer; use existentials when heterogeneous storage or runtime substitution is the intended feature. Do not choose based only on which spelling makes an error disappear.

`associatedtype Item` names a conformer-selected type. `P.Item` refers to that relationship in generic code. `some Protocol` hides one concrete return type; `any Protocol` stores an existential value.

Some does not mean any arbitrary type at each return. Existential containers can lose relationships needed by generic operations. Compiler diagnostics often point to a missing type relationship rather than a missing cast.

## Review before continuing

Run the reference and confirm it prints `swift-019: passed`, then rerun the guide's counterexample.
