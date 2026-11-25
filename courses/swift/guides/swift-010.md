# swift-010: Dictionaries, sets and stable hashing

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `swift-009`

## Learning objectives

Use dictionaries and sets for lookup and deduplication and sort them for stable output. The central exercise is task 3: Build a unique sorted list of accepted inventory names.

## Purpose and mental model

A Dictionary associates unique keys with values; a Set stores unique members. Both use Hashable to narrow equality lookup. Equal values must hash consistently. A hash value is not a persistent identifier and should not be saved as an enduring key, since hashing can vary across process runs.

Dictionary lookup returns an optional, preserving the distinction between a missing key and a present zero. Output order is not a business sorting policy. Sort keys explicitly for stable presentation. When designing a custom key, use stable identity fields and avoid changing a key after it has been inserted into hashed storage.

## Vocabulary and concepts

**Hashable:** A type providing equality-compatible hashing.

**Key:** The identity used for lookup.

**Set membership:** Presence of an equivalent element without duplicates.

## How to run this lesson

Dictionary and set iteration order is unspecified, so never print a dictionary directly as evidence; sort first, as Example B does with `sorted()`. Task 4 is a written diagnosis: `hashValue` uses a per-process random seed, so a value stored by one run will not match the next run of the same program.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`[String: Int]` declares a dictionary. `counts[key, default: 0] += 1` inserts a default only for that mutation. Set.insert returns whether an element was newly inserted. sorted establishes presentation order.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Preserve absence and zero

Optional lookup prevents missing information from being confused with a stored value.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let counts = ["pear": 0]
      precondition(counts["pear"] == 0)
      precondition(counts["apple"] == nil)
    }
    print("swift-010: passed")
  }
}
```

**Observe:** Pear is present with zero and apple is absent.

**Trace.** `counts` has one entry, pear mapped to 0. The subscript lookup for pear returns `Int?`, here `Optional(0)`, and the check compares it with 0. The lookup for apple finds no key and returns nil. The two lookups share a type but mean different things: one says the store knows there are zero pears, the other says the store holds no information about apples. Supplying a default of 0 at lookup time would merge those two meanings.

### Example B: Deduplicate and order deliberately

Set semantics establish uniqueness while sorting separately establishes order.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      var tags: Set<String> = ["red"]
      precondition(!tags.insert("red").inserted)
      precondition(tags.insert("blue").inserted)
      precondition(tags.sorted() == ["blue", "red"])
    }
    print("swift-010: passed")
  }
}
```

**Observe:** Duplicate red is not inserted and sorted output is deterministic.

**Trace.** `tags` starts with red. Inserting red again finds an equal element, leaves the set unchanged and returns a tuple whose `inserted` field is false. Inserting blue adds a new element and returns true. The set now holds two strings in an unspecified order, so the final check calls `sorted()`, which returns an `Array` in ascending order: blue, then red. Uniqueness comes from the set; the order comes only from the sort.

## Exercises

1. **Predict and explain.** Explain the optional result of each dictionary lookup.

2. **Guided modification.** Count repeated tags using the default-value subscript.

3. **Independent construction.** Build a unique sorted list of accepted inventory names.

4. **Diagnose a defect.** Diagnose persisting hashValue as a cross-run identifier.

5. **Boundary evidence.** Test missing, present-zero and duplicate keys.

6. **Transfer and justify.** Design a custom Hashable key using only stable identity fields.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Hash collisions do not mean values are equal; equality resolves them. Dictionary order should not be treated as a report contract. A default subscript can insert values during mutation, so inspect side effects.

The default-value subscript in task 2 has a side effect worth pinning: incrementing `counts[key, default: 0]` inserts a missing key, while merely reading it does not. Compare `counts.count` before and after each form to see the difference. Include a missing key, a key present with zero and a duplicate tag in the boundary checks for task 5.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Preserve absence and zero) before changing anything, and confirm its observation: Pear is present with zero and apple is absent.
2. Compare Example B (Deduplicate and order deliberately) with Example A and name the first line whose behavior differs. Its observation is: Duplicate red is not inserted and sorted output is deterministic.
3. Before opening the explanation, check your task 3 attempt (Build a unique sorted list of accepted inventory names) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Explain why two different strings can share a hash value and how a set still keeps them apart. State the type returned by a plain dictionary subscript and by the default-value subscript. List the fields of a customer record you would hash for a key that must stay stable across app launches.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): Sets, set operations and dictionaries appear in the book's Collection Types chapter; the standard library reference documents the Hashable protocol.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-010: Dictionaries, sets and stable hashing.
Read courses/swift/guides/swift-010.md and courses/swift/lessons/swift-010.swift. Prerequisites: swift-009.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-010_solution.swift and
courses/swift/solutions/swift-010_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
