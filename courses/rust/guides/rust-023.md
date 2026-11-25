# rust-023: Modules, visibility and a stable public surface

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `rust-022`

## Learning objectives

Organize code into modules with a small, stable public surface. The central exercise is task 3: Move a pure domain operation into an inline module.

## Purpose and mental model

Modules organize names and control visibility. A private implementation can change without forcing every consumer to understand it. Public items form a compatibility boundary and should expose domain meaning rather than internal representation. A crate is a compilation unit; a package can contain a library crate and executable crates.

The classroom can demonstrate modules inside one source file. A real multi-file Cargo project has separate preparation and is not uploaded through the pad. Keep that distinction explicit when a lesson introduces src/lib.rs and integration tests. Good module boundaries follow responsibilities and dependency direction, not a fixed rule that every type needs its own file.

## Vocabulary and concepts

**Module:** A namespace and visibility boundary.

**Crate:** A Rust compilation unit.

**Public API:** The surface consumers may depend on.

## How to run this lesson

This lesson's programs need only the prelude and their own helpers. A passing run prints `rust-023: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).

The later [InventoryLab Cargo project](../fixtures/InventoryLab/README.md) supplies actual multi-file source and integration tests outside the single-file pad.

## Syntax anatomy and execution trace

`mod domain { ... }` declares a module. pub exposes an item to permitted external paths. use imports a name into scope without copying its implementation. pub(crate) limits visibility to the current crate.

**Reading Example A (Call a reviewed public function, code below).** `mod domain { ... }` declares a module inline, creating a new namespace. Items in a module are private by default, visible only inside that module and its children. Writing `pub fn double` exports the function to the parent scope, so it can be called through the path `domain::double`. The function's body could change without affecting callers as long as its signature and documented behavior stay the same; that signature is the stable public surface. The two assertions act as consumer tests: they use only the public path and check an ordinary value and the zero edge. Removing `pub` makes both calls fail with E0603, function `double` is private.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Call a reviewed public function

The implementation details remain behind its named boundary.

```rust
mod domain {
    pub fn double(value: i32) -> i32 {
        value * 2
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        assert_eq!(domain::double(4), 8);
        assert_eq!(domain::double(0), 0);
    }
    println!("rust-023: passed");
    Ok(())
}
```

**Observe:** The consumer uses the domain module interface.

### Example B: Import a name without changing ownership

Use changes name resolution, not execution or data ownership.

```rust
mod domain {
    pub fn double(value: i32) -> i32 {
        value * 2
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use domain::double;
        assert_eq!(double(3), 6);
    }
    println!("rust-023: passed");
    Ok(())
}
```

**Observe:** The shorter imported name refers to the same function.

## Exercises

1. **Predict and explain.** Identify the public and private items.

2. **Guided modification.** Add a private helper used by the public function.

3. **Independent construction.** Move a pure domain operation into an inline module.

4. **Diagnose a defect.** Diagnose a consumer accessing a private representation field.

5. **Boundary evidence.** Test the public contract without relying on internal helper names.

6. **Transfer and justify.** Split a future library and executable crate by responsibility and document dependency direction.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

Modules are not runtime services. Excessive pub can freeze accidental implementation details into an API. A use declaration does not install a dependency.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Call a reviewed public function) before changing anything, and confirm its observation: The consumer uses the domain module interface.
2. Compare Example B (Import a name without changing ownership) with Example A and name the first line whose behavior differs. Its observation is: The shorter imported name refers to the same function.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Modules are not runtime services.

Tempting approaches to rule out before you compare:

- **Task 1.** Assuming `domain` must be `pub mod` before `main` can use it confuses crate-level privacy with export. That change compiles, but it would only matter for code outside this crate, and it widens the surface for no caller here.
- **Task 2.** Marking the helper `pub fn factor` "just in case" compiles, but it lets `main` write `domain::factor()`. Renaming or inlining the helper later then breaks that caller, which is exactly the accidental surface the lesson warns about.
- **Task 3.** Returning `unit * quantity` as a plain `u32` hides the overflow: `total(u32::MAX, 2)` panics with attempt to multiply with overflow when overflow checks are on and wraps to 4294967294 otherwise, so the `None` contract cannot be expressed at all.
- **Task 5.** Asserting `domain::factor() == 2` fails to compile from `main` with E0603. Making `factor` public to satisfy the test turns a refactoring detail into API that every later change must preserve.
- **Task 6.** Keeping the domain logic in `src/main.rs` and adding `tests/report.rs` fails: an integration test links against the library target, and a package with only a binary has no library for the test to `use`.

## Self-check and next step

Which items in `domain` does `main` reach, and which `pub` keyword makes each reachable? What does rustc report if `double` loses its `pub`? After `use domain::double;`, does `double(3)` call a copy of the function or the same function? Why is a small public surface easier to keep stable than a module where every item is `pub`?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [The Rust Book, 7.2 Modules and Privacy](https://doc.rust-lang.org/book/ch07-02-defining-modules-to-control-scope-and-privacy.html) for `pub` and the default of private items.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-023: Modules, visibility and a stable public surface.
Read courses/rust/guides/rust-023.md and courses/rust/lessons/rust-023.rs. Prerequisites: rust-022.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-023_solution.rs and
courses/rust/solutions/rust-023_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
