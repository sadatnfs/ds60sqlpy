# rust-021: Closures and Fn capability bounds

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `rust-020`

## Learning objectives

Write closures and choose Fn, FnMut or FnOnce bounds by what the closure does. The central exercise is task 3: Implement a helper accepting FnMut for repeated transformations.

## Purpose and mental model

A closure captures surrounding values according to what its body needs. It may borrow, mutate captured state or take ownership. Fn, FnMut and FnOnce describe calling capabilities: shared repeatable calls, mutable repeatable calls and at least one consuming call respectively. These traits form a relationship, not three arbitrary spellings to try until compilation succeeds.

A move closure takes ownership of captured values, useful when work outlives the creating scope. Moving a reference still moves only that reference and does not make its borrowed target live forever. Choose capture and call contracts from the intended lifetime and mutation behavior.

## Vocabulary and concepts

**Capture:** A surrounding value or reference retained by a closure.

**FnMut:** A closure capability permitting mutation during repeated calls.

**FnOnce:** A capability allowing a potentially consuming call.

## How to run this lesson

This lesson's programs need only the prelude and their own helpers. A passing run prints `rust-021: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

`|value| value * factor` declares a closure. `move || ...` transfers captures into it. A closure mutating a captured accumulator needs mutable calling access. A function accepting FnOnce can invoke consuming behavior once.

**Reading Example A (Observe mutable capture, code below).** `let mut count = 0;` is the captured variable. The closure `|value| { count += value; }` mentions `count` and modifies it, so the compiler captures it by mutable reference and gives the closure the `FnMut` capability: it may be called many times, but each call needs exclusive access. That is why the closure binding itself is `let mut add`. The parameter `value` has no annotation; the compiler infers `i32` from how the closure uses it and from the two calls. The extra `{ }` around the closure makes the end of its mutable borrow of `count` visible at the closing brace, after which `assert_eq!` may read `count` again. Without that block the code still compiles, because a borrow lasts only until its final use.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Observe mutable capture

The scope makes the exclusive captured access visible.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let mut count = 0;
        {
            let mut add = |value| {
                count += value;
            };
            add(2);
            add(3);
        }
        assert_eq!(count, 5);
    }
    println!("rust-021: passed");
    Ok(())
}
```

**Observe:** The closure updates its borrowed accumulator before the borrow ends.

### Example B: Move owned data into a closure

Returning the owned capture makes this closure consuming rather than indefinitely repeatable.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let text = String::from("owned");
        let consume = move || text;
        let result = consume();
        assert_eq!(result, "owned");
    }
    println!("rust-021: passed");
    Ok(())
}
```

**Observe:** The closure transfers its captured String to the caller once.

## Exercises

1. **Predict and explain.** Identify capture mode and calling capability in each example.

2. **Guided modification.** Write a pure repeatable closure capturing an immutable factor.

3. **Independent construction.** Implement a helper accepting FnMut for repeated transformations.

4. **Diagnose a defect.** Diagnose attempting to call a consuming closure twice.

5. **Boundary evidence.** Test a closure with no captures and one capturing a borrowed reference.

6. **Transfer and justify.** Choose capture ownership for work that will run on another thread.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

Move does not imply deep copy. A moved reference still has a borrowed lifetime. Avoid adding static bounds when the real solution is scoped execution or owned data.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Observe mutable capture) before changing anything, and confirm its observation: The closure updates its borrowed accumulator before the borrow ends.
2. Compare Example B (Move owned data into a closure) with Example A and name the first line whose behavior differs. Its observation is: The closure transfers its captured String to the caller once.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Move does not imply deep copy.

Tempting approaches to rule out before you compare:

- **Task 1.** Crediting the `move` keyword for Example B being `FnOnce` is wrong: `move || text.len()` also owns `text` yet is `Fn`, callable any number of times. Returning `text` is what makes it consuming.
- **Task 2.** Adding a call counter, `calls += 1`, inside the closure makes it `FnMut`. It then needs `let mut scale`, and passing it where `Fn` is required fails with E0525.
- **Task 3.** Dropping `mut` from the parameter `mut step` fails with E0596: calling an `FnMut` needs `&mut step`. Tightening the bound to `impl Fn()` fails too, because the closure assigns to `value`.
- **Task 5.** Calling `drop(name)` before `greet()` assumes `move` gave the closure the `String`. It fails with E0505, cannot move out of `name` because it is borrowed, showing the moved reference still depends on its owner.
- **Task 6.** Calling `std::thread::spawn(|| rows.iter().sum::<i32>())` without `move` fails with E0373: the closure may outlive the function but borrows `rows`. Leaking the vector to obtain a `'static` reference silences it at the cost of never freeing the memory.

## Self-check and next step

In Example A, does the closure capture `count` by shared reference, mutable reference or value, and why can `count` not be read while the closure is still in use? Which of `Fn`, `FnMut` and `FnOnce` does each closure in the lesson implement? Why can Example B's closure, which hands its captured `String` back to the caller, run only once?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [The Rust Book, 13.1 Closures](https://doc.rust-lang.org/book/ch13-01-closures.html) for how captures decide `Fn`, `FnMut` or `FnOnce`.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-021: Closures and Fn capability bounds.
Read courses/rust/guides/rust-021.md and courses/rust/lessons/rust-021.rs. Prerequisites: rust-020.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-021_solution.rs and
courses/rust/solutions/rust-021_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
