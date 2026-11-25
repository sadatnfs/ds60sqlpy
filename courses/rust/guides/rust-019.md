# rust-019: Lifetime parameters and borrowed API design

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `rust-018`

## Learning objectives

Design borrowed APIs with the narrowest lifetime relationships the compiler can check. The central exercise is task 3: Write a borrowed prefix parser with the narrowest lifetime relationship.

## Purpose and mental model

A lifetime parameter expresses a relationship between references. It does not allocate storage or extend an owner's life. A function returning one of two borrowed inputs must describe that the output is valid only where both candidate input borrows are valid. The caller and compiler then check actual uses against that relationship.

Prefer simple ownership first. Lifetime annotations become useful when an API deliberately returns views or stores borrowed data. Returning an owned value can simplify a boundary when independent lifetime is required, at an explicit copying cost. Do not force static lifetime onto data merely to suppress a diagnostic.

## Vocabulary and concepts

**Lifetime parameter:** A name for a reference-validity relationship.

**Elision:** Compiler rules inferring common lifetime relationships.

**Borrowed result:** A result whose storage remains owned by another value.

## How to run this lesson

This lesson's programs need only the prelude and their own helpers. A passing run prints `rust-019: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

`fn choose<'a>(left: &'a str, right: &'a str) -> &'a str` relates the output borrow to both inputs. Elision handles common simple cases automatically. A struct field containing a reference also needs its lifetime relationship.

**Reading Example A (Return one input view, code below).** `fn longer<'a>(left: &'a str, right: &'a str) -> &'a str` introduces one lifetime parameter, `'a`, and attaches it to both inputs and the output. The annotation does not change how long anything lives. It states a relationship the compiler checks at every call: the returned reference is valid only while both arguments are still valid. At the call in Example A, `&left` and `&right` borrow two owned `String` values and coerce to `&str`. The compiler picks `'a` as the region where both borrows are live, so the result may be used until either owner ends. The body only compares byte lengths and returns one of its inputs unchanged; it never creates new text, which is why a borrowed return type is possible here at all.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Return one input view

The annotation prevents a caller from using the view after a required owner is gone.

```rust
fn longer<'a>(left: &'a str, right: &'a str) -> &'a str {
    if left.len() >= right.len() {
        left
    } else {
        right
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let left = String::from("pear");
        let right = String::from("watermelon");
        assert_eq!(longer(&left, &right), "watermelon");
    }
    println!("rust-019: passed");
    Ok(())
}
```

**Observe:** The output is a borrowed view of the longer input.

### Example B: Own a result when lifetime must separate

A deliberate owned copy changes the lifetime contract rather than pretending the borrow is static.

```rust
fn longer<'a>(left: &'a str, right: &'a str) -> &'a str {
    if left.len() >= right.len() {
        left
    } else {
        right
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let result = {
            let temporary = String::from("retained");
            temporary.to_owned()
        };
        assert_eq!(result, "retained");
    }
    println!("rust-019: passed");
    Ok(())
}
```

**Observe:** The independent owned result survives the temporary scope.

## Exercises

1. **Predict and explain.** Draw the valid-use regions of both inputs and the output.

2. **Guided modification.** Test the tie policy of longer.

3. **Independent construction.** Write a borrowed prefix parser with the narrowest lifetime relationship.

4. **Diagnose a defect.** Try returning a local reference and explain why annotations cannot make it valid.

5. **Boundary evidence.** Test empty inputs and use after one candidate owner leaves scope.

6. **Transfer and justify.** Choose a borrowed or owned result for a cache boundary and justify cost and lifetime.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

Lifetime names describe relationships, not durations in seconds. Static is not a universal fix. A lifetime annotation cannot rescue a reference to destroyed local storage.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Return one input view) before changing anything, and confirm its observation: The output is a borrowed view of the longer input.
2. Compare Example B (Own a result when lifetime must separate) with Example A and name the first line whose behavior differs. Its observation is: The independent owned result survives the temporary scope.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Lifetime names describe relationships, not durations in seconds.

Tempting approaches to rule out before you compare:

- **Task 1.** Drawing the output region as the whole region of `right` because the longer string happens to be `right` ignores that the signature cannot know which input is returned.
- **Task 2.** Testing with `longer("pear", "pear")` and `assert_eq!` passes whichever argument is returned, so it says nothing about the policy.
- **Task 5.** Assuming the borrow checker sees at run time that `outer` won and allows the view to escape treats lifetimes as a dynamic property. They are decided from the signature alone.

## Self-check and next step

Why does `longer` need one named lifetime tying both inputs to its result, when a one-input function gets its lifetime by elision? What stops a caller from dropping `right` while the view returned by `longer(&left, &right)` is still in use? Why does Example B return an owned `String` so that "retained" survives the inner scope?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [The Rust Book, 10.3 Lifetimes](https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html) for the three elision rules.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-019: Lifetime parameters and borrowed API design.
Read courses/rust/guides/rust-019.md and courses/rust/lessons/rust-019.rs. Prerequisites: rust-018.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-019_solution.rs and
courses/rust/solutions/rust-019_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
