# csharp-042: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-042_solution.cs](csharp-042_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Evaluate an explicit permission policy:** Absence of an entry does not become implicit permission. Read is allowed and delete is denied.

**Redact before producing diagnostics:** A minimal example makes the diagnostic contract explicit; production structured logging should use an allowlist of safe fields. The token is replaced while a status remains visible.

## Task answers

### Task 1: Predict and explain

Separate identity from permission in a request trace.

**Written answer.** In a request trace, identity answers who is calling: an authenticated subject such as `user-17` established by a verified token. Permission answers what that subject may do: whether the action `report:read` is in the set granted to it. Example A only has the permission step, a `HashSet<string>` with `StringComparer.Ordinal` containing `report:read`. A trace should show both separately: subject authenticated, then action checked against the grants, then allowed or denied.

**Why it is correct.** Knowing who someone is never implies what they may do. Keeping the steps apart makes a denied request explainable as either an unknown caller or a known caller without that right.

**Plausible wrong approach.** Treating a successful login as permission to everything, or checking permission against a name the caller typed, merges the two steps and removes the boundary.

**How to verify.** Trace one request where the identity is valid but `report:delete` is denied, and one where the token is missing so the permission check never runs.

### Task 2: Guided modification

Add a second permitted read action without granting write access.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```csharp
var rights = new HashSet<string>(StringComparer.Ordinal);
rights.Add("report:read");
rights.Add("audit:read");
Check(rights.Contains("audit:read"), "second read allowed");
Check(!rights.Contains("audit:write"), "audit write still denied");
Check(!rights.Contains("report:write"), "no write implied");
bool IsRead(string right) {
  return right.EndsWith(":read", StringComparison.Ordinal);
}
Check(rights.All(IsRead), "every grant is a read");
```

**Observe:** `audit:read` is allowed, neither `audit:write` nor `report:write` is, and every grant ends in `:read`.

The allowlist grants exact action names, so adding `audit:read` grants that one action and nothing related to it. Write access is denied because it is absent, not because a rule removed it. The last check states the intended property of this role directly: it holds only read actions, so a later edit that adds a write grant fails visibly.

**Plausible wrong approach.** Granting `audit:*` or checking `right.StartsWith("audit")` would admit `audit:write` and `audit:delete` along with the read.

**How to verify.** Add `audit:write` to the set and observe that both the write check and the read-only check fail.

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

**Written answer.** If the handler reads `{"user":"u1","isAdmin":true}` and uses `isAdmin` to grant access, the caller has chosen its own permissions: anyone can type `true`. The request body is untrusted data, like any other input. The server must derive roles from the authenticated identity, for example by looking up grants for the subject from a verified token, and ignore or reject a privilege field in the body.

**Why it is correct.** A security boundary only works if the side that decides cannot be influenced by the side being checked. A flag supplied by the client is on the wrong side of the boundary.

**Plausible wrong approach.** Validating that `isAdmin` is a boolean, or hiding the field in the user interface, does not help: a crafted request can still send `true`.

**How to verify.** Send the same request with `isAdmin` set to true from a non-admin identity and confirm the server still denies admin actions and its decision trace mentions the stored grants, not the body.

### Task 5: Boundary evidence

Test missing permission and case variants according to the documented identity policy.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```csharp
var rights = new HashSet<string>(StringComparer.Ordinal);
rights.Add("report:read");
Check(rights.Contains("report:read"), "exact action allowed");
Check(!rights.Contains("report:delete"), "missing permission denied");
Check(!rights.Contains(""), "empty action denied");
Check(!rights.Contains("Report:read"), "case variant denied");
Check(!rights.Contains("REPORT:READ"), "upper case denied");
Check(!rights.Contains("report:read "), "trailing space denied");
```

**Observe:** Only the exact string `report:read` is allowed; a missing permission, an empty action, case variants and a trailing space are all denied.

The documented policy is ordinal: action names are identifiers compared byte for byte, so `Report:read` is a different, ungranted action. Denying near matches fails closed. If the product decided action names were case-insensitive, that would be a separate, written decision implemented by constructing the set with `StringComparer.OrdinalIgnoreCase`, never by lowercasing some inputs and not others.

**Plausible wrong approach.** Calling `ToLower()` on the request before the check while the set uses `Ordinal` creates a policy nobody wrote down, and it differs from culture-sensitive lowercasing in some locales.

**How to verify.** Build a second set with `StringComparer.OrdinalIgnoreCase` and confirm the case variants are allowed there but the trailing space and the empty action are still denied.

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
