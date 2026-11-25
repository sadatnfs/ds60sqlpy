# rust-031: Box, Rc, Weak and recursive structures

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `rust-030`

## Learning objectives

Build recursive and shared structures with Box, Rc and Weak without reference cycles. The central exercise is task 3: Model a parent-child relationship with a weak back-reference.

## Purpose and mental model

Box provides owned indirection, useful when a recursive structure needs a finite-sized outer representation. Rc provides shared ownership within one thread, while Weak provides a non-owning link that may no longer upgrade to a live owner. These pointers express different lifetime contracts and should not be chosen interchangeably.

Cycles of strong reference counts can leak resources even in memory-safe Rust. A parent-child structure often needs owning edges in one direction and weak back-references in the other. RefCell permits checked interior mutation in a single thread; violating its dynamic borrowing rules panics. It does not make Rc suitable for concurrent access.

## Vocabulary and concepts

**Box:** A uniquely owned heap allocation with a known pointer-sized handle.

**Rc:** Single-threaded reference-counted shared ownership.

**Weak:** A non-owning link whose target may no longer exist.

## How to run this lesson

Beyond the prelude, this lesson's programs use `std::rc`. A passing run prints `rust-031: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

Box::new stores an owned value behind a pointer. Rc::clone increments shared ownership. Rc::downgrade creates Weak, and upgrade returns Option because the owner may have disappeared.

**Reading Example A (Represent recursion through indirection, code below).** `enum Node { End, More(i32, Box<Node>) }` defines a list as either an empty end or a value followed by another node. A field of type `Node` directly inside `Node` would make the type infinitely large, and rustc rejects that with E0072, recursive type has infinite size. `Box<Node>` stores the next node on the heap, so the outer value holds only a pointer of known size. `total(&self)` matches on the borrowed node: `End` contributes 0, and `More(value, next)` binds the integer and a reference to the box. `next.total()` works through auto-dereference, calling the method on the boxed `Node` and recursing until it reaches `End`. Building the list nests the `Box::new` calls from the inside out.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Represent recursion through indirection

Each node owns the next node and releases that chain through ordinary ownership.

```rust
enum Node {
    End,
    More(i32, Box<Node>),
}
impl Node {
    fn total(&self) -> i32 {
        match self {
            Self::End => 0,
            Self::More(value, next) => value + next.total(),
        }
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let list = Node::More(2, Box::new(Node::More(3, Box::new(Node::End))));
        assert_eq!(list.total(), 5);
    }
    println!("rust-031: passed");
    Ok(())
}
```

**Observe:** Box makes the recursive type have a finite outer size.

### Example B: Observe a weak target disappearing

Upgrade makes absence explicit after the final strong owner is released.

```rust
enum Node {
    End,
    More(i32, Box<Node>),
}
impl Node {
    fn total(&self) -> i32 {
        match self {
            Self::End => 0,
            Self::More(value, next) => value + next.total(),
        }
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let owner = std::rc::Rc::new(String::from("value"));
        let weak = std::rc::Rc::downgrade(&owner);
        assert!(weak.upgrade().is_some());
        drop(owner);
        assert!(weak.upgrade().is_none());
    }
    println!("rust-031: passed");
    Ok(())
}
```

**Observe:** The weak reference does not keep the String alive.

## Exercises

1. **Predict and explain.** Draw the owning edges of the recursive list.

2. **Guided modification.** Add another node and predict its total.

3. **Independent construction.** Model a parent-child relationship with a weak back-reference.

4. **Diagnose a defect.** Diagnose an Rc cycle that keeps both objects alive.

5. **Boundary evidence.** Test an empty list and upgrading a dead weak reference.

6. **Transfer and justify.** Choose Box, Rc or Arc for unique, local-shared and cross-thread ownership scenarios.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

Memory safety does not guarantee absence of leaks. Deep recursive drops can have stack costs. RefCell moves borrow checking to runtime and remains single-threaded.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Represent recursion through indirection) before changing anything, and confirm its observation: Box makes the recursive type have a finite outer size.
2. Compare Example B (Observe a weak target disappearing) with Example A and name the first line whose behavior differs. Its observation is: The weak reference does not keep the String alive.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Memory safety does not guarantee absence of leaks.

Tempting approaches to rule out before you compare:

- **Task 1.** Drawing `Node::More(i32, Node)` without the `Box` describes an infinitely sized type; the compiler rejects it with E0072, recursive type has infinite size.
- **Task 2.** Predicting 10 for the extended list, as if the new head replaced the old one, forgets that `More(10, Box::new(list))` keeps the old nodes as its tail.
- **Task 5.** Unwrapping `weak.upgrade()` on the assumption that the target is still alive turns a normal absence into a panic.

## Self-check and next step

Why does the recursive `Node` in Example A need a `Box` for its next link, and what does rustc report without one? In Example B, why does `Weak::upgrade` return `Some` before the `String` is dropped and `None` afterwards? What would leak if a child held an `Rc` to its parent instead of a `Weak`?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [The Rust Book, 15.6 Reference Cycles](https://doc.rust-lang.org/book/ch15-06-reference-cycles.html) for how `Weak` breaks an ownership cycle.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-031: Box, Rc, Weak and recursive structures.
Read courses/rust/guides/rust-031.md and courses/rust/lessons/rust-031.rs. Prerequisites: rust-030.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-031_solution.rs and
courses/rust/solutions/rust-031_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
