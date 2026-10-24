# csharp-038: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-038_solution.cs](csharp-038_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Validate a bounded identifier:** Whole-input anchors prevent a valid substring from disguising an invalid full value. The identifier begins with a lowercase letter and uses only admitted characters.

**Keep literal user text literal:** Escaping preserves data meaning instead of accidentally granting regex syntax authority. The plus sign is matched literally.

## Reason through the six tasks

1. **Predict and explain.** Explain every part of the identifier pattern.

2. **Guided modification.** Change the maximum identifier length and test the exact boundary.

3. **Independent construction.** Validate a structured identifier and then check its domain-specific reserved words.

4. **Diagnose a defect.** Diagnose matching a valid substring inside an invalid full input.

5. **Boundary evidence.** Test newline, empty input and one character beyond the limit.

6. **Transfer and justify.** Choose a parser or regex for a nested format and justify complexity and error reporting.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Validation defines what an input means and which representations are accepted. A regular expression can recognize a textual shape, but it does not enforce every semantic rule. A date-shaped string can still name an impossible date. Keep size, syntax and domain validation as separate steps.

Backtracking expressions can require excessive work on adversarial inputs. Use a bounded input length, a timeout and an appropriate engine mode. Prefer simple parsers when they make the contract clearer. Never construct a regex from untrusted text without deciding whether that text is literal or syntax.

`RegexOptions.NonBacktracking` supports a bounded engine for compatible patterns. Anchors constrain the entire input. Regex.Escape treats input as literal pattern text. Domain validation follows a successful shape match.

A timeout is a fallback, not a substitute for a simple pattern and bounded input. Regex does not make a path, SQL query or HTML context safe. Validate according to the destination meaning.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
