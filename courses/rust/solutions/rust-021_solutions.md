# rust-021: explanation and comparison

Executable reference: [rust-021_solution.rs](rust-021_solution.rs), which runs both examples and the coded answers.

Open this only after [an attempt](../STUDY-GUIDE.md#attempt-a-lesson).

## Why the two examples differ

**Observe mutable capture:** The scope makes the exclusive captured access visible. The closure updates its borrowed accumulator before the borrow ends.

**Move owned data into a closure:** Returning the owned capture makes this closure consuming rather than indefinitely repeatable. The closure transfers its captured String to the caller once.

## Task answers

### Task 1: Predict and explain

Identify capture mode and calling capability in each example.

**Written answer.** In Example A, `add` captures `count` by mutable borrow because its body runs `count += value`, so it implements `FnMut` and must be bound with `let mut add`. In Example B, `move` captures `text` by value and the body returns it, so the closure implements only `FnOnce`.

**Why it is correct.** The compiler infers the capture mode from what the body does with each variable, and the call traits follow: mutation needs `FnMut`, and moving a capture out needs `FnOnce`.

**Plausible wrong approach.** Crediting the `move` keyword for Example B being `FnOnce` is wrong: `move || text.len()` also owns `text` yet is `Fn`, callable any number of times. Returning `text` is what makes it consuming.

**How to verify.** Pass `consume` to `fn call_twice(f: impl Fn() -> String)` and read E0525, the closure implements `FnOnce` but `Fn` was expected. A `move || owned.len()` closure passes the same kind of `Fn` bound.

### Task 2: Guided modification

Write a pure repeatable closure capturing an immutable factor.

**Written answer.** Write `let factor = 3; let scale = |value: i32| value * factor;` then `assert_eq!(scale(2), 6);` twice and `assert_eq!(factor, 3);`.

**Why it is correct.** The body only reads `factor`, so the closure captures it by shared reference and implements `Fn`. Calling it any number of times with the same input gives the same output.

**Plausible wrong approach.** Adding a call counter, `calls += 1`, inside the closure makes it `FnMut`. It then needs `let mut scale`, and passing it where `Fn` is required fails with E0525.

**How to verify.** Define `fn twice(f: impl Fn(i32) -> i32) -> (i32, i32) { (f(2), f(2)) }` and assert `twice(scale) == (6, 6)`.

### Task 3: Independent construction

Implement a helper accepting FnMut for repeated transformations.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 3` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    fn apply_times(times: usize, mut step: impl FnMut()) {
        for _ in 0..times {
            step();
        }
    }
    let mut value = 1;
    apply_times(3, || value *= 2);
    assert_eq!(value, 8);
    Ok(())
}
```

**Observe:** Doubling three times turns 1 into 8.

FnMut allows the closure to mutate its captured value on each call, which Fn would forbid.

**Plausible wrong approach.** Dropping `mut` from the parameter `mut step` fails with E0596: calling an `FnMut` needs `&mut step`. Tightening the bound to `impl Fn()` fails too, because the closure assigns to `value`.

**How to verify.** Run the block, then add `apply_times(0, || value *= 2);` with an assertion that `value` is unchanged, and a fresh `value = 1` doubled ten times giving 1024.

### Task 4: Diagnose a defect

Diagnose attempting to call a consuming closure twice.

**Written answer.** Call Example B's closure twice: `let first = consume(); let second = consume();`. rustc reports E0382, use of moved value `consume`, with a note that the closure cannot be invoked more than once because it moves `text` out of its environment. Return `text.clone()` instead to make it repeatable, or call it once.

**Why it is correct.** An `FnOnce` call takes the closure by value, so after the first call the closure, and the `String` it held, are gone.

**Plausible wrong approach.** Removing the `move` keyword does not help: `|| text` still moves `text` out in its body, so the closure is still `FnOnce` and the second call is still rejected.

**How to verify.** Compile the two-call version and read E0382 with its note. Change the body to `text.clone()` and assert both calls return `"owned"`.

### Task 5: Boundary evidence

Test a closure with no captures and one capturing a borrowed reference.

**Written answer.** No captures: `let double = |value: i32| value * 2;` coerces to a function pointer, `let as_fn: fn(i32) -> i32 = double;`. Borrowed capture: `let name = String::from("pear"); let name_ref = &name; let greet = move || format!("hi {name_ref}");` moves only the reference.

**Why it is correct.** A closure with no captures has no environment, so it is zero-sized and converts to `fn`. Moving `name_ref` copies a `&String`, so `name` still owns the text and stays usable.

**Plausible wrong approach.** Calling `drop(name)` before `greet()` assumes `move` gave the closure the `String`. It fails with E0505, cannot move out of `name` because it is borrowed, showing the moved reference still depends on its owner.

**How to verify.** Assert `as_fn(4) == 8`, `std::mem::size_of_val(&double) == 0`, `greet() == "hi pear"` and `name == "pear"`.

### Task 6: Transfer and justify

Choose capture ownership for work that will run on another thread.

**Written answer.** Give the thread owned data: `let rows = vec![2, 3]; let handle = std::thread::spawn(move || rows.iter().sum::<i32>());` and read `handle.join()`. If the caller must keep `rows`, borrow it inside `std::thread::scope(|s| { s.spawn(|| rows.iter().sum::<i32>()); });` instead.

**Why it is correct.** `spawn` requires a `'static` closure because the thread may outlive the current function, so it must own what it touches. A scope joins every thread before returning, which makes borrowing safe. A limitation of `move` is that `rows` is no longer usable by the caller.

**Plausible wrong approach.** Calling `std::thread::spawn(|| rows.iter().sum::<i32>())` without `move` fails with E0373: the closure may outlive the function but borrows `rows`. Leaking the vector to obtain a `'static` reference silences it at the cost of never freeing the memory.

**How to verify.** Assert `handle.join().unwrap() == 5` for the move version. For the scoped version, assert the sum is 5 and that `rows == vec![2, 3]` afterwards.

## Mechanism and diagnostic reasoning

A closure captures surrounding values according to what its body needs. It may borrow, mutate captured state or take ownership. Fn, FnMut and FnOnce describe calling capabilities: shared repeatable calls, mutable repeatable calls and at least one consuming call respectively. These traits form a relationship, not three arbitrary spellings to try until compilation succeeds.

A move closure takes ownership of captured values, useful when work outlives the creating scope. Moving a reference still moves only that reference and does not make its borrowed target live forever. Choose capture and call contracts from the intended lifetime and mutation behavior.

`|value| value * factor` declares a closure. `move || ...` transfers captures into it. A closure mutating a captured accumulator needs mutable calling access. A function accepting FnOnce can invoke consuming behavior once.

Move does not imply deep copy. A moved reference still has a borrowed lifetime. Avoid adding static bounds when the real solution is scoped execution or owned data.

## Review before continuing

Rebuild Example B (Move owned data into a closure) from a blank pad.

Review routine: [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).
