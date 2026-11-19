# csharp-013: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-013_solution.cs](csharp-013_solution.cs). It runs both worked examples, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Preserve a nonnegative balance:** Validate affordability before subtraction so rejected requests cannot corrupt state. Spending 4 succeeds; spending 7 afterward fails without changing 6.

**Reject malformed operations:** These are separate boundary policies. Both preserve the invariant, but they communicate different meanings to the caller. Negative spending is rejected and zero is an accepted no-op.

## Task answers

### Task 1: Predict and explain

Trace the wallet state through successful and rejected spending.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Validate affordability before subtraction so rejected requests cannot corrupt state. Spending 4 succeeds; spending 7 afterward fails without changing 6.

### Task 2: Guided modification

Add a validated deposit operation.

No separate reference answer has been written for this task. Start from Example B: These are separate boundary policies. Both preserve the invariant, but they communicate different meanings to the caller. Negative spending is rejected and zero is an accepted no-op.

### Task 3: Independent construction

Implement a bounded inventory whose reservations never make stock negative.

No reference answer has been written for this task yet. It needs a project or platform outside the single-file pad, so record your own build and run evidence and judge it against the vocabulary entry **Invariant** and the lesson notes.

### Task 4: Diagnose a defect

Diagnose subtracting before checking affordability.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Private fields alone do not establish a correct contract. A partially mutated object after failure can poison later operations. This class is intentionally single-threaded; encapsulation does not itself provide synchronization.

### Task 5: Boundary evidence

Test exactly the available amount, zero and a negative request.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Preserve a nonnegative balance) and Example B (Reject malformed operations).

### Task 6: Transfer and justify

Explain whether a shared wallet needs synchronization when several tasks may spend concurrently.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Invariant**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A class can protect a state transition by admitting changes only through reviewed operations. A constructor establishes the initial invariant; methods preserve it. Private setters are useful only when the public operations actually enforce the domain rule. A property named Balance that any caller can replace with a negative number has no meaningful protection.

Model expected rejection distinctly from programming defects. A withdrawal larger than the available balance can be a normal false result. A negative withdrawal is malformed input and may merit an argument exception. State should remain unchanged on rejected operations. This failure atomicity is often more important than a compact implementation.

A constructor has the class name and no return type. `private set` permits mutation inside the class. `sealed` prevents inheritance when extension is not part of the design. Guard clauses reject invalid inputs before state changes.

Private fields alone do not establish a correct contract. A partially mutated object after failure can poison later operations. This class is intentionally single-threaded; encapsulation does not itself provide synchronization.

## Review before continuing

Run the reference and confirm that it prints `csharp-013: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
