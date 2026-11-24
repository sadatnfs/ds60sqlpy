# go-015: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

Generics express algorithms whose structure is shared across several types. A type parameter is constrained by the operations the algorithm requires. comparable permits equality and map keys; it does not permit ordering or arithmetic. A constraint using a type set can admit underlying integer types with the ~ operator. Generic code still needs a meaningful domain contract: adding signed integers can overflow, floating equality can surprise, and pointer equality is not deep value equality. Prefer a normal function when only one concrete type is useful. A useful generic abstraction removes real duplication while preserving clear errors and readable call sites.

`func first[T any](items []T) (T,bool)` declares a type parameter `T`. `var zero T` obtains its zero value for an empty result. A custom constraint such as `interface { ~int | ~int64 }` admits named types with those underlying types. Type inference often determines `T` from arguments. A constraint belongs to compile-time capability checking; it is not runtime validation of application data.

## 1. Reuse an element contract: change one input

Copy worked example 1 into a scratch pad and change `a, okA := first([]int{4, 5})` to `a, okA := first([]int{5, 5})`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.

The unchanged code is worked example 1:

```go
a, okA := first([]int{4, 5})
b, okB := first([]string{"red", "blue"})
check(okA && okB && a == 4 && b == "red", "generic first")
```

**Expected:** The changed run panics with `generic first` because `okA && okB && a == 4 && b == "red"` no longer holds. Restoring the original line brings back the worked observation: the results are 4 and red with presence true.

The algorithm needs indexing and length, not knowledge of the element representation. That makes any an honest constraint here.

**Approach.** Instantiate `first` with the edited slice `[]int{5, 5}`. The function returns `items[0]`, so `a` becomes 5 and `okA` stays true.

**Why it holds here.** Only `a == 4` changes: `okA`, `okB` and `b == "red"` still hold, so the conjunction fails on the integer value and panics with `generic first`.

**A plausible wrong approach.** Predicting that the duplicate makes `okA` false or that type inference changes. `first` neither inspects duplicates nor depends on the values, and `T` is still inferred as `int` from the slice type.

**Verify.** Print `a, okA` and see `5 true` before the panic. Restoring `4` restores the success line.

## 2. Handle a generic empty value: diagnose an edited check

A careless edit changed the check in worked example 2 so that it reads `check(v != 0 && !ok, "empty generic")`. Run worked example 2 with that line, explain why the edited check now fails for the same program state, and restore it.

The unchanged code is worked example 2:

```go
v, ok := first([]int{})
check(v == 0 && !ok, "empty generic")
```

**Expected:** Before the repair the program panics with `empty generic`; after it the line reads `check(v == 0 && !ok, "empty generic")` again and the result is zero with presence false.

A zero value alone cannot distinguish an empty input from a first element equal to zero. The boolean preserves that information.

**Approach.** For an empty slice, `first` declares `var zero T` and returns it with `false`, so for `[]int{}` the results are 0 and false.

**Why it holds here.** The original check accepts exactly that state. The edited `v != 0` is false because 0 is the zero value of `int`, so the same program state now panics with `empty generic`.

**A plausible wrong approach.** Returning `items[0]` without the length test, which panics with an index out of range on the empty slice, or returning a sentinel such as -1, which does not compile because -1 is not a valid value for every `T`.

**Verify.** Print `v, ok` for `first([]int{})` and `first([]int{0})`: they show `0 false` and `0 true`, which is why the boolean, not the value, reports presence.

## 3. Preserve stable uniqueness

Deduplicate 2, 1, 2 while preserving first occurrence.

```go
v := unique([]int{2, 1, 2})
check(len(v) == 2 && v[0] == 2 && v[1] == 1, "unique order")
```

**Expected:** The result is 2 then 1.

A map tracks membership while the result slice preserves order. Returning map keys directly would lose the ordering contract.

**Approach.** Walk the input once, record each value in the `seen` map and append it to `out` only the first time it appears.

**Why it holds here.** For 2, 1, 2 the first 2 and the 1 are appended and the second 2 is skipped, so `out` is `[2 1]` and its order follows first occurrence.

**A plausible wrong approach.** Building the result by ranging over the `seen` map. Go randomizes map iteration order, so `v[0] == 2` fails on some runs, which makes the test flaky rather than reliably wrong.

**Verify.** Print `unique([]int{2, 1, 2})` and see `[2 1]`, and `unique([]int{3, 3, 3})` to see `[3]`. Run several times to confirm the order is stable.

## 4. Admit a named underlying type

Sum two values of a named Count type.

```go
check(sumInts([]Count{3, 4}) == Count(7), "underlying type")
```

**Expected:** The result is Count(7).

The tilde constraint admits the underlying int representation while preserving the named result type.

**Approach.** Call `sumInts` with `[]Count{3, 4}`. `T` is inferred as `Count`, which `Integer` admits through `~int`.

**Why it holds here.** The tilde admits any type whose underlying type is `int`, and `out += x` works on that representation, so the result is `Count(7)` with the named type preserved.

**A plausible wrong approach.** Writing the constraint as `int | int64` without tildes. Then `Count` does not satisfy `Integer`, and the call fails to compile with a hint about a missing `~`.

**Verify.** Print `fmt.Printf("%T %v\n", sumInts([]Count{3, 4}), sumInts([]Count{3, 4}))` and see `main.Count 7`.

## 5. Test the empty sum identity

Sum an empty int64 slice.

```go
check(sumInts([]int64{}) == 0, "generic identity")
```

**Expected:** The result is int64 zero.

The identity must make sense for every allowed type. Expanding a constraint to unrelated types can invalidate an otherwise convenient implementation.

**Approach.** Call `sumInts` on an empty `[]int64`. The accumulator `var out T` starts at the zero value and the loop body never runs.

**Why it holds here.** Zero is the additive identity for every type in `Integer`, so returning the untouched accumulator gives `int64(0)` and the check passes.

**A plausible wrong approach.** Seeding the accumulator with `items[0]` and summing `items[1:]`. It works for `[]Count{3, 4}` but panics with an index out of range here, because empty input is a defined case.

**Verify.** Print `fmt.Printf("%T %v\n", sumInts([]int64{}), sumInts([]int64{}))` and see `int64 0`.

## 6. Transfer equality semantics

Deduplicate strings with different case.

```go
v := unique([]string{"Red", "red", "Red"})
check(len(v) == 2, "case policy")
```

**Expected:** Red and red remain distinct.

comparable uses the language equality operation. Case folding or domain normalization would need an explicit preprocessing policy, not a hidden generic assumption.

**Approach.** Deduplicate `Red`, `red`, `Red` with the same `unique`, which compares strings with `==` through `comparable`.

**Why it holds here.** `Red` and `red` differ in their first byte, so they are distinct keys; only the second `Red` is dropped and the result has length 2.

**A plausible wrong approach.** Lowercasing inside the generic helper to merge them. `strings.ToLower` needs a `string`, not an arbitrary `T`, so it cannot compile there, and a string-only version would silently change the policy and make the length 1.

**Verify.** Print the result and see `[Red red]`. To fold case, map the input through `strings.ToLower` before calling `unique` and expect `[red]`.

## Transfer after comparison

Write `last[T any](items []T) (T, bool)` and `count[T comparable](items []T, x T) int`. Check `last([]string{"a", "b"})` returns `b` and true, `last([]float64{})` returns 0 and false, and `count([]Count{2, 2, 3}, 2)` returns 2. Explain which check a sentinel return or a constraint without `~` would break.
