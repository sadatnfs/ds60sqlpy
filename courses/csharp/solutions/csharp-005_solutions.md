# csharp-005: explanation and comparison

Reference program: [csharp-005_solution.cs](csharp-005_solution.cs), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**A guard prevents unsafe access:** The left operand establishes the precondition needed by the right operand. The missing value is handled without dereferencing null.

**Classify a threshold:** Ordered relational patterns make the inclusive boundary visible and preserve the invalid-input category. 59 retries, 60 passes, and 101 is rejected.

## Task answers

### Task 1: Predict and explain

Trace which operands execute when label is null.

**Written answer.** With `label` null, `label != null` is false, so `&&` returns false without evaluating `label.Length > 0`, and the outer `!` turns that into true for the `guarded access` check. After `label = "ok"` both operands run: the null test is true and `Length == 2` is true.

**Why it is correct.** C# evaluates the right operand of `x && y` only when `x` is true. The dereference therefore sits behind a precondition that has already been proved, and the null case never reaches `.Length`.

**Plausible wrong approach.** Distributing the negation by hand as `!(label != null) && label.Length > 0` looks equivalent but is not. When `label` is null the left side is true, so `label.Length` runs and throws `NullReferenceException`, which is the exact access the original parentheses prevent.

**How to verify.** Replace the right operand with a helper such as `bool Longer(string s) { Console.WriteLine("read Length"); return s.Length > 0; }`. With the null label nothing is printed; with `"ok"` the line appears once, and both checks stay silent before the lesson marker.

### Task 2: Guided modification

Change the classifier pass threshold to 70 and update boundary checks.

**Written answer.** Change only the retry arm to `< 70 => "retry"` and move the boundary checks with it: `Classify(69) == "retry"`, `Classify(70) == "pass"`, and keep `Classify(101) == "invalid"`. Arm order stays `< 0`, `< 70`, `<= 100`, `_`.

**Why it is correct.** A switch expression takes the first arm whose pattern matches. 69 matches `< 70` first, while 70 fails it and lands in `<= 100`, so 70 is the inclusive pass boundary and the invalid categories at both ends are untouched.

**Plausible wrong approach.** Writing `<= 70 => "retry"` moves the boundary one value too far: `Classify(70)` returns `retry` and the at-boundary check throws. Updating only the checks to 69 and 70 while leaving `< 60` fails the other way, because 69 then passes.

**How to verify.** A failing `Check` throws `InvalidOperationException` carrying its reason, so an off-by-one version stops at `at boundary`. The corrected classifier lets all three checks pass silently and the run ends with `csharp-005: passed`.

### Task 3: Independent construction

Write a classifier for negative, zero and positive temperatures.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
string Temperature(int celsius) {
  if (celsius < 0) {
    return "below zero";
  }
  if (celsius == 0) {
    return "zero";
  }
  return "above zero";
}
Check(Temperature(-5) == "below zero", "negative");
Check(Temperature(0) == "zero", "zero");
Check(Temperature(12) == "above zero", "positive");
```

**Observe:** -5, 0 and 12 are classified as below zero, zero and above zero.

The three branches cover every int exactly once, and zero is tested on its own instead of being folded into either side.

**Plausible wrong approach.** A two-way ternary `celsius <= 0 ? "below zero" : "above zero"` folds zero into the negative side. `Temperature(0)` then returns `below zero` and the `zero` check throws, which is why zero has its own branch.

**How to verify.** The `Task 3` block checks -5, 0 and 12. Extra probes at `int.MinValue` and `int.MaxValue` should return `below zero` and `above zero`, showing the three branches cover the whole `int` range.

### Task 4: Diagnose a defect

Find why replacing && with & can break a null guard.

**Written answer.** For `bool` operands `&` is the non-conditional logical AND: it evaluates both sides before combining them. In `label != null & label.Length > 0` with a null label, `label.Length` still runs and throws `NullReferenceException`, so the guard guards nothing.

**Why it is correct.** Only `&&` and `||` are conditional operators. `&` and `|` always evaluate both operands, which is useful when the right side has a required effect but wrong when it depends on the left side being true.

**Plausible wrong approach.** Treating it as a precedence problem and writing `(label != null) & (label.Length > 0)` changes nothing. The parentheses already matched the intent; the defect is evaluation order, and only restoring `&&` fixes it.

**How to verify.** Run the `&` version with `label = null`: execution stops with `NullReferenceException` before the `guarded access` check reports anything. Restore `&&` and the same fixture passes silently.

### Task 5: Boundary evidence

Test the two ends of the valid score range and one value beyond each end.

**Written answer.** The valid domain is 0 through 100. Check `Classify(-1) == "invalid"`, `Classify(0) == "retry"`, `Classify(100) == "pass"` and `Classify(101) == "invalid"`: one value on each side of each edge.

**Why it is correct.** The arms `< 0` and `<= 100` define both edges. These four inputs are the smallest set that separates an inclusive edge from an exclusive one at each end, which a middle score such as 75 cannot do.

**Plausible wrong approach.** Testing only 50 and 101 passes a classifier that says `< 100 => "pass"`, where 100 falls through to `invalid`, and one that rejects 0 with `<= 0 => "invalid"`. Both wrong edges survive because neither test touches them.

**How to verify.** Mutate `<= 100` to `< 100` temporarily; the `Classify(100)` check must throw. Mutate `< 0` to `<= 0`; the `Classify(0)` check must throw. Restore both and all four pass.

### Task 6: Transfer and justify

Choose a routing policy with three mutually exclusive outcomes and explain how invalid values are represented.

**Written answer.** Route a ticket priority of 1, 2 or 3 to an `enum Route { Page, Queue, Backlog }` with `priority switch { 1 => Route.Page, 2 => Route.Queue, 3 => Route.Backlog, _ => throw new ArgumentOutOfRangeException(nameof(priority)) }`. Invalid input is a rejection, not a fourth route.

**Why it is correct.** The three constant patterns are disjoint, so each valid priority matches exactly one arm. Keeping invalid values out of the enum means no caller can confuse a rejected ticket with a low-priority one. A limitation is that callers must handle the exception, or the policy must return a separate result type instead.

**Plausible wrong approach.** Using `_ => Route.Backlog` as the fallback is compact but sends priority 0 or 7 to the backlog as if it were valid. That is the lesson's pitfall of an else branch classifying every invalid value as valid.

**How to verify.** Check 1, 2 and 3 map to `Page`, `Queue` and `Backlog`, then call it with 0 and 4 inside `try` blocks and `Check` that `ArgumentOutOfRangeException` was caught each time.

## Mechanism and diagnostic reasoning

A branch chooses one path based on a Boolean expression. Good branches expose the domain distinction, not just a compact operator chain. Short-circuit operators evaluate their right side only when needed, which lets a guard protect a later operation. This is a control-flow property, not merely a performance optimization.

For mutually exclusive categories, put the cases in an order that matches the domain and include a policy for values outside the range. A boundary such as zero should have a deliberate meaning. Testing values just below, exactly at and just above a threshold detects mistakes that a typical middle value will miss.

`&&` requires both conditions and stops after false; `||` stops after true. A switch expression returns one value from its matching arm. The discard pattern `_` can provide an explicit fallback but must not conceal invalid input.

An else branch can accidentally classify every invalid value as valid. Test domain validity independently from success thresholds. Do not use a fallback to hide an impossible state without explaining recovery.

## Review before continuing

Run the reference and confirm it prints `csharp-005: passed`, then rerun the guide's counterexample.
