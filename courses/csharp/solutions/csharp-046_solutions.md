# csharp-046: explanation and comparison

Reference program: [csharp-046_solution.cs](csharp-046_solution.cs), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Use a target-typed collection:** The compact syntax still creates concrete storage according to its target. The target types select array and list representations.

**Keep constructor policy visible:** Concise construction should preserve a clear relationship between input parameters and behavior. The three newer checks compile only with C# 13 or 14, which the net10.0 target selects by default; an older target would reject them at compile time. The supplied factor is used by the instance operation, nameof(List<>) is List, missing?.Capacity = 32 leaves the null builder alone, and \e is the escape character.

## Task answers

### Task 1: Predict and explain

Identify the target type of each collection expression.

**Written answer.** A collection expression has no type of its own; the declared target chooses it. In Example A, `int[] values = [1, 2, 3];` creates an `int[]` of length 3, and `List<int> list = [..values, 4];` creates a `List<int>` by copying the three values and appending 4. The same brackets would build a `Span<int>`, an `ImmutableArray<int>` or, for an interface target such as `IEnumerable<int>`, a compiler-chosen type that implements it. Writing `var x = [1, 2];` does not compile because there is no target to choose from.

**Why it is correct.** Knowing the target type tells you what the expression costs and what you can do with the result: an array has a fixed length, a list can grow.

**Plausible wrong approach.** Assuming `[...]` always builds a list, or that it is lazy like a LINQ query, leads to wrong expectations about mutation and evaluation time. Both collections in Example A are built immediately.

**How to verify.** Print `values.GetType()` and `list.GetType()` and confirm `System.Int32[]` and `System.Collections.Generic.List`1[System.Int32]`.

### Task 2: Guided modification

Use an empty collection expression with an explicit target.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```csharp
List<int> none = [];
int[] empty = [];
Check(none.Count == 0 && empty.Length == 0, "both empty");
Check(empty.GetType() == typeof(int[]), "target decides the type");
none.Add(1);
Check(none.Count == 1, "the empty list is a new mutable list");
IEnumerable<int> view = [];
Check(!view.Any(), "interface target is also empty");
```

**Observe:** `[]` produces an empty `List<int>`, an empty `int[]` and an empty sequence, chosen by each declaration; the list can then grow.

An empty collection expression is only valid with an explicit target, because nothing inside the brackets could suggest a type. Each declaration supplies one: a new empty list that can be added to, a zero-length array and, for the interface, an empty sequence. This replaces `new List<int>()` and `Array.Empty<int>()` without changing what the program does.

**Plausible wrong approach.** Writing `var none = [];` fails with a compile error, and assuming the array version can grow like the list confuses the two targets.

**How to verify.** Try `var none = [];` and read the compiler error, then restore the explicit type.

### Task 3: Independent construction

Refactor one simple class to a primary constructor without changing behavior.

**Written answer.** Before, with validation in an ordinary constructor:

```csharp
public sealed class ScaleBefore {
  private readonly int factor;
  public ScaleBefore(int factor) {
    ArgumentOutOfRangeException.ThrowIfNegative(factor);
    this.factor = factor;
  }
  public int Apply(int value) => checked(value * factor);
}
```

After, with a primary constructor:

```csharp
public sealed class Scale(int factor) {
  private readonly int factor =
      factor >= 0 ? factor
                  : throw new ArgumentOutOfRangeException(nameof(factor));
  public int Apply(int value) => checked(value * factor);
}
```

The validation moves into the field initializer, which runs during construction, so a negative factor is still rejected before the object exists. The `readonly` field keeps the value immutable, which a bare primary constructor parameter would not. Both classes were compiled together in the csharp worker image and gave the same results for -2, 0 and 4, both threw `OverflowException` for `int.MaxValue`, and both rejected -1.

**Why it is correct.** A refactor is only safe if it keeps every observable behavior: results, exceptions and immutability. A side-by-side check proves that instead of assuming it.

**Plausible wrong approach.** Writing `public sealed class Scale(int factor) { public int Apply(int value) => checked(value * factor); }` drops the validation and leaves `factor` as a mutable captured parameter, so `new Scale(-1)` would now succeed.

**How to verify.** Construct both versions with -1, 0 and 3 and compare `Apply` for several inputs, including `int.MaxValue`.

### Task 4: Diagnose a defect

Diagnose copying new syntax into a project targeting an older language version.

**Written answer.** The language version, not the runtime, decides which syntax compiles. Compiling Example B's syntax in the worker image with `-p:LangVersion=13` failed with CS9260 `Feature 'null conditional assignment' is not available in C# 13.0` and CS9260 `Feature 'unbound generic types in nameof operator' is not available in C# 13.0`, and with `LangVersion=12` the `\e` escape failed with CS9202. The same code compiled under the default for `net10.0`, which is C# 14. Diagnose by reading the feature name and version in the error, then either target a framework whose default language supports it or rewrite the code in the older syntax.

