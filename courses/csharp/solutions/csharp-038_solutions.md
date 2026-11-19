# csharp-038: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-038_solution.cs](csharp-038_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Validate a bounded identifier:** Whole-input anchors prevent a valid substring from disguising an invalid full value. The identifier begins with a lowercase letter and uses only admitted characters.

**Keep literal user text literal:** Escaping preserves data meaning instead of accidentally granting regex syntax authority. The plus sign is matched literally.

## Task answers

### Task 1: Predict and explain

Explain every part of the identifier pattern.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Whole-input anchors prevent a valid substring from disguising an invalid full value. The identifier begins with a lowercase letter and uses only admitted characters.

### Task 2: Guided modification

Change the maximum identifier length and test the exact boundary.

No separate reference answer has been written for this task. Start from Example B: Escaping preserves data meaning instead of accidentally granting regex syntax authority. The plus sign is matched literally.

### Task 3: Independent construction

Validate a structured identifier and then check its domain-specific reserved words.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
var options = RegexOptions.NonBacktracking;
var limit = TimeSpan.FromSeconds(1);
var shape = new Regex(@"\A[a-z][a-z0-9_]{0,15}\z", options, limit);
var reserved = new HashSet<string>(StringComparer.Ordinal) { "admin" };
bool Valid(string id) => shape.IsMatch(id) && !reserved.Contains(id);
Check(Valid("report_2"), "accepted");
Check(!Valid("admin"), "reserved word rejected");
Check(!Valid("2report"), "shape rejected");
```

**Observe:** report_2 is accepted; admin and 2report are rejected for different reasons.

The regular expression checks only the shape; the reserved-word rule is a separate domain check applied afterward.

### Task 4: Diagnose a defect

Diagnose matching a valid substring inside an invalid full input.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A timeout is a fallback, not a substitute for a simple pattern and bounded input. Regex does not make a path, SQL query or HTML context safe. Validate according to the destination meaning.

### Task 5: Boundary evidence

Test newline, empty input and one character beyond the limit.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Validate a bounded identifier) and Example B (Keep literal user text literal).

### Task 6: Transfer and justify

Choose a parser or regex for a nested format and justify complexity and error reporting.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Syntax validation**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Validation defines what an input means and which representations are accepted. A regular expression can recognize a textual shape, but it does not enforce every semantic rule. A date-shaped string can still name an impossible date. Keep size, syntax and domain validation as separate steps.

Backtracking expressions can require excessive work on adversarial inputs. Use a bounded input length, a timeout and an appropriate engine mode. Prefer simple parsers when they make the contract clearer. Never construct a regex from untrusted text without deciding whether that text is literal or syntax.

`RegexOptions.NonBacktracking` supports a bounded engine for compatible patterns. Anchors constrain the entire input. Regex.Escape treats input as literal pattern text. Domain validation follows a successful shape match.

A timeout is a fallback, not a substitute for a simple pattern and bounded input. Regex does not make a path, SQL query or HTML context safe. Validate according to the destination meaning.

## Review before continuing

Run the reference and confirm that it prints `csharp-038: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
