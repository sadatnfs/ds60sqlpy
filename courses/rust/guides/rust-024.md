# rust-024: Tests, assertions and useful counterexamples

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `rust-023`

## Learning objectives

Write table-driven tests whose counterexamples reject plausible wrong implementations. The central exercise is task 3: Write table-driven checks for a quantity validator.

## Purpose and mental model

A test is strong when a plausible wrong implementation fails it. Derive expected results from the contract rather than copying the same formula into the assertion. Normal, boundary and invalid cases expose different assumptions. Properties such as idempotence can cover a wider relationship but do not replace concrete expected values.

Rust's built-in test harness runs functions marked test when compiling a test target. The classroom ordinary reference instead invokes always-active assertions through main. This keeps code execution distinct from a Cargo test workflow. A clean unit test does not prove filesystem configuration, network availability or deployment correctness.

## Vocabulary and concepts

**Test oracle:** An independent rule deciding whether behavior is correct.

**Regression case:** A fixture preserving a previously observed defect.

**Property:** A relationship expected across a family of values.

## How to run this lesson

This lesson's programs need only the prelude and their own helpers. A passing run prints `rust-024: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

assert and assert_eq remain active in ordinary builds, unlike debug_assert. A cfg(test) module belongs to a test compilation. Cargo test discovers unit, integration and documentation tests under their own contracts.

**Reading Example A (Use independent expected cases, code below).** `let cases = [(-2, 0), (0, 0), (3, 3)];` is an array of tuples, each pairing an input with an expected output written by hand. The `for` loop destructures each tuple into `input` and `expected` with the pattern `(input, expected)`. `input.max(0)` is the implementation under test: `Ord::max` returns the larger of two values, so it clamps negatives to zero. Each expected value is a literal that does not depend on `max`, which is what makes the check independent. When an assertion fails inside a loop, `assert_eq!` prints the left and right values but not the loop variable, so the message alone does not identify the case; a third argument such as `"input {input}"` adds it.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Use independent expected cases

Literal expectations make the test independent of the implementation expression.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let cases = [(-2, 0), (0, 0), (3, 3)];
        for (input, expected) in cases {
            assert_eq!(input.max(0), expected);
        }
    }
    println!("rust-024: passed");
    Ok(())
}
```

**Observe:** Negative, zero and positive cases satisfy the stated clamp rule.

### Example B: Reject a plausible wrong boundary

The property alone would not necessarily distinguish every wrong constant implementation.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let wrong = |value: i32| if value <= 0 { 1 } else { value };
        assert_ne!(wrong(0), 0);
        assert_eq!((-4_i32).max(0).max(0), (-4_i32).max(0));
    }
    println!("rust-024: passed");
    Ok(())
}
```

**Observe:** Zero rejects the incorrect default while idempotence adds a second property.

## Exercises

1. **Predict and explain.** Name a wrong implementation each case catches.

2. **Guided modification.** Add an extreme integer input without negating its minimum value.

3. **Independent construction.** Write table-driven checks for a quantity validator.

4. **Diagnose a defect.** Diagnose an assertion comparing a function call with itself.

5. **Boundary evidence.** Test idempotence alongside independent boundary expectations.

6. **Transfer and justify.** Separate unit, integration, compile-fail and runtime evidence for a library change.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

A disabled debug_assert is not a release invariant. Random cases require reproducibility and an oracle. A test that catches and ignores its own failure is misleading.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Use independent expected cases) before changing anything, and confirm its observation: Negative, zero and positive cases satisfy the stated clamp rule.
2. Compare Example B (Reject a plausible wrong boundary) with Example A and name the first line whose behavior differs. Its observation is: Zero rejects the incorrect default while idempotence adds a second property.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: A disabled debug_assert is not a release invariant.

Tempting approaches to rule out before you compare:

- **Task 1.** Claiming `(3, 3)` catches `abs` is wrong: `3_i32.abs()` is 3. Only the negative row separates `abs` from the clamp, so removing it would let that bug through.
- **Task 2.** Writing an expectation such as `-i32::MIN`, or calling `i32::MIN.abs()`, overflows because 2147483648 does not fit in an `i32`. The constant form is rejected at compile time by the deny-by-default arithmetic overflow lint, and `abs` panics with attempt to negate with overflow when checks are on.
- **Task 3.** Writing the range as `(0..1000).contains(&value)` excludes 1000, because `..` is half-open. The `(1000, true)` row then panics with `left: false`, `right: true` and the message `input 1000`.
- **Task 5.** Relying on idempotence alone passes for the identity `|value| value` and for the constant `|_| 0`, since both return the same result when applied twice. Neither is a clamp.
- **Task 6.** Treating a green `cargo test` as proof the binary reads the right file is wrong here: the unit and integration tests pass slices of strings and never open the configured path.

## Self-check and next step

For the clamp rule `value.max(0)`, why does Example A test -2, 0 and 3 rather than three positive numbers? Which input exposes Example B's plausible wrong closure, and why would a suite of only negative and positive cases pass it? What does the second property, clamping twice equals clamping once, catch that a table of cases might miss?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [The Rust Book, 11.1 How to Write Tests](https://doc.rust-lang.org/book/ch11-01-writing-tests.html) for what `assert_eq!` and `assert_ne!` print when a case fails.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-024: Tests, assertions and useful counterexamples.
Read courses/rust/guides/rust-024.md and courses/rust/lessons/rust-024.rs. Prerequisites: rust-023.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-024_solution.rs and
courses/rust/solutions/rust-024_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
