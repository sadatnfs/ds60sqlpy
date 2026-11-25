# rust-020: explanation and comparison

Executable reference: [rust-020_solution.rs](rust-020_solution.rs), which runs both examples and the coded answers.

Open this only after [an attempt](../STUDY-GUIDE.md#attempt-a-lesson).

## Why the two examples differ

**Consume a transformation recipe:** Copied turns referenced integers into independent small values before filtering and mapping. The recipe selects and transforms while retaining the borrowed source.

**Observe iterator progress:** Calling next again does not restart the source automatically. The iterator advances and eventually exhausts.

## Task answers

### Task 1: Predict and explain

Identify adapters and the final consumer.

**Written answer.** In Example A, `values.iter()` creates the source, `copied`, `filter` and `map` are adapters, and `collect` is the consumer that drives the chain. In Example B, `into_iter` creates the source and each `next` call is a manual consumption step.

**Why it is correct.** Adapters only wrap one iterator in another and do no work; a consumer pulls items through the chain. That is why `values` is still four long afterwards: `iter` borrowed it.

**Plausible wrong approach.** Calling `filter` the consumer because it removes items gets the roles backwards. Without `collect`, the filter never runs, and the compiler warns that iterators are lazy and do nothing unless consumed.

**How to verify.** Write `values.iter().map(|value| value * 10);` as a statement and read the `unused Map that must be used` warning. Restore `collect` and `result == vec![20, 40]` passes.

### Task 2: Guided modification

Add a take limit and predict how much work is demanded.

**Written answer.** Add `.take(1)` after `map`: the result is `vec![20]`. Only two source items are examined: 1 is filtered out, 2 becomes 20, and `take` stops pulling, so 3 and 4 are never visited.

**Why it is correct.** Iterators are pull-based: `collect` asks `take`, which asks `map`, and so on. Once `take` has yielded one item it returns `None` without asking for more.

**Plausible wrong approach.** Placing `take(1)` before `filter` takes only the first source item, 1, which is odd, so the result is empty. Adapter order changes which items the limit counts.

**How to verify.** Insert `.inspect(|value| seen.push(*value))` right after `copied()`, with `let mut seen = Vec::new();` above. Assert `result == vec![20]` and `seen == vec![1, 2]`.

### Task 3: Independent construction

Write a borrowed transformation returning a collected result.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 3` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    fn upper_names(names: &[&str]) -> Vec<String> {
        names.iter().map(|name| name.to_uppercase()).collect()
    }
    let names = ["pear", "fig"];
    assert_eq!(upper_names(&names), vec!["PEAR", "FIG"]);
    assert_eq!(names, ["pear", "fig"]);
    Ok(())
}
```

**Observe:** The result is PEAR and FIG, and the borrowed input is unchanged.

The function borrows the input slice, the iterator chain is lazy, and collect consumes it into a new owned Vec.

**Plausible wrong approach.** Ending the function body at `.map(|name| name.to_uppercase())` without `collect` fails with E0308: the body is a lazy `Map` iterator, not the `Vec<String>` the signature promises.

**How to verify.** Add `assert_eq!(upper_names(&[]), Vec::<String>::new());` and `assert_eq!(upper_names(&["straße"]), vec!["STRASSE"]);`. The second shows `to_uppercase` can change a word's length.

### Task 4: Diagnose a defect

Diagnose constructing a lazy map and expecting it to execute immediately.

**Written answer.** The defect is `values.iter().map(|value| println!("{value}"));`, expecting four lines. Nothing prints, because `map` only builds an adapter. Use `for value in &values { println!("{value}"); }` or `for_each` when the side effect is the point.

**Why it is correct.** No consumer ever calls `next`, so the closure never runs. rustc flags this with a warning that the unused `Map` must be used, because iterators are lazy.

**Plausible wrong approach.** Forcing execution with `.count()` or `.collect::<Vec<()>>()` does print the lines, but it builds and discards a result purely for its side effects, hiding the intent the lesson's pitfall warns about.

**How to verify.** Prove laziness: `let mut calls = 0; let lazy = values.iter().map(|value| { calls += 1; value * 10 }); drop(lazy); assert_eq!(calls, 0);`. Replacing `drop(lazy)` with `let total: i32 = lazy.sum();` gives `calls == 4` and `total == 100`.

### Task 5: Boundary evidence

Test empty input and a partially consumed iterator.

**Written answer.** Empty input: `let empty: Vec<i32> = Vec::new();` through Example A's chain collects an empty `Vec`. Partial consumption: `let mut iterator = [2, 3, 4].into_iter();` then `iterator.next() == Some(2)`, and `iterator.collect::<Vec<_>>()` returns `vec![3, 4]`.

**Why it is correct.** A chain over no items calls none of its closures and collects nothing. `collect` starts from the iterator's current position, so an item already taken by `next` is not seen again.

**Plausible wrong approach.** Expecting `collect` to restart and return `[2, 3, 4]` treats the iterator as the array. Calling `iterator.next()` after `collect` fails to compile with E0382, because `collect` took the iterator by value.

**How to verify.** Assert both results, then add `iterator.next()` after the `collect` and read E0382, use of moved value.

### Task 6: Transfer and justify

Choose iter, iter_mut or into_iter for three operations and justify ownership.

**Written answer.** Sum prices with `iter()`: `let total: u32 = prices.iter().sum();`. Apply a 10 percent discount in place with `iter_mut()`: `for price in prices.iter_mut() { *price -= *price / 10; }`. Move names into a new owner with `into_iter()`: `let registry: Vec<String> = names.into_iter().collect();`.

**Why it is correct.** Summing only reads, discounting needs exclusive access to each element, and the registry should own the `String`s without cloning them. Each form grants exactly that much access. A limitation is that `into_iter` leaves `names` unusable afterwards.

**Plausible wrong approach.** Using `into_iter()` for the sum consumes `prices`, so the discount loop then fails with E0382. Using `iter()` for the discount fails instead, because `*price -= ...` cannot assign through a `&` reference.

**How to verify.** With `prices = vec![100, 250]` and `names = vec![String::from("pear")]`, assert `total == 350`, `prices == [90, 225]` and `registry == ["pear"]`.

## Mechanism and diagnostic reasoning

Iterator adapters describe transformations that execute when consumed. Map and filter generally build a recipe; collect, sum or a loop drives it. Repeated iteration is possible only if the source can be recreated or borrowed appropriately. An iterator itself holds progress and may be exhausted.

The three common vector forms make ownership visible: iter yields shared references, iter_mut yields exclusive references, and into_iter consumes owned elements. Choose the form matching the work. A lazily executed closure with side effects is harder to reason about, so keep transformations pure unless the side effect is explicitly the lesson.

`iter().filter(...).map(...)` chains borrowed transformations. collect needs an inferred or annotated target. next advances one iterator instance. into_iter consumes the collection when the collection owns non-Copy elements.

Laziness does not mean no allocation if a later consumer collects. Reusing an exhausted iterator does not recreate it. A chain with hidden effects can execute at an unexpected boundary.

## Review before continuing

Rebuild Example B (Observe iterator progress) from a blank pad.

Review routine: [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).
