# csharp-012: explanation and comparison

Reference program: [csharp-012_solution.cs](csharp-012_solution.cs), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Copy a value:** The struct contains only integer fields, so its copied state is independently mutable. Changing the copied point leaves the original X at 2.

**Share an object identity:** Passing or assigning a reference by value does not clone the referenced object. Both references observe the same counter increment.

## Task answers

### Task 1: Predict and explain

Draw the values and references after each assignment.

**Written answer.** Example A: `first` holds the struct value X 2, Y 3. `var second = first;` copies both fields into a second value, so there are two independent points. `second.X = 9` changes only the copy: `first` is (2, 3) and `second` is (9, 3). Example B: `first` holds a reference to one `Counter` object with `Value` 0. `var second = first;` copies the reference, not the object, so both variables point at the same counter. `second.Value++` changes that object to 1, and `first.Value` reads the same 1.

**Why it is correct.** `Point` is a struct, so a variable of that type contains the data itself and assignment duplicates it. `Counter` is a class, so a variable contains a reference, and assignment duplicates only the reference. The drawing needs two boxes for A and one shared box with two arrows for B.

**Plausible wrong approach.** Drawing B like A, with two counters, predicts `first.Value == 0` and makes `ReferenceEquals(first, second)` look impossible. Drawing A like B predicts that `first.X` becomes 9.

**How to verify.** Both examples already check the result. Add `Check(!ReferenceEquals(second, new Counter()), ...)` in B and print `first.Y` and `second.Y` in A to confirm that the untouched field 3 was copied too.

### Task 2: Guided modification

Make a separate Counter instance and compare identity with equal property values.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```csharp
var first = new Counter();
first.Value = 5;
var second = new Counter();
second.Value = 5;
Check(first.Value == second.Value, "equal property values");
Check(!ReferenceEquals(first, second), "separate identities");
Check(!first.Equals(second), "class Equals defaults to identity");
second.Value++;
Check(first.Value == 5 && second.Value == 6, "independent state");
```

**Observe:** Two counters both hold 5 but are different objects; incrementing one leaves the other at 5.

`new Counter()` runs twice, so there are two objects. Their `Value` properties are equal, but `ReferenceEquals` asks whether the variables point at the same object, and they do not. `Counter` does not override `Equals`, so it inherits reference equality from `object` and also reports false. Because the objects are separate, the increment changes only `second`.

**Plausible wrong approach.** Using `first.Equals(second)` as the test for equal content gives false here and suggests the values differ. For a class without an override, `Equals` answers the identity question, not the content question.

**How to verify.** Replace `var second = new Counter();` with `var second = first;` and confirm the identity check now fails and the increment makes `first.Value` 6. Restore the second `new` afterwards.

### Task 3: Independent construction

Choose a representation for a coordinate and for a shared session, explaining the difference.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
var coordinate = new Point(1, 2);
var moved = coordinate;
moved.X = 5;
var session = new Counter();
var sameSession = session;
sameSession.Value = 3;
Check(coordinate.X == 1 && moved.X == 5, "coordinate copied by value");
Check(session.Value == 3, "session shared by reference");
```

**Observe:** Changing the copied coordinate leaves the original at 1, while both session variables see 3.

A coordinate is a small value, so the Point struct copies it; a session is shared state with one identity, so the Counter class is shared by reference.

### Task 4: Diagnose a defect

Diagnose expecting assignment of a class variable to produce a deep copy.

**Written answer.** `var backup = session; session.Value = 10;` leaves `backup.Value` at 10 as well, because `backup` is a second reference to the same `Counter`. Assigning a class variable never copies the object. To keep an independent snapshot, create a new object: `var backup = new Counter(); backup.Value = session.Value;`, or give the class an explicit copy method.

**Why it is correct.** A class variable stores a reference. Assignment copies that reference, so both names lead to one object and every mutation through either name is visible through the other. Only a constructor call or a copy method produces a second object.

**Plausible wrong approach.** Switching `Counter` to a struct to get copying changes the meaning of every other use, including the shared-session behavior Example B relies on. A shallow copy is also not enough when the class holds a mutable list, because the copy would share that list.

**How to verify.** Check `ReferenceEquals(backup, session)` is true for the faulty version and that `backup.Value` follows the change to 10. With the explicit copy, check `!ReferenceEquals(backup, session)` and that `backup.Value` keeps its old value.

### Task 5: Boundary evidence

Place a mutable list inside a struct and explain which part of the copied value remains shared.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```csharp
var original = (Count: 1, Items: new List<int> { 1 });
var copy = original;
copy.Count = 2;
copy.Items.Add(2);
Check(original.Count == 1, "value field copied");
Check(original.Items.Count == 2, "list content shared");
Check(ReferenceEquals(original.Items, copy.Items), "same list object");
```

**Observe:** The copied tuple changes its own Count to 2, but original.Items also contains two elements after the Add.

A value tuple is a struct, so assignment copies its fields. `Count` is an `int`, and its copy is independent. `Items` is a reference to a `List<int>`, and copying it copies the reference, so both tuples point at one list. Adding through `copy.Items` therefore changes the list that `original.Items` sees.

**Plausible wrong approach.** Assuming that struct semantics make the whole value immutable from the outside predicts `original.Items.Count == 1`. Value semantics apply only one level deep: the reference is copied, the list it refers to is not.

**How to verify.** Give the copy its own list with `copy.Items = new List<int>(original.Items);` before the `Add` and confirm `original.Items.Count` stays 1 and `ReferenceEquals` becomes false.

### Task 6: Transfer and justify

Design a data boundary that prevents callers from mutating an internal collection.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Mechanism and diagnostic reasoning

Value and reference semantics describe what assignment copies. A value-type assignment copies the value. A reference-type assignment copies a reference, so both variables may reach the same object. This is more useful than the misleading slogan that values always live on the stack and objects always live on the heap: storage placement depends on context, while assignment semantics remain the reasoning tool.

A class can deliberately encapsulate mutation behind operations that preserve invariants. A value object can make independent copies easier to reason about. Neither choice is automatically faster or safer. Ask whether identity matters, whether consumers should share changes, and how large or expensive copies may become.

`struct` introduces a value type; `class` introduces a reference type. Assignment has the same spelling for both, so inspect the declared type. `ReferenceEquals` asks whether references identify the same object, not whether their properties happen to match.

A struct containing a reference copies that reference, so value semantics do not imply a recursive deep copy. Equality and identity are separate questions. Avoid reasoning about correctness from presumed stack placement.

## Review before continuing

Run the reference and confirm it prints `csharp-012: passed`, then rerun the guide's counterexample.
