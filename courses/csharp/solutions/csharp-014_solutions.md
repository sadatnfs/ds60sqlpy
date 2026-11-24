# csharp-014: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-014_solution.cs](csharp-014_solution.cs). It runs both worked examples, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Equal data with distinct identities:** Value equality and reference identity answer different questions. Equal records can be distinct objects; with preserves the previous age.

**Notice nested shared state:** The record copy duplicates its field values, including the list reference. Generated copying is not a deep-clone promise. Both records see the appended list item.

## Task answers

### Task 1: Predict and explain

Predict record equality and reference equality separately.

**Written answer.** `first == second` is true because the record compares `Name` and `Age`, both `"Ada"` and 30. `ReferenceEquals(first, second)` is false because two `new` expressions created two objects.

**Why it is correct.** A record class synthesizes `Equals`, `==` and `GetHashCode` over its declared members, while `ReferenceEquals` always compares object identity and cannot be overridden.

**Plausible wrong approach.** Assuming `==` on a reference type always means identity predicts false here. That holds for ordinary classes but not for records, whose synthesized operator compares data.

**How to verify.** Add `var third = first; Check(ReferenceEquals(first, third) && first == third, "same object");` beside the two Example A checks and confirm all three pass.

### Task 2: Guided modification

Create a changed copy with a new name and retain the original.

**Written answer.** Write `var renamed = first with { Name = "Grace" };` and check `first.Name == "Ada"`, `renamed.Name == "Grace"`, `renamed.Age == 30` and `renamed != first`.

**Why it is correct.** `with` calls the record copy constructor and then sets only the listed members, so `Age` carries over and the original object is not touched.

**Plausible wrong approach.** Trying `first.Name = "Grace"` fails to compile, because positional record properties are `init`-only. Declaring a mutable `Name { get; set; }` to make it compile would change the original in place and lose the earlier value.

**How to verify.** Run the four checks; all pass silently. Also check `(renamed with { Name = "Ada" }) == first` to show equality is decided by data, not by how the instance was produced.

### Task 3: Independent construction

Design an immutable coordinate using a readonly record struct.

**Written answer.** Declare `public readonly record struct Point(int X, int Y);`. Use `var a = new Point(1, 2); var b = a with { X = 5 };` and check `a.X == 1`, `b.X == 5`, `b.Y == 2` and `new Point(1, 2) == a`.

**Why it is correct.** A record struct is a value type, so assignment copies the data, and `readonly` makes the generated properties `init`-only. No alias can change a stored point.

**Plausible wrong approach.** A plain `record struct Point(int X, int Y)` without `readonly` gets settable properties, so `a.X = 9` compiles and the coordinate is no longer immutable even though it is still compared by value.

**How to verify.** Check the four results, then add `a.X = 9;` and confirm the compiler rejects it because `X` is init-only. Remove that line and check `var c = a; c = c with { Y = 7 };` leaves `a.Y == 2`, since each struct variable holds its own copy.

### Task 4: Diagnose a defect

Diagnose a supposedly immutable history entry containing a mutable list.

**Written answer.** `record Entry(string Label, List<int> Values)` looks immutable, but `entry.Values.Add(4)` changes the list that every copy made with `with` also holds. Store `IReadOnlyList<int>` built from `values.ToArray()` or an `ImmutableList<int>` in the constructor.

**Why it is correct.** The positional properties are `init`-only, which protects the reference, not the object it points to. Copying the input into a new read-only collection breaks the link to the caller's list.

**Plausible wrong approach.** Changing only the property type to `IReadOnlyList<int>` while storing the caller's `List<int>` still shares it. The caller can keep adding to the original list and the history entry changes with it.

**How to verify.** Build `var source = new List<int> { 1, 2 }; var entry = new Entry("a", source); source.Add(3);` and check `entry.Values.Count == 2` and `!ReferenceEquals(entry.Values, source)`. Without the copy the count is 3 and the first check throws.

### Task 5: Boundary evidence

Compare records whose nested collections contain equal values but have different identities.

**Written answer.** Build `var a = new Basket(new List<int> { 1, 2 }); var b = new Basket(new List<int> { 1, 2 });`. `a == b` is false even though the lists hold the same numbers; `a.Items.SequenceEqual(b.Items)` is true.

**Why it is correct.** The synthesized equality calls `EqualityComparer<List<int>>.Default`, which for `List<int>` is reference equality. Two distinct lists are unequal regardless of contents.

**Plausible wrong approach.** Expecting `a == b` to be true because records have value equality assumes the comparison is recursive. It compares each member with that member type's own equality, and `List<T>` does not override it.

**How to verify.** Check `!(a == b)` and `a.Items.SequenceEqual(b.Items)`. Then make `b` with `a with { }` and check `a == b` is true because both now hold the same list reference.

### Task 6: Transfer and justify

Choose identity-based or data-based equality for an order and explain how updates affect collection membership.

**Written answer.** Give an order identity-based equality on a stable `OrderId`, not on all of its data. Its status and lines change after creation, and a `HashSet<Order>` keyed on every field would lose track of an order once it was updated.

**Why it is correct.** Hash-based collections place an item using the hash at insertion. If the hash comes from mutable data, updating the order moves its correct bucket and `Contains` returns false. A fixed ID keeps the hash stable. The cost is that two orders with identical contents are still different orders.

**Plausible wrong approach.** Declaring `record Order(int OrderId, string Status)` and replacing it with `order with { Status = "Shipped" }` creates a new value that is unequal to the stored one, so the set now holds the stale order and `Contains(updated)` is false.

**How to verify.** Insert an order into a `HashSet`, produce the shipped version, and check `Contains`. With equality on `OrderId` only, it is true; with full record equality, it is false.

## Mechanism and diagnostic reasoning

Records describe data with synthesized equality and convenient copying. A record class still has reference identity, but its equality normally compares declared data members. A record struct is a value type. These features reduce boilerplate; they do not automatically make nested objects immutable or define the correct business identity.

A with expression constructs a copy with selected changes. That copy is shallow for referenced members. When a record contains a mutable list, two record instances may still share that list. Use immutable representations or deliberate copying when independent history is required. Choose equality fields from the domain rather than accepting every field merely because generation is convenient.

`record Person(string Name, int Age)` declares positional properties and value-based equality. `record struct` changes assignment semantics. `with { Age = 31 }` creates a changed copy. `==` on records follows generated value equality.

Record equality does not recursively compare arbitrary collection contents. A positional record can still contain mutable members. Avoid putting fields that change after insertion into a hash key contract.

## Review before continuing

Run the reference and confirm that it prints `csharp-014: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
