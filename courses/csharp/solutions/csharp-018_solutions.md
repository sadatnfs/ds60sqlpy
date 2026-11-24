# csharp-018: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-018_solution.cs](csharp-018_solution.cs). It runs both worked examples, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Retain the element type:** The constraint guarantees comparison while the generic return preserves the concrete type. The same method returns an int or a string without object casts.

**Preserve a generic relationship:** A generic data model encodes relationships between fields independently of the values used. Swap preserves the element type, and a tie remains a valid value.

## Task answers

### Task 1: Predict and explain

Predict the inferred type at each Max call.

**Written answer.** `Max(4, 9)` infers `T` as `int` from both arguments and returns `int` 9. `Max("apple", "pear")` infers `string` and returns `"pear"`. `Max(5, 5)` is again `int`.

**Why it is correct.** Type inference looks at the argument types. Both arguments must agree on one `T`, and that `T` must satisfy `IComparable<T>`, which both `int` and `string` do.

**Plausible wrong approach.** Predicting that the result is typed as the constraint, `IComparable<int>`, leads to unnecessary casts such as `(int)Max(4, 9)`. The return type is `T` itself, so `Max(4, 9) + 1` compiles directly and is 10.

**How to verify.** Add `int next = Max(4, 9) + 1; Check(next == 10, "typed result");`. Also check `Max(4, 9.5) == 9.5`: the `int` argument converts to `double`, so inference picks `double` for that call.

### Task 2: Guided modification

Use Max with decimal values.

**Written answer.** Call `decimal price = Max(19.99m, 5.25m);` and check `price == 19.99m`. Both literals carry the `m` suffix, so `T` is `decimal`.

**Why it is correct.** `decimal` implements `IComparable<decimal>`, so it satisfies the constraint and the method returns a `decimal` without any conversion or boxing.

**Plausible wrong approach.** Writing `Max(19.99, 5.25m)` mixes a `double` literal with a `decimal`, which fails inference. Casting both to `double` to make it compile loses decimal precision for money values.

**How to verify.** Check `Max(19.99m, 5.25m) == 19.99m` and `Max(0.1m + 0.2m, 0.3m) == 0.3m`; with `decimal` the sum is exactly 0.3, so the tie returns the left value and the check passes.

### Task 3: Independent construction

Create a generic immutable three-element container.

**Written answer.** Declare `public record Triple<T>(T First, T Second, T Third) { public Triple<T> Rotate() => new(Second, Third, First); }`. Check `new Triple<int>(1, 2, 3).Rotate() == new Triple<int>(2, 3, 1)`.

**Why it is correct.** The single type parameter states that all three positions hold the same type, and the positional record gives `init`-only properties and value equality, so the container is immutable and comparable.

**Plausible wrong approach.** Using `record Triple(object First, object Second, object Third)` compiles, but `First` comes back as `object`, so reading it as an `int` needs a cast that can throw `InvalidCastException`, the object escape the pitfalls warn about.

**How to verify.** Check the rotation, then check `new Triple<string>("a", "b", "c").First == "a"` with no cast. Try `triple.First = 9;` and confirm the compiler rejects the init-only property.

### Task 4: Diagnose a defect

Explain why an unconstrained T cannot safely call Length.

**Written answer.** In `int Size<T>(T value) => value.Length;` the compiler reports CS1061 because `T` could be `int`, which has no `Length`. Inside the method only members of `object` are known.

**Why it is correct.** A generic method is compiled once for every possible `T`, so it may only use operations every allowed type supports. Without a constraint, that set is just `object`'s members.

**Plausible wrong approach.** Adding `where T : class` does not help, because a class constraint promises a reference type, not a `Length` property. Casting through `dynamic` compiles but fails at run time with `RuntimeBinderException` when `T` is `int`.

**How to verify.** Compile the unconstrained version and read CS1061. Rewrite it as `int Size<T>(IReadOnlyCollection<T> value) => value.Count;`, which asks for exactly the capability it uses, and check `Size(new[] { 1, 2, 3 }) == 3`.

### Task 5: Boundary evidence

Test equal values and document whether the first or second object is returned on a tie.

**Written answer.** `Max` returns `left` when `CompareTo` is greater than or equal to 0, so ties return the first argument. Use records with equal ordering but different identity: `record Item(int Rank, string Name) : IComparable<Item>` comparing only `Rank`, then `Max(new Item(1, "a"), new Item(1, "b")).Name == "a"`.

**Why it is correct.** With integers, the first and second tie values are indistinguishable, so a test cannot see which one was returned. Objects that compare equal but carry different names make the tie policy observable.

**Plausible wrong approach.** Testing only `Max(5, 5) == 5` passes whether the method returns `left` or `right`. Changing `>= 0` to `> 0` would silently switch the policy to the second argument and that check would still pass.

**How to verify.** Check the `Item` tie returns `"a"`. Temporarily change `>= 0` to `> 0` and confirm the check now throws because `"b"` is returned.

### Task 6: Transfer and justify

Design a generic helper with the smallest useful capability constraint.

**Written answer.** Write `static T FirstOr<T>(IEnumerable<T> items, Func<T, bool> keep, T fallback)` with no constraint at all, because it only enumerates and calls a delegate. Contrast with `Max`, which needs `IComparable<T>` because it calls `CompareTo`.

**Why it is correct.** Each constraint narrows which types callers may use. A helper that never compares or constructs `T` should accept every type, including structs and nullable references.

**Plausible wrong approach.** Adding `where T : IComparable<T>` to `FirstOr` by habit compiles but blocks a caller with a list of records that are not comparable, for no algorithmic reason.

**How to verify.** Call `FirstOr(new[] { 1, 4, 6 }, n => n > 3, 0)` and expect 4, then call it with a list of an uncomparable `record Tag(string Name)` and confirm it compiles and returns the first match.

## Mechanism and diagnostic reasoning

Generics let an algorithm or container retain a type relationship without copying source for each element type. A List<int> cannot accidentally accept text because the element relationship is checked by the compiler. This differs from storing everything as object and discovering type mistakes later through casts.

An unconstrained type parameter supports only operations valid for every possible type. Constraints declare additional capabilities, such as comparison or a required interface. The constraint should express what the algorithm really needs. A comparable type supports ordering, but the algorithm must still specify what happens for an empty sequence and whether ties preserve the first value.

`T` names a type parameter. `where T : IComparable<T>` makes CompareTo available. The method call can infer T from its arguments. Return types preserve the relationship to the input type.

Adding a class constraint does not make arbitrary methods available. Avoid converting to object merely to escape a compiler error. String ordering may require a comparer for culture-independent business behavior.

## Review before continuing

Run the reference and confirm that it prints `csharp-018: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
