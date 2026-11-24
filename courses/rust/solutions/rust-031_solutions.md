# rust-031: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-031_solution.rs](rust-031_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Represent recursion through indirection:** Each node owns the next node and releases that chain through ordinary ownership. Box makes the recursive type have a finite outer size.

**Observe a weak target disappearing:** Upgrade makes absence explicit after the final strong owner is released. The weak reference does not keep the String alive.

## Task answers

### Task 1: Predict and explain

Draw the owning edges of the recursive list.

**Written answer.** `list` owns the outer `Node::More(2, ...)`. That node owns a `Box`, which owns the heap node `More(3, ...)`, whose `Box` owns the heap node `End`. Every node has exactly one owner, so the edges form a chain with no sharing. When `list` is dropped, each `Box` drops its node in turn from the head toward `End`.

**Why it is correct.** `Box<Node>` has a fixed size, the size of one pointer, so `Node` has a finite size even though it is recursive. Unique ownership along the chain means cleanup needs no counting.

**Plausible wrong approach.** Drawing `Node::More(i32, Node)` without the `Box` describes an infinitely sized type; the compiler rejects it with E0072, recursive type has infinite size.

**How to verify.** Define `enum Bad { End, More(i32, Bad) }` and read E0072, which suggests inserting indirection such as `Box`.

### Task 2: Guided modification

Add another node and predict its total.

**Reference answer.** The same statements run as the `Task 2` block of the reference program; here they are wrapped in `main` as a complete file. It uses `Node` from the lesson's helpers, defined in the reference program.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let list = Node::More(
        1,
        Box::new(Node::More(2, Box::new(Node::More(3, Box::new(Node::End))))),
    );
    assert_eq!(list.total(), 6);
    let extended = Node::More(10, Box::new(list));
    assert_eq!(extended.total(), 16);
    Ok(())
}
```

**Observe:** The three-node list totals 6, and prepending a node with 10 totals 16.

`total` adds each value to the total of the rest, so a new node changes the sum by exactly its own value. Prepending moves the whole old list into a new `Box`; nothing is copied, and `list` is no longer usable afterward.

**Plausible wrong approach.** Predicting 10 for the extended list, as if the new head replaced the old one, forgets that `More(10, Box::new(list))` keeps the old nodes as its tail.

**How to verify.** Run the block. Add `list.total()` after `extended` is built and read E0382, use of moved value.

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

**Written answer.** The defect is two nodes of type `Rc<RefCell<Peer>>` where each holds an `Rc` to the other. Dropping both local handles lowers each strong count from 2 to 1, never to 0, so neither destructor runs and both allocations leak. Make one direction `Weak`, as a child's back-reference to its parent in task 3 does, so the owning edges form a tree.

**Why it is correct.** `Rc` frees its value when the strong count reaches zero, and a cycle of strong edges keeps every count at one or more. Safe Rust prevents use after free, but it does not promise freedom from leaks.

**Plausible wrong approach.** Calling `drop` on both handles explicitly does not help: it releases the same two local references that leaving scope would.

**How to verify.** Keep `let probe = Rc::downgrade(&first);`, drop both handles, and assert `probe.upgrade().is_some()`: the node is still alive.

### Task 5: Boundary evidence

Test an empty list and upgrading a dead weak reference.

**Reference answer.** The same statements run as the `Task 5` block of the reference program; here they are wrapped in `main` as a complete file. It uses `Node` from the lesson's helpers, defined in the reference program.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    assert_eq!(Node::End.total(), 0);
    let single = Node::More(-4, Box::new(Node::End));
    assert_eq!(single.total(), -4);
    let weak = {
        let owner = std::rc::Rc::new(5);
        std::rc::Rc::downgrade(&owner)
    };
    assert!(weak.upgrade().is_none());
    assert_eq!(weak.strong_count(), 0);
    let never: std::rc::Weak<i32> = std::rc::Weak::new();
    assert!(never.upgrade().is_none());
    Ok(())
}
```

**Observe:** An empty list totals 0 and a single negative node totals -4. A weak reference whose owner left its block upgrades to None with strong count 0, as does a Weak that never pointed anywhere.

`End` is the base case of the recursion, so the empty list needs no special handling. `upgrade` returns an `Option` precisely so that a dead target is an ordinary, checkable outcome rather than a dangling pointer.

**Plausible wrong approach.** Unwrapping `weak.upgrade()` on the assumption that the target is still alive turns a normal absence into a panic.

**How to verify.** Run the block. Move `owner` out of the inner block so it lives longer and the first `is_none` assertion fails.

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
