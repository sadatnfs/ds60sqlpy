# csharp-045: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-045_solution.cs](csharp-045_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Inspect declared metadata:** Runtime lookup needs an absence policy even when the programmer expects a member to exist. The known property is an int and the missing property is absent.

**Prefer typed access for a fixed contract:** A statically known relationship gives the compiler and deployment tools more information. The fixed projection needs no string-based member lookup.

## Task answers

### Task 1: Predict and explain

Compare compile-time and runtime checking in the two examples.

**Written answer.** Example A checks at run time: `GetProperty` returns `PropertyInfo?`, and `GetProperty("Missing")` compiles but returns null. `nameof(Metric.Count)` is the only compile-time check there. Example B is checked entirely by the compiler: `value.Count` must exist and be an `int`, or `Func<Metric, int>` does not compile.

**Why it is correct.** A string member name is opaque to the compiler, while a lambda member access is resolved during compilation, so typos and type changes become build errors.

**Plausible wrong approach.** Assuming `nameof` makes the reflection lookup safe overlooks that it only checks the name at build time. The result is still nullable, and trimming or a renamed member reached through a different string can still produce null at run time.

**How to verify.** Change Example B to `value.Cont` and the build fails with CS1061. Change Example A to `GetProperty("Cont")` and it compiles, then the `known metadata` check throws.

### Task 2: Guided modification

Inspect a different known property and handle absence explicitly.

**Written answer.** Inspect `typeof(string).GetProperty(nameof(string.Length))`; its `PropertyType` is `typeof(int)`, and `GetValue("pear")` returns 4. For absence, `if (typeof(string).GetProperty("Size") is not { } size)` reports `Size missing` instead of dereferencing.

**Why it is correct.** The pattern `is not { } size` both tests for null and binds the non-null value, so the code that reads the property runs only when it exists.

**Plausible wrong approach.** Writing `typeof(string).GetProperty("Size")!.GetValue("pear")` silences the nullable warning with `!`, and the missing property becomes a `NullReferenceException` at run time.

**How to verify.** Check `typeof(string).GetProperty("Length")?.PropertyType == typeof(int)`, that `GetProperty("Size")` is null, and that `typeof(Metric).GetProperties().Length == 1`, because the record's synthesized `EqualityContract` property is protected.

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

**Plausible wrong approach.** The string version `metrics.Sum(m => (int)typeof(Metric).GetProperty("count")!.GetValue(m)!)` compiles, but `GetProperty` is case-sensitive by default. It returns null for `"count"`, and the `!` turns that into a `NullReferenceException` at run time.

**How to verify.** The block checks the total is 7. Add `new Metric(0)` and expect 7 again; rename `Count` to `Total` in the record and the build fails at `metric.Count`, which is the point of the typed projection.

### Task 4: Diagnose a defect

Diagnose assuming dynamic reflection will remain available after trimming.

**Written answer.** Reading a type name and property name from configuration and calling `Type.GetType(typeName)?.GetProperty(propertyName)` works in a normal run. With `-p:PublishTrimmed=true`, the trimmer cannot see which members those strings name, so it may remove them and the calls return null. Annotate the parameter with `[DynamicallyAccessedMembers(DynamicallyAccessedMemberTypes.PublicProperties)]` or replace the lookup with a typed projection.

**Why it is correct.** Trimming keeps only what static analysis proves is used. `typeof(Metric).GetProperty(nameof(Metric.Count))` uses constants it can follow, but names from configuration are unknown at publish time.

**Plausible wrong approach.** Suppressing the trim analysis warnings (IL2xxx) with `<NoWarn>` or `[UnconditionalSuppressMessage]` makes the publish look clean while the members are still removed, so the failure appears in production instead of at publish time.

**How to verify.** Run `dotnet publish -c Release -r linux-x64 -p:PublishTrimmed=true` in a separate project and read the trim warnings. Run the trimmed output and check that the configured lookup is not null.

### Task 5: Boundary evidence

Test an absent member and an unexpected member type.

**Written answer.** Write `int? ReadInt(object target, string name)`: return null when `GetProperty(name)` is null or when `PropertyType != typeof(int)`, otherwise return `(int)property.GetValue(target)!`. Test with `Metric(4)` and `"Count"`, with `"Missing"`, and with `record Wide(long Count)`.

**Why it is correct.** Checking `PropertyType` before unboxing turns both kinds of surprise, an absent member and a member of another type, into one explicit policy result.

**Plausible wrong approach.** Unboxing without the type check, `(int)property.GetValue(target)!`, throws `InvalidCastException` for `Wide(5)`, because a boxed `long` can be unboxed only as `long`, even though 5 fits in an `int`.

**How to verify.** Check `ReadInt(new Metric(4), "Count") == 4`, `ReadInt(new Metric(4), "Missing") is null` and `ReadInt(new Wide(5), "Count") is null`.

### Task 6: Transfer and justify

Plan an external Native AOT experiment stating target architecture, native prerequisites and runtime checks.

**Written answer.** Target `linux-x64`, built on a Linux x64 host with `clang` and the zlib development package installed. Publish with `dotnet publish -c Release -r linux-x64 -p:PublishAot=true`. Runtime checks: the native binary prints the same `csharp-045: passed` marker as the managed run, the publish reports no unreviewed AOT or trim warnings, and startup time and file size are compared with a framework-dependent publish.

**Why it is correct.** Native AOT compiles ahead of time for one operating system and architecture and needs the platform linker, so the plan must name both and compare behavior, not only build success.

**Plausible wrong approach.** Publishing from macOS with `-r linux-x64 -p:PublishAot=true` and expecting a Linux binary fails, because Native AOT does not support cross-OS compilation. The experiment has to run on the target OS or in a matching container.

**How to verify.** `file` on the output reports an ELF 64-bit x86-64 executable, running it prints the pass marker, and the publish log shows zero warnings.

## Mechanism and diagnostic reasoning

Reflection inspects types and members at runtime. It is useful for tooling and frameworks, but unrestricted dynamic discovery makes deployment analysis harder. Trimming removes code that appears unused, and ahead-of-time compilation moves work from startup to build. Reflection-heavy paths may need annotations, generated metadata or a different design.

Calling native code adds an ABI boundary: layout, calling convention, string encoding, allocation ownership and error reporting must agree. This route deliberately avoids unsafe native calls in its ordinary pad. The portable examples compare reflection with explicit typed access; an external Native AOT publish remains a separate platform-specific build exercise.

`typeof(T)` gets type metadata; GetProperty returns a possibly absent member. Typed access is checked at compile time. Native AOT uses a publish property and platform toolchain requirements rather than a magic source keyword.

Publishing AOT does not guarantee a smaller or faster application for every workload. Never guess native memory ownership. A successful ordinary managed run does not qualify an AOT or interop path.

## Review before continuing

Run the reference and confirm that it prints `csharp-045: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