**Why it is correct.** Each target framework has a default language version. Copied code carries assumptions about that version that are invisible until the compiler names them.

**Plausible wrong approach.** Setting `<LangVersion>latest</LangVersion>` or `preview` as an unexplained fix can produce code that compiles against a runtime that does not support it, and it hides the real mismatch.

**How to verify.** Replace `missing?.Capacity = 32;` with `if (missing is not null) missing.Capacity = 32;` and confirm it compiles at C# 13.

### Task 5: Boundary evidence

Test empty spread and zero scaling.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```csharp
int[] nothing = [];
List<int> spread = [..nothing];
Check(spread.Count == 0, "empty spread adds nothing");
List<int> mixed = [0, ..nothing, 9];
Check(mixed.SequenceEqual(new[] { 0, 9 }), "neighbors kept");
var zero = new Scale(0);
Check(zero.Apply(5) == 0, "zero scaling");
Check(zero.Apply(int.MaxValue) == 0, "zero cannot overflow");
```

**Observe:** Spreading an empty array adds no elements, the surrounding elements stay in order, and a zero factor maps every input, even `int.MaxValue`, to 0.

A spread copies each element of its source, so an empty source contributes nothing and does not insert a placeholder. Scaling by 0 is a valid edge, not an error: `checked(value * 0)` is always 0, so even the largest input cannot overflow.

**Plausible wrong approach.** Expecting `[..nothing]` to throw, or to contain a default 0, confuses an empty spread with a missing value; expecting zero scaling to be rejected adds a rule `Scale` does not have.

**How to verify.** Spread `nothing` twice into the same list and confirm the count is still the number of literal elements.

### Task 6: Transfer and justify

Review a proposed new feature and justify adopting it using readability, compatibility and tooling evidence.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Mechanism and diagnostic reasoning

Language evolution adds concise ways to express familiar contracts. Primary constructors, collection expressions and improved patterns can reduce noise, but unfamiliar syntax should be introduced by its meaning rather than used to make code look advanced. Version-aware code records the target language generation and avoids accidentally relying on a preview feature.

C# 14 accompanies .NET 10 and is the default for the classroom's net10.0 target. C# 13 (.NET 9) added params collections, the System.Threading.Lock type for lock statements and the \e escape sequence. C# 14 adds the field keyword in property accessors, extension members, null-conditional assignment such as a?.B = c, nameof for unbound generic types such as List<> and implicit span conversions. Example B exercises three of these features. New syntax does not relax nullability, ownership or equality rules. A code review should ask whether a feature makes the domain relationship easier to see and whether contributors can diagnose its errors.

A collection expression such as `[1, 2, 3]` is target-typed. A primary constructor supplies parameters used by members. `nameof` produces a symbol name while retaining compile-time refactoring support; since C# 14 it also accepts an unbound generic type such as `nameof(List<>)`. `missing?.Capacity = 32` assigns only when `missing` is not null, and `\e` is the escape character U+001B.

Newer syntax is not inherently better. A collection expression is not universally lazy. Do not use latest or preview as an unexplained fix for a compiler error.

## Review before continuing

Run the reference and confirm it prints `csharp-046: passed`, then rerun the guide's counterexample.
