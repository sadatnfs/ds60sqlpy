# csharp-015: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-015_solution.cs](csharp-015_solution.cs). It runs both worked examples, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Narrow before using a value:** The bound number is available only after the type pattern succeeds. The same method distinguishes type, value range and string shape.

**Represent results without impossible combinations:** Separate cases prevent a Boolean success flag from disagreeing with unrelated optional fields. Success carries a count; failure carries a reason.

## Task answers

### Task 1: Predict and explain

Predict the matched arm for zero, positive integer, empty text and nonempty text.

**Written answer.** For `Describe(0)` the first arm needs `number > 0`, so it falls to `int => "nonpositive"`. `Describe(12)` matches the first arm, `positive`. `Describe("")` reaches `string { Length: 0 }`, `empty`. `Describe("hi")` matches no specific arm and gets `other`.

**Why it is correct.** Arms are tried top to bottom, and an arm matches only when its type pattern and any property pattern or `when` guard all succeed. A failed guard moves evaluation to the next arm instead of stopping.

**Plausible wrong approach.** Predicting an exception for `"hi"` because no string arm covers it ignores the `_` discard, which matches every remaining value. Predicting `positive` for 0 forgets that the guard is strictly greater than zero.

**How to verify.** Add checks for `Describe(0) == "nonpositive"` and `Describe("hi") == "other"` to the two Example A checks; all pass.

### Task 2: Guided modification

Add a nonempty string arm without shadowing the empty case.

**Written answer.** Insert `string { Length: > 0 } => "text"` after the `string { Length: 0 }` arm and before `_`. Check `Describe("") == "empty"` and `Describe("hi") == "text"`.

**Why it is correct.** The new property pattern matches only strings with at least one character, so it does not overlap the empty arm, and placing it before the discard keeps the discard for non-string values such as `3.5`.

**Plausible wrong approach.** Adding a bare `string => "text"` above the empty arm matches every string first, so `""` returns `text`. The compiler reports the empty arm as unreachable (CS8510), which is exactly the shadowing to avoid.

**How to verify.** Check `""`, `"hi"` and `3.5` give `empty`, `text` and `other`. Swap the two string arms temporarily and confirm the build fails with the unreachable-arm error.

### Task 3: Independent construction

Model a loading, ready and failed operation with separate payloads.

**Written answer.** Declare `abstract record Op; sealed record Loading : Op; sealed record Ready(string Data) : Op; sealed record Failed(string Error) : Op;` and render with `op switch { Loading => "loading", Ready(var d) => $"ready:{d}", Failed(var e) => $"failed:{e}", _ => throw new InvalidOperationException("unknown state") }`.

**Why it is correct.** Each state carries only its own payload, so a loading operation cannot have data and a ready one cannot have an error. Positional deconstruction gives each arm a nonnullable value to use.

**Plausible wrong approach.** A single `record Op(bool Loading, string? Data, string? Error)` allows `Loading = true` with `Data` set, or both `Data` and `Error` null when not loading. Every consumer must then guess which field wins.

**How to verify.** Check `new Loading()` renders `loading`, `new Ready("rows")` renders `ready:rows` and `new Failed("timeout")` renders `failed:timeout`.

### Task 4: Diagnose a defect

Diagnose a broad object arm placed before a more specific case.

**Written answer.** In `item switch { object => "other", int number when number > 0 => "positive", ... }` the first arm matches every non-null value, so later arms never run. Move `object` (or `_`) to the end.

**Why it is correct.** Switch expressions choose the first matching arm. Since every type converts to `object`, that arm subsumes the rest, and the compiler reports the later arms as unreachable with error CS8510.

**Plausible wrong approach.** Keeping the broad arm first and adding `when item is not int` to it hides the error but duplicates the type tests by hand. Each new specific arm then needs another exclusion in the guard.

**How to verify.** Compile the broken order and observe CS8510 on the `int` arm. After moving `object` last, `Describe(12) == "positive"` passes.

### Task 5: Boundary evidence

Test an unexpected subclass and explain the fallback policy.

**Written answer.** Add `sealed record Pending : Result;` without updating `Render`. `Render(new Pending())` reaches `_ => throw new InvalidOperationException("unknown result")`, and a test should expect exactly that exception.

**Why it is correct.** The C# compiler does not know that `Result` has only `Success` and `Failure`, because any code may derive another subclass. Throwing on the discard makes a forgotten case loud rather than silently rendered as success.

**Plausible wrong approach.** Making the fallback `_ => "count:0"` keeps the program running but reports a pending result as success with zero items, the pitfall of a default branch hiding a new state.

**How to verify.** Wrap `Render(new Pending())` in `try` and catch `InvalidOperationException`, checking its `Message` is `unknown result`. Success and failure still render as before.

### Task 6: Transfer and justify

Replace several loosely related flags in a program with explicit states and justify which impossible combinations disappear.

**Written answer.** Replace `bool isConnected, isConnecting; string? error;` with records `Disconnected`, `Connecting(int Attempt)`, `Connected(string Session)` and `Lost(string Error)`. The flag combination `isConnected && isConnecting` and an `error` while connected can no longer be expressed.

**Why it is correct.** With three independent flags there are 8 combinations, of which only 4 are meaningful. Four exclusive records describe exactly the meaningful ones, so code cannot build the other 4. The limitation is that a new state forces every switch to be reviewed.

**Plausible wrong approach.** Keeping the flags and adding an enum `ConnectionState` alongside them leaves two sources of truth. A bug can set the enum to `Connected` while `error` is still set.

**How to verify.** Write a `Describe` switch over the four records and check one value of each, such as `new Connecting(2)` giving `connecting:2`. `Connected` takes only a session string, so a connected state carrying an error cannot be written at all.

## Mechanism and diagnostic reasoning

Pattern matching combines a test with structured access to the matched data. It can replace a chain of unsafe casts with branches that make the valid shape visible. Patterns are especially useful when a finite set of domain states carries different information, such as loading, success and failure. The goal is a truthful state model, not clever syntax.

A fallback branch should have a deliberate meaning. If a new domain state is introduced later, silently treating it as success is dangerous. C# class hierarchies are not fully closed algebraic data types, so review exhaustiveness and reject unexpected cases explicitly when necessary. Keep missing information distinct from failure information.

`value is int number` tests and binds. Property patterns inspect named properties. A switch expression can select an expression by type and guard. `when` adds a condition after the structural match.

An early broad pattern can make a later case unreachable. A default branch can hide a newly added state. Pattern matching is not a substitute for validating external data.

## Review before continuing

Run the reference and confirm that it prints `csharp-015: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
