# csharp-045: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-045_solution.cs](csharp-045_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Inspect declared metadata:** Runtime lookup needs an absence policy even when the programmer expects a member to exist. The known property is an int and the missing property is absent.

**Prefer typed access for a fixed contract:** A statically known relationship gives the compiler and deployment tools more information. The fixed projection needs no string-based member lookup.

## Task answers

### Task 1: Predict and explain

Compare compile-time and runtime checking in the two examples.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Runtime lookup needs an absence policy even when the programmer expects a member to exist. The known property is an int and the missing property is absent.

### Task 2: Guided modification

Inspect a different known property and handle absence explicitly.

No separate reference answer has been written for this task. Start from Example B: A statically known relationship gives the compiler and deployment tools more information. The fixed projection needs no string-based member lookup.

### Task 3: Independent construction

Replace string-based access in a small report with a typed projection.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
var metrics = new[] { new Metric(2), new Metric(5) };
Func<Metric, int> count = metric => metric.Count;
int total = metrics.Sum(count);
Check(total == 7, "typed projection");
```

**Observe:** The typed projection sums the counts to 7.

A Func<Metric, int> is checked by the compiler; renaming Count breaks the build instead of a reflection lookup failing at run time.

### Task 4: Diagnose a defect

Diagnose assuming dynamic reflection will remain available after trimming.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Publishing AOT does not guarantee a smaller or faster application for every workload. Never guess native memory ownership. A successful ordinary managed run does not qualify an AOT or interop path.

### Task 5: Boundary evidence

Test an absent member and an unexpected member type.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Inspect declared metadata) and Example B (Prefer typed access for a fixed contract).

### Task 6: Transfer and justify

Plan an external Native AOT experiment stating target architecture, native prerequisites and runtime checks.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Reflection**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Reflection inspects types and members at runtime. It is useful for tooling and frameworks, but unrestricted dynamic discovery makes deployment analysis harder. Trimming removes code that appears unused, and ahead-of-time compilation moves work from startup to build. Reflection-heavy paths may need annotations, generated metadata or a different design.

Calling native code adds an ABI boundary: layout, calling convention, string encoding, allocation ownership and error reporting must agree. This route deliberately avoids unsafe native calls in its ordinary pad. The portable examples compare reflection with explicit typed access; an external Native AOT publish remains a separate platform-specific build exercise.

`typeof(T)` gets type metadata; GetProperty returns a possibly absent member. Typed access is checked at compile time. Native AOT uses a publish property and platform toolchain requirements rather than a magic source keyword.

Publishing AOT does not guarantee a smaller or faster application for every workload. Never guess native memory ownership. A successful ordinary managed run does not qualify an AOT or interop path.

## Review before continuing

Run the reference and confirm that it prints `csharp-045: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
