# csharp-042: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-042_solution.cs](csharp-042_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Evaluate an explicit permission policy:** Absence of an entry does not become implicit permission. Read is allowed and delete is denied.

**Redact before producing diagnostics:** A minimal example makes the diagnostic contract explicit; production structured logging should use an allowlist of safe fields. The token is replaced while a status remains visible.

## Task answers

### Task 1: Predict and explain

Separate identity from permission in a request trace.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Absence of an entry does not become implicit permission. Read is allowed and delete is denied.

### Task 2: Guided modification

Add a second permitted read action without granting write access.

No separate reference answer has been written for this task. Start from Example B: A minimal example makes the diagnostic contract explicit; production structured logging should use an allowlist of safe fields. The token is replaced while a status remains visible.

### Task 3: Independent construction

Design an allowlist of fields safe to include in an import error.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
string[] allowed = { "line", "field", "reason" };
var safe = new HashSet<string>(allowed, StringComparer.Ordinal);
var error = new Dictionary<string, string>();
error["line"] = "4";
error["field"] = "quantity";
error["reason"] = "negative";
error["token"] = "synthetic-secret";
var visible = error.Where(item => safe.Contains(item.Key));
var shown = visible.ToDictionary(item => item.Key, item => item.Value);
Check(shown.Count == 3 && !shown.ContainsKey("token"), "allowlisted");
```

**Observe:** The visible error keeps line, field and reason and drops the token.

An allowlist names what may be shown, so a new sensitive field is hidden by default instead of leaking until someone adds it to a blocklist.

### Task 4: Diagnose a defect

Diagnose trusting an isAdmin value supplied in a request body.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: This fixture is policy reasoning, not a complete authentication system. Do not invent cryptography or store passwords in reversible form. Parameter binding and destination-specific APIs are preferable to manual escaping.

### Task 5: Boundary evidence

Test missing permission and case variants according to the documented identity policy.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Evaluate an explicit permission policy) and Example B (Redact before producing diagnostics).

### Task 6: Transfer and justify

Describe authorization checks for a resource owned by another user and the evidence each check needs.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Authentication**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A security boundary is where less-trusted input receives authority: a path reaches a filesystem, text becomes SQL, or a request chooses a resource. Validation must match that destination. A string being valid JSON does not make it a safe file path or a safe authorization decision. Keep data and instructions separate.

Authentication answers who the caller is; authorization answers what that caller may do to this resource. Neither should depend on a client-supplied role string. Secrets belong in a deliberate secret source, not committed examples or logs. The offline fixture teaches an explicit allowlist policy without pretending to implement a complete identity system.

Use exact identity comparisons and explicit permission mappings. A default-deny decision rejects absent policy entries. Parsing and authorization should remain separate methods with separately testable outcomes.

This fixture is policy reasoning, not a complete authentication system. Do not invent cryptography or store passwords in reversible form. Parameter binding and destination-specific APIs are preferable to manual escaping.

## Review before continuing

Run the reference and confirm that it prints `csharp-042: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
