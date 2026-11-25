# csharp-038: explanation and comparison

Reference program: [csharp-038_solution.cs](csharp-038_solution.cs), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Validate a bounded identifier:** Whole-input anchors prevent a valid substring from disguising an invalid full value. The identifier begins with a lowercase letter and uses only admitted characters.

**Keep literal user text literal:** Escaping preserves data meaning instead of accidentally granting regex syntax authority. The plus sign is matched literally.

## Task answers

### Task 1: Predict and explain

Explain every part of the identifier pattern.

**Written answer.** `\A` anchors at the start of the input. `[a-z]` requires one lowercase ASCII letter first. `[a-z0-9_]{0,15}` allows up to 15 more letters, digits or underscores. `\z` anchors at the absolute end. Total length is 1 to 16. `NonBacktracking` gives linear-time matching, and the one-second timeout is a final guard.

**Why it is correct.** With both anchors, the whole input must match the pattern, so no prefix or suffix outside the allowed characters can slip through.

**Plausible wrong approach.** Using `$` instead of `\z` looks equivalent, but `$` also matches before a final newline, so `"report\n"` would be accepted with a trailing line break.

**How to verify.** Check `IsMatch("a")`, a 16-character identifier accepted, a 17-character one rejected, and `"report\n"` rejected.

### Task 2: Guided modification

Change the maximum identifier length and test the exact boundary.

**Written answer.** For a maximum of 8 characters, change the quantifier to `{0,7}`. Check `"abcdefgh"` (8) is accepted and `"abcdefghi"` (9) is rejected.

**Why it is correct.** The first letter is matched by `[a-z]` outside the quantifier, so the quantifier's maximum is one less than the total.

**Plausible wrong approach.** Writing `{0,8}` for an 8-character maximum allows 9 characters, an off-by-one that a test using only short names never sees.

**How to verify.** Check both boundary values with the new pattern, then temporarily use `{0,8}` and confirm the 9-character check throws.

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

**Plausible wrong approach.** Folding the reserved word into the pattern with a lookahead, `\A(?!admin\z)[a-z]...`, fails at construction: `RegexOptions.NonBacktracking` does not support lookarounds and throws `NotSupportedException`.

**How to verify.** The block checks `report_2`, `admin` and `2report`. Add `!Valid("Admin")`, rejected by shape, and `Valid("admin2")`, accepted because the reserved check is an exact ordinal match; decide whether prefixes should also be reserved.

### Task 4: Diagnose a defect

Diagnose matching a valid substring inside an invalid full input.

**Written answer.** Without anchors, `[a-z][a-z0-9_]{0,15}` finds `report` inside `"report!"` and inside `"2report"`, so `IsMatch` returns true for both. Add `\A` and `\z` so the whole input must match.

**Why it is correct.** `IsMatch` searches for a match anywhere in the input unless the pattern pins the start and end.

**Plausible wrong approach.** Adding only the start anchor, `\A[a-z][a-z0-9_]{0,15}`, rejects `"2report"` but still accepts `"report!"`, because the trailing `!` is never examined.

**How to verify.** With the unanchored pattern, the Example A `rejected shapes` check throws. With both anchors it passes.

### Task 5: Boundary evidence

Test newline, empty input and one character beyond the limit.

**Written answer.** Check `"report\n"` is rejected, `""` is rejected because one letter is required, `"a" + new string('b', 15)` (16 characters) is accepted and `"a" + new string('b', 16)` (17 characters) is rejected.

**Why it is correct.** `\z` refuses the trailing newline, the leading `[a-z]` refuses empty input, and the quantifier caps the length at 16.

**Plausible wrong approach.** Calling `input.Trim()` before validation accepts `"report\n"`, but if the original string is then stored, the saved identifier still contains the newline that validation never saw.

**How to verify.** Run the four checks; all pass silently. Replace `\z` with `$` and confirm the newline check now throws.

### Task 6: Transfer and justify

Choose a parser or regex for a nested format and justify complexity and error reporting.

**Written answer.** For a nested format such as `(a,(b,c))`, write a small recursive descent parser with a depth limit. It can report errors such as `expected ')' at position 7`, and the depth limit bounds the work.

**Why it is correct.** Matching nesting needs counting, which a regular expression cannot express; .NET balancing groups exist but are hard to review and are not supported by `NonBacktracking`. A parser makes the grammar and the error positions explicit.

**Plausible wrong approach.** A pattern like `\A\(.*\)\z` accepts `"((a)"`, which is unbalanced, and `"(a)(b)"`, which is two groups, because `.*` cannot track depth.

**How to verify.** Check the parser accepts `(a,(b,c))`, rejects `((a)` with an error at the end of input, and rejects 1,000 nested parentheses with a depth error instead of a `StackOverflowException`.

## Mechanism and diagnostic reasoning

Validation defines what an input means and which representations are accepted. A regular expression can recognize a textual shape, but it does not enforce every semantic rule. A date-shaped string can still name an impossible date. Keep size, syntax and domain validation as separate steps.

Backtracking expressions can require excessive work on adversarial inputs. Use a bounded input length, a timeout and an appropriate engine mode. Prefer simple parsers when they make the contract clearer. Never construct a regex from untrusted text without deciding whether that text is literal or syntax.

`RegexOptions.NonBacktracking` supports a bounded engine for compatible patterns. Anchors constrain the entire input. Regex.Escape treats input as literal pattern text. Domain validation follows a successful shape match.

A timeout is a fallback, not a substitute for a simple pattern and bounded input. Regex does not make a path, SQL query or HTML context safe. Validate according to the destination meaning.

## Review before continuing

Run the reference and confirm it prints `csharp-038: passed`, then rerun the guide's counterexample.
