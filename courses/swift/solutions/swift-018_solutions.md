# swift-018: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-018_solution.swift](swift-018_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Reuse an ordering mechanism:** The Comparable requirement makes ordering available without dynamic casts. One implementation preserves Int and String results.

**Preserve container element type:** The relationship is encoded in the type rather than a runtime convention. Swapping retains the same concrete element type.

## Task answers

### Task 1: Predict and explain

Identify inferred generic types at every call.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
let number = larger(3, 8)
let word = larger("apple", "pear")
let pair = Pair(first: "left", second: "right")
precondition(type(of: number) == Int.self)
precondition(type(of: word) == String.self)
precondition(type(of: pair) == Pair<String>.self)
```

**Observe:** T is inferred as Int for larger(3, 8), String for the words, and the pair is a Pair<String>.

The compiler infers T from the arguments at each call, so no annotation is needed and the result keeps that concrete type.

### Task 2: Guided modification

Use larger with Double values and a tie.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
precondition(larger(2.5, 1.5) == 2.5)
let tie = larger(2.0, 2.0)
precondition(tie == 2.0 && type(of: tie) == Double.self)
```

**Observe:** larger picks 2.5 from the Double pair, and the tie 2.0, 2.0 returns 2.0 as a Double.

Double conforms to Comparable, so the same generic body is reused with T = Double; a numeric tie returns an equal value either way.

### Task 3: Independent construction

Create a generic immutable triple with a rotation operation.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
struct Triple<T> {
  let first: T
  let second: T
  let third: T
  func rotated() -> Triple<T> { Triple(first: second, second: third, third: first) }
}
let rotated = Triple(first: 1, second: 2, third: 3).rotated()
precondition(rotated.first == 2 && rotated.second == 3 && rotated.third == 1)
```

**Observe:** Rotating (1, 2, 3) gives (2, 3, 1).

The properties are let constants, so rotation returns a new triple instead of changing the original.

### Task 4: Diagnose a defect

Diagnose calling an unavailable method on an unconstrained T.

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
func describe<T: CustomStringConvertible>(_ value: T) -> String {
  "value: \(value.description)"
}
precondition(describe(7) == "value: 7")
precondition(describe("pear") == "value: pear")
```

**Observe:** Constraining T to CustomStringConvertible lets describe produce value: 7 and value: pear.

Without the constraint, swiftc rejects value.description with value of type 'T' has no member 'description', because an unconstrained T promises no members. The constraint states the capability the body uses.

### Task 5: Boundary evidence

State tie behavior and test equal inputs.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
struct Ranked: Comparable {
  let rank: Int
  let tag: String
  static func < (left: Ranked, right: Ranked) -> Bool { left.rank < right.rank }
  static func == (left: Ranked, right: Ranked) -> Bool { left.rank == right.rank }
}
let winner = larger(Ranked(rank: 1, tag: "left"), Ranked(rank: 1, tag: "right"))
precondition(winner.tag == "left")
```

**Observe:** With equal ranks, larger returns the value tagged left.

left >= right is true on a tie, so larger documents and returns its first argument; the tag reveals that choice when equal values are distinguishable.

### Task 6: Transfer and justify

Choose generic or existential abstraction for an API that must preserve concrete result type.

No single reference answer exists: several designs can satisfy this transfer task. Build yours from the task 3 answer above (Create a generic immutable triple with a rotation operation) and the mechanism described below, and state one limitation of your choice.

## Solution reasoning

**Approach.** The generic function `larger<T: Comparable>` returns the greater of two values of one type, and `Pair<T>` stores two values of the same type with a `swapped()` method that returns another `Pair<T>`. Example A calls `larger` with Ints and with Strings; Example B swaps a pair of Strings. The task 3 answer builds a generic triple with rotation.

**Why it is correct.** The `Comparable` constraint gives `>=` to `T`, so `larger(3, 8)` returns 8 and `larger("apple", "pear")` returns pear because p sorts after a. Because `swapped()` returns `Pair<T>`, the compiler knows the result still holds Strings, so `swapped.first == "right"` needs no cast. Rotating `(1, 2, 3)` gives `(2, 3, 1)`.

**A plausible wrong approach.** Dropping the constraint and writing `func larger<T>(_ left: T, _ right: T) -> T { left >= right ? left : right }` fails to compile, because an unconstrained `T` has no `>=`. Using `Any` instead of a generic compiles but forces casts at every call site and loses the guarantee that both inputs and the result share a type.

**How to verify.** For task 5, `larger(4, 4)` returns the left argument because the comparison uses `>=`; check identity with a struct that carries a tag. Try `larger(3, "x")` in a scratch pad and read the compile error naming the conflicting types.

## Mechanism and diagnostic reasoning

Generics preserve type relationships across an algorithm or container. A generic pair stores two values of the same chosen type. The compiler rejects mixing unrelated types unless the API explicitly models that possibility. This is stronger and clearer than storing Any and casting later.

Constraints expose the capabilities an algorithm needs. Comparable permits ordering, while Equatable permits equality. Use the narrowest useful constraint and state behavior for ties and empty inputs. Generic abstraction is valuable when it removes duplicated mechanisms without erasing domain meaning.

`func larger<T: Comparable>` introduces a constrained type parameter. The return type T preserves the input relationship. Generic structs use the same parameter syntax.

Any discards useful type information. Excessively broad constraints make reuse harder. A generic algorithm still needs domain-specific failure and ordering policies.

## Review before continuing

Run the reference and confirm that it prints `swift-018: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
