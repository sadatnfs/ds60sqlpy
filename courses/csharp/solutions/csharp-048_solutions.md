# csharp-048: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-048_solution.cs](csharp-048_solution.cs). It runs both worked examples, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Build a stable valid report:** Sorting and aggregation have independent responsibilities and both are observable. The sorted report is a=3;b=6.

**Preserve rejected data accounting:** A correct result preserves domain distinctions instead of hiding them behind a plausible total. A valid zero remains in the report while two invalid rows are counted.

## Task answers

### Task 1: Predict and explain

Trace every input to an accepted total or a rejection.

**Written answer.** Example A: `b=2`, `a=3` and `b=4` all pass validation; grouping gives `b` 6 and `a` 3, and ordinal ordering yields `a=3;b=6` with 0 rejected. Example B: `("", 2)` fails `IsNullOrWhiteSpace`, `("a", -1)` fails `Quantity < 0`, and `("b", 0)` is accepted, so the text is `b=0` with 2 rejected.

**Why it is correct.** Every row takes exactly one branch of the `if`, so the valid count plus the rejected count always equals the input count.

**Plausible wrong approach.** Assuming `("b", 0)` disappears because it adds nothing predicts text `""`. The rule rejects only negative quantities, so a zero row creates its own group.

**How to verify.** Add `Check(valid.Count + rejected == rows.Count())` inside a copy of `Report` (over a materialized array) and run both examples.

### Task 2: Guided modification

Add an item and update only independently derived expected output.

**Written answer.** Add `new Row("B", 1)` to Example A. By hand: `B` is a new group with 1, and ordinal order puts uppercase `B` (code 66) before `a` (97). The expected text is `B=1;a=3;b=6` with 0 rejected.

**Why it is correct.** The expected value is derived from the input and the rules, not from the program, so the check can catch a defect in the code.

**Plausible wrong approach.** Running the program and pasting whatever it prints into the expected string makes the test agree with the code by construction. If `OrderBy` used a case-insensitive comparer, its `a=3;b=6;B=1` would be enshrined even though the contract says ordinal.

**How to verify.** Check `report.Text == "B=1;a=3;b=6"`. Temporarily switch the comparer to `StringComparer.OrdinalIgnoreCase`: `b` and `B` then tie, the stable sort keeps `b` first, the text becomes `a=3;b=6;B=1` and the check fails.

### Task 3: Independent construction

Build the external DomainLab and expose the domain contract through the ApiLab adapter.

**Written answer.** Build DomainLab with its README commands and expect `DomainLab: seven contract checks passed`. In ApiLab.csproj add `<ProjectReference Include="../DomainLab/Domain/Domain.csproj" />` (adjusting the path to your copy) and map `POST /reports` to `Journey.Domain.Inventory.Summarize`, converting each ApiLab `Item` with `new Journey.Domain.Item(i.Name, i.Quantity)`.

**Why it is correct.** The domain library keeps the validation and aggregation rules, and the endpoint only converts HTTP input and maps the result, so the seven checks still cover the logic the API uses.

**Plausible wrong approach.** Copying the `IsNullOrWhiteSpace` and negative-quantity checks into the endpoint and passing only valid rows to `Summarize` makes `Rejected` always 0, and leaves two copies of the rule that can drift.

**How to verify.** POST `[{"id":"1","name":"pear","quantity":2},{"id":"2","name":"","quantity":9}]` to `/reports` and expect 200 with totals `pear` 2 and `rejected` 1.

### Task 4: Diagnose a defect

Introduce and diagnose a duplicate-aggregation, nullability or cancellation defect.

**Written answer.** Introduce `.Select(group => group.Key + "=" + group.First().Quantity)` in place of `group.Sum`. Example A then prints `a=3;b=2`, and the `stable report` check throws. The diagnosis: duplicate names were grouped but only the first quantity was kept.

**Why it is correct.** Example A deliberately contains `b` twice, so any aggregation that does not sum the group produces a different value for `b`.

**Plausible wrong approach.** "Fixing" duplicates with `rows.Distinct()` before reporting collapses rows that are equal by value, because `Row` is a record. `Row("b", 2)` twice becomes one row, and `b` reports 2 instead of 4.

**How to verify.** Restore `group.Sum`, then check `Report(new[] { new Row("b", 2), new Row("b", 2) }).Text == "b=4"`.

### Task 5: Boundary evidence

Document and test empty, malformed, overflow and repeated-operation boundaries.

**Written answer.** Empty: `Text == ""` and `Rejected == 0`. Malformed: `Row("  ", 1)` and `Row("a", -5)` are rejected. Overflow: `Row("x", int.MaxValue)` plus `Row("x", 1)` throws `OverflowException`, because `Enumerable.Sum` over `int` is checked. Repeated operation: calling `Report` twice on the same array gives equal tuples.

**Why it is correct.** Each boundary has a defined outcome: empty is a valid report, malformed rows are counted, overflow is a visible failure, and the function is pure, so repeating it changes nothing.

**Plausible wrong approach.** Replacing `Sum` with a manual `total += row.Quantity` loop in an unchecked context wraps to `-2147483648` and prints `x=-2147483648` as if it were a real total.

**How to verify.** Check each case, catching `OverflowException` for the overflow input, and compare two calls with `==` on the tuples.

### Task 6: Transfer and justify

Deliver a project README with build commands, architecture, failure policies, tests, operational limits and a proposed next extension.

**Written answer.** The README lists the DomainLab and ApiLab restore, build and run commands with their expected outputs, an architecture section (Domain owns rules, Checks owns examples, ApiLab owns HTTP mapping), failure policies (400 invalid, 409 duplicate id, overflow as a visible error), the tests, the limits (in-memory state lost on restart, loopback only, no authentication) and one next extension such as per-item rejection reasons.

**Why it is correct.** A reviewer can rebuild the project, rerun the evidence and see what is unsupported without reading the code first.

**Plausible wrong approach.** Documenting `dotnet test` as the test command fails the reviewer immediately: `Checks` is a console executable, not a test project, so that command never runs the seven contract checks.

**How to verify.** In a fresh copy, run every README command in order and confirm the seven-check message and the six ApiLab statuses 200, 201, 200, 409, 400 and 404.

## Mechanism and diagnostic reasoning

The final project combines validated input, a pure domain core, deterministic reporting and explicit operational outcomes. A complete application is more than a successful algorithm: it needs a documented build, input contract, failure policy, resource ownership and evidence that its output remains meaningful after changes.

The classroom reference is the portable kernel, and the DomainLab and ApiLab fixtures provide actual multi-file boundaries. Extend them deliberately rather than pasting an entire server into the single source pad. Review normal, rejected and unknown outcomes separately. Expert practice means being able to explain the limits and diagnose an unfamiliar failure, not claiming that a finite tutorial covers every production circumstance.

Compose small functions around explicit record types. Keep parsing, validation, aggregation and presentation separate. Sort output when order is part of the contract; retain rejection evidence alongside accepted totals.

Do not equate a kernel assertion with API, persistence or deployment acceptance. Retain learner data and use owned temporary state for tests. A useful capstone documents what remains intentionally unsupported.

## Review before continuing

Run the reference and confirm that it prints `csharp-048: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
