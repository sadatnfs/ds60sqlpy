# csharp-012: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-012_solution.cs](csharp-012_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Copy a value:** The struct contains only integer fields, so its copied state is independently mutable. Changing the copied point leaves the original X at 2.

**Share an object identity:** Passing or assigning a reference by value does not clone the referenced object. Both references observe the same counter increment.

## Task answers

### Task 1: Predict and explain

Draw the values and references after each assignment.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The struct contains only integer fields, so its copied state is independently mutable. Changing the copied point leaves the original X at 2.

### Task 2: Guided modification

Make a separate Counter instance and compare identity with equal property values.

No separate reference answer has been written for this task. Start from Example B: Passing or assigning a reference by value does not clone the referenced object. Both references observe the same counter increment.

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

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A struct containing a reference copies that reference, so value semantics do not imply a recursive deep copy. Equality and identity are separate questions. Avoid reasoning about correctness from presumed stack placement.

### Task 5: Boundary evidence

Place a mutable list inside a struct and explain which part of the copied value remains shared.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Copy a value) and Example B (Share an object identity).

### Task 6: Transfer and justify

Design a data boundary that prevents callers from mutating an internal collection.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Value semantics**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Value and reference semantics describe what assignment copies. A value-type assignment copies the value. A reference-type assignment copies a reference, so both variables may reach the same object. This is more useful than the misleading slogan that values always live on the stack and objects always live on the heap: storage placement depends on context, while assignment semantics remain the reasoning tool.

A class can deliberately encapsulate mutation behind operations that preserve invariants. A value object can make independent copies easier to reason about. Neither choice is automatically faster or safer. Ask whether identity matters, whether consumers should share changes, and how large or expensive copies may become.

`struct` introduces a value type; `class` introduces a reference type. Assignment has the same spelling for both, so inspect the declared type. `ReferenceEquals` asks whether references identify the same object, not whether their properties happen to match.

A struct containing a reference copies that reference, so value semantics do not imply a recursive deep copy. Equality and identity are separate questions. Avoid reasoning about correctness from presumed stack placement.

## Review before continuing

Run the reference and confirm that it prints `csharp-012: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
