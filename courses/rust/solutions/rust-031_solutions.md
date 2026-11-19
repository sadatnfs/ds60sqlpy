# rust-031: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-031_solution.rs](rust-031_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Represent recursion through indirection:** Each node owns the next node and releases that chain through ordinary ownership. Box makes the recursive type have a finite outer size.

**Observe a weak target disappearing:** Upgrade makes absence explicit after the final strong owner is released. The weak reference does not keep the String alive.

## Task answers

### Task 1: Predict and explain

Draw the owning edges of the recursive list.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Each node owns the next node and releases that chain through ordinary ownership. Box makes the recursive type have a finite outer size.

### Task 2: Guided modification

Add another node and predict its total.

No separate reference answer has been written for this task. Start from Example B: Upgrade makes absence explicit after the final strong owner is released. The weak reference does not keep the String alive.

### Task 3: Independent construction

Model a parent-child relationship with a weak back-reference.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use std::cell::RefCell;
    use std::rc::{Rc, Weak};
    struct Parent {
        name: String,
        children: RefCell<Vec<Rc<Child>>>,
    }
    struct Child {
        parent: RefCell<Weak<Parent>>,
    }
    let parent = Rc::new(Parent {
        name: String::from("root"),
        children: RefCell::new(Vec::new()),
    });
    let child = Rc::new(Child {
        parent: RefCell::new(Weak::new()),
    });
    *child.parent.borrow_mut() = Rc::downgrade(&parent);
    parent.children.borrow_mut().push(Rc::clone(&child));
    let found = child.parent.borrow().upgrade().map(|p| p.name.clone());
    assert_eq!(found.as_deref(), Some("root"));
    assert_eq!(Rc::strong_count(&parent), 1);
    drop(parent);
    assert!(child.parent.borrow().upgrade().is_none());
    Ok(())
}
```

**Observe:** The child finds root while the parent lives, the parent keeps one strong count, and after it is dropped the back-reference upgrades to None.

The parent owns its children with Rc, while each child refers back with Weak, so the pair forms no reference cycle and the parent can be freed.

### Task 4: Diagnose a defect

Diagnose an Rc cycle that keeps both objects alive.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Memory safety does not guarantee absence of leaks. Deep recursive drops can have stack costs. RefCell moves borrow checking to runtime and remains single-threaded.

### Task 5: Boundary evidence

Test an empty list and upgrading a dead weak reference.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Represent recursion through indirection) and Example B (Observe a weak target disappearing).

### Task 6: Transfer and justify

Choose Box, Rc or Arc for unique, local-shared and cross-thread ownership scenarios.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Box**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Box provides owned indirection, useful when a recursive structure needs a finite-sized outer representation. Rc provides shared ownership within one thread, while Weak provides a non-owning link that may no longer upgrade to a live owner. These pointers express different lifetime contracts and should not be chosen interchangeably.

Cycles of strong reference counts can leak resources even in memory-safe Rust. A parent-child structure often needs owning edges in one direction and weak back-references in the other. RefCell permits checked interior mutation in a single thread; violating its dynamic borrowing rules panics. It does not make Rc suitable for concurrent access.

Box::new stores an owned value behind a pointer. Rc::clone increments shared ownership. Rc::downgrade creates Weak, and upgrade returns Option because the owner may have disappeared.

Memory safety does not guarantee absence of leaks. Deep recursive drops can have stack costs. RefCell moves borrow checking to runtime and remains single-threaded.

## Review before continuing

Run the reference and confirm that it prints `rust-031: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
