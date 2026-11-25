# swift-016: Foundation project: an honest inventory importer

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `swift-015`

## Learning objectives

Build an honest inventory importer that reports sorted totals and rejected lines. The central exercise is task 3: Produce a sorted text report with accepted totals and rejected count.

## Purpose and mental model

A first useful Swift project combines optional parsing, value models, loops and deterministic reporting. The critical boundary is admission: malformed or negative quantities must not become accepted zero values. A report should separately account for valid quantities and rejected records.

The fixture uses in-memory lines and produces a value result, so it runs offline and is easy to test. External file loading can be added later as an adapter. Preserve a clear contract for duplicate names and ordering. The same small project will return in later lessons with Codable, async ownership and app presentation.

## Vocabulary and concepts

**Admission:** The decision to accept a record into domain processing.

**Aggregation:** Combining accepted values under shared keys.

**Rejection evidence:** A retained description or count of excluded inputs.

## How to run this lesson

Both examples share `importRows`, declared above `LessonMain`, so copy the whole helper section along with either example. Tasks 1 and 5 require predicting the guard outcome for each input line on paper first. Task 3 produces text output, so print the sorted report and compare it line by line with your prediction.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

Split creates field substrings; convert them deliberately when storing long-lived names. Int parsing returns an optional. Dictionary default mutation accumulates admitted duplicates. sorted fixes presentation order.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Combine repeated valid names

Duplicate names are deliberately accumulated after validation.

```swift
import Foundation

func importRows(_ lines: [String]) -> (counts: [String: Int], rejected: Int) {
  var counts: [String: Int] = [:]
  var rejected = 0
  for line in lines {
    let fields = line.split(separator: ",", omittingEmptySubsequences: false)
    guard fields.count == 2, !fields[0].isEmpty, let quantity = Int(fields[1]), quantity >= 0 else {
      rejected += 1
      continue
    }
    counts[String(fields[0]), default: 0] += quantity
  }
  return (counts, rejected)
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let result = importRows(["pear,2", "apple,3", "pear,4"])
      precondition(result.counts == ["pear": 6, "apple": 3])
      precondition(result.rejected == 0)
    }
    print("swift-016: passed")
  }
}
```

**Observe:** Pear totals 6 and apple totals 3.

**Trace.** For pear,2 the split produces two fields, the name is nonempty and `Int` parses 2, so the guard passes and the default-value subscript stores pear 2. Apple,3 adds a new key with 3. The second pear,4 line passes the same checks and the subscript adds 4 to the existing 2, giving 6. No line fails, so `rejected` stays 0. The dictionary comparison in the check does not depend on insertion order, which is why it is safe to compare against a literal.

### Example B: Keep rejection separate from zero

This result preserves the difference between accepted zero, absence and invalid input.

```swift
import Foundation

func importRows(_ lines: [String]) -> (counts: [String: Int], rejected: Int) {
  var counts: [String: Int] = [:]
  var rejected = 0
  for line in lines {
    let fields = line.split(separator: ",", omittingEmptySubsequences: false)
    guard fields.count == 2, !fields[0].isEmpty, let quantity = Int(fields[1]), quantity >= 0 else {
      rejected += 1
      continue
    }
    counts[String(fields[0]), default: 0] += quantity
  }
  return (counts, rejected)
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let result = importRows(["pear,0", "bad", "apple,-1", "pear,no"])
      precondition(result.counts == ["pear": 0])
      precondition(result.rejected == 3)
      precondition(importRows([]).counts.isEmpty)
    }
    print("swift-016: passed")
  }
}
```

**Observe:** The valid zero remains present while three records are rejected.

**Trace.** Pear,0 passes every check because 0 satisfies `quantity >= 0`, so pear is stored with 0. The line bad splits into one field and fails the field count. Apple,-1 has two fields and parses, but the negative quantity fails the last condition. Pear,no fails because `Int` returns nil. Each failure increments `rejected` and continues, giving 3. Apple never enters the dictionary, so absence and accepted zero stay distinct. An empty input runs the loop zero times.

## Exercises

1. **Predict and explain.** Trace each line through field count, name and quantity checks.

2. **Guided modification.** Add a valid duplicate and predict the new aggregate.

3. **Independent construction.** Produce a sorted text report with accepted totals and rejected count.

4. **Diagnose a defect.** Diagnose replacing failed Int parsing with zero.

5. **Boundary evidence.** Test empty names, extra fields, zero and an empty input list.

6. **Transfer and justify.** Design a reusable result that retains safe line-specific reasons without storing raw sensitive input.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Check field count before indexing. String splitting can omit empty fields unless configured, so this fixture preserves them deliberately. Production totals also need an overflow policy.

Replacing failed parsing with zero, as in task 4, turns pear,no into an accepted pear with quantity 0. The counts still read pear 0, so only the rejected total reveals the bug. The counterexample is Example B's own input: the correct result is pear 0 with three rejections, and the buggy one is pear 0 with two. For task 5, an extra field such as pear,2,x must be rejected because the split produces three fields.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Combine repeated valid names) before changing anything, and confirm its observation: Pear totals 6 and apple totals 3.
2. Compare Example B (Keep rejection separate from zero) with Example A and name the first line whose behavior differs. Its observation is: The valid zero remains present while three records are rejected.
3. Before opening the explanation, check your task 3 attempt (Produce a sorted text report with accepted totals and rejected count) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Explain what `omittingEmptySubsequences: false` changes for an input such as a lone comma. Say why `continue` rather than `return` belongs in the guard's else branch here. Describe how you would record a reason for each rejected line without keeping the raw line, which might contain sensitive data.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): Dictionary subscripts with defaults are covered under Collection Types; the standard library reference documents `split(separator:maxSplits:omittingEmptySubsequences:)`.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-016: Foundation project: an honest inventory importer.
Read courses/swift/guides/swift-016.md and courses/swift/lessons/swift-016.swift. Prerequisites: swift-015.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-016_solution.swift and
courses/swift/solutions/swift-016_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
