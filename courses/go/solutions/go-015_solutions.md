# go-015: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

Generics express algorithms whose structure is shared across several types. A type parameter is constrained by the operations the algorithm requires. comparable permits equality and map keys; it does not permit ordering or arithmetic. A constraint using a type set can admit underlying integer types with the ~ operator. Generic code still needs a meaningful domain contract: adding signed integers can overflow, floating equality can surprise, and pointer equality is not deep value equality. Prefer a normal function when only one concrete type is useful. A useful generic abstraction removes real duplication while preserving clear errors and readable call sites.

`func first[T any](items []T) (T,bool)` declares a type parameter `T`. `var zero T` obtains its zero value for an empty result. A custom constraint such as `interface { ~int | ~int64 }` admits named types with those underlying types. Type inference often determines `T` from arguments. A constraint belongs to compile-time capability checking; it is not runtime validation of application data.

## 1. Reuse an element contract

Call first with an integer slice and a string slice.

```go
a, okA := first([]int{4, 5})
b, okB := first([]string{"red", "blue"})
check(okA && okB && a == 4 && b == "red", "generic first")
```

**Expected:** The results are 4 and red with presence true.

The algorithm needs indexing and length, not knowledge of the element representation. That makes any an honest constraint here.

## 2. Handle a generic empty value

Call first with an empty integer slice.

```go
v, ok := first([]int{})
check(v == 0 && !ok, "empty generic")
```

**Expected:** The result is zero with presence false.

A zero value alone cannot distinguish an empty input from a first element equal to zero. The boolean preserves that information.

## 3. Preserve stable uniqueness

Deduplicate 2, 1, 2 while preserving first occurrence.

```go
v := unique([]int{2, 1, 2})
check(len(v) == 2 && v[0] == 2 && v[1] == 1, "unique order")
```

**Expected:** The result is 2 then 1.

A map tracks membership while the result slice preserves order. Returning map keys directly would lose the ordering contract.

## 4. Admit a named underlying type

Sum two values of a named Count type.

```go
check(sumInts([]Count{3, 4}) == Count(7), "underlying type")
```

**Expected:** The result is Count(7).

The tilde constraint admits the underlying int representation while preserving the named result type.

## 5. Test the empty sum identity

Sum an empty int64 slice.

```go
check(sumInts([]int64{}) == 0, "generic identity")
```

**Expected:** The result is int64 zero.

The identity must make sense for every allowed type. Expanding a constraint to unrelated types can invalidate an otherwise convenient implementation.

## 6. Transfer equality semantics

Deduplicate strings with different case.

```go
v := unique([]string{"Red", "red", "Red"})
check(len(v) == 2, "case policy")
```

**Expected:** Red and red remain distinct.

comparable uses the language equality operation. Case folding or domain normalization would need an explicit preprocessing policy, not a hidden generic assumption.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
