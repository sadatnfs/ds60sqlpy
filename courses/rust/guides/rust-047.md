# rust-047: Properties, compile-fail cases and regression design

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `rust-046`

## Learning objectives

Design property tests and regression checks that would fail for a broken implementation. The central exercise is task 3: Write a property checking an Arrow filter's output count against its Boolean mask.

## Purpose and mental model

Advanced verification combines examples, properties and boundary-specific evidence. A property such as sorting preserving element multiplicity can expose mistakes that one expected list misses. Compile-fail tests can preserve an API's ownership or visibility restrictions, but they belong to a deliberately prepared test harness rather than an ordinary successful runtime reference.

Fuzzing and property-testing crates are valuable external tools, not hidden dependencies in this pad. Start with deterministic exhaustive enumeration over a small bounded domain and an independent oracle. Keep minimized counterexamples when a failure appears. Never weaken an invariant to accommodate a wrong implementation merely because a large suite is expensive.

## Vocabulary and concepts

**Property test:** A test of a relationship across many inputs.

**Counterexample:** An input disproving a claimed property.

**Compile-fail test:** Evidence that an invalid program is rejected by the intended language contract.

## How to run this lesson

This lesson's programs need only the prelude and their own helpers. A passing run prints `rust-047: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

Nested loops can enumerate a small input space reproducibly. A sorted clone can be compared with the original through a frequency map. Compile diagnostics should be categorized by the violated rule rather than fragile full-message text.

**Reading Example A (Check a bounded algebraic property, code below).** Two nested `for` loops iterate over the range `0_i32..10`, which includes 0 and excludes 10, so `a` and `b` each take ten values and the inner body runs once for every ordered pair. The `_i32` suffix fixes the type, so the property is checked for `i32` addition, not for numbers in general. The assertion compares `a + b` with `b + a` for each pair. `pairs` counts how many times the body actually ran, and the final assertion checks that count. That second check guards the test itself: if a later edit narrowed a range or added an early `break`, the property would still pass on fewer cases, and only the count would reveal it.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Check a bounded algebraic property

The range avoids overflow, making the mathematical property appropriate to this representation.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let mut pairs = 0;
        for a in 0_i32..10 {
            for b in 0_i32..10 {
                assert_eq!(a + b, b + a);
                pairs += 1;
            }
        }
        assert_eq!(pairs, 100);
    }
    println!("rust-047: passed");
    Ok(())
}
```

**Observe:** All one hundred bounded pairs were checked and satisfy the addition relation.

### Example B: Check order and multiplicity separately

Order alone would not reject a broken implementation that drops duplicates.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let original = vec![3, 1, 3, 2];
        let mut sorted = original.clone();
        sorted.sort();
        assert!(sorted.windows(2).all(|pair| pair[0] <= pair[1]));
        for value in 1..=3 {
            assert_eq!(original.iter().filter(|item| **item == value).count(), sorted.iter().filter(|item| **item == value).count());
        }
    }
    println!("rust-047: passed");
    Ok(())
}
```

**Observe:** Sorting establishes order without losing the repeated three.

## Exercises

1. **Predict and explain.** State the assumptions making the bounded arithmetic property valid.

2. **Guided modification.** Add a small exhaustive test for checked quantity addition.

3. **Independent construction.** Write a property checking an Arrow filter's output count against its Boolean mask.

4. **Diagnose a defect.** Diagnose a sortedness test that never checks retained values.

5. **Boundary evidence.** Preserve empty, duplicate and all-null regression fixtures.

6. **Transfer and justify.** Design an external fuzzing and compile-fail plan with reproducible seeds, minimized failures and clear acceptance scope.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

A property can be too weak to distinguish incorrect implementations. Integer overflow can invalidate a mathematical law's assumed domain. Compiler message wording may change even when the underlying rule remains correct.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Check a bounded algebraic property) before changing anything, and confirm its observation: All one hundred bounded pairs were checked and satisfy the addition relation.
2. Compare Example B (Check order and multiplicity separately) with Example A and name the first line whose behavior differs. Its observation is: Sorting establishes order without losing the repeated three.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: A property can be too weak to distinguish incorrect implementations.

Tempting approaches to rule out before you compare:

- **Task 1.** Concluding that addition is commutative for every `i32` from this test generalizes past the domain it enumerated.
- **Task 2.** Testing only small values such as 1 + 2 never reaches the overflow boundary, so an implementation that wraps would pass.
- **Task 5.** Deleting a fixture after its bug is fixed lets the same defect return unnoticed.

## Self-check and next step

Why does Example A count its pairs and assert 100, rather than only asserting commutativity inside the loop? In Example B, why does sortedness alone not prove a correct sort, and which check catches a sort that drops one of the two 3s? When should a counterexample found by a property become a fixed regression case?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [The Rust Book, 11.1 How to Write Tests](https://doc.rust-lang.org/book/ch11-01-writing-tests.html) for test attributes and failure messages.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-047: Properties, compile-fail cases and regression design.
Read courses/rust/guides/rust-047.md and courses/rust/lessons/rust-047.rs. Prerequisites: rust-046.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-047_solution.rs and
courses/rust/solutions/rust-047_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
