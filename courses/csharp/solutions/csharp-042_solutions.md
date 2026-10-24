# csharp-042: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-042_solution.cs](csharp-042_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Evaluate an explicit permission policy:** Absence of an entry does not become implicit permission. Read is allowed and delete is denied.

**Redact before producing diagnostics:** A minimal example makes the diagnostic contract explicit; production structured logging should use an allowlist of safe fields. The token is replaced while a status remains visible.

## Reason through the six tasks

1. **Predict and explain.** Separate identity from permission in a request trace.

2. **Guided modification.** Add a second permitted read action without granting write access.

3. **Independent construction.** Design an allowlist of fields safe to include in an import error.

4. **Diagnose a defect.** Diagnose trusting an isAdmin value supplied in a request body.

5. **Boundary evidence.** Test missing permission and case variants according to the documented identity policy.

6. **Transfer and justify.** Describe authorization checks for a resource owned by another user and the evidence each check needs.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A security boundary is where less-trusted input receives authority: a path reaches a filesystem, text becomes SQL, or a request chooses a resource. Validation must match that destination. A string being valid JSON does not make it a safe file path or a safe authorization decision. Keep data and instructions separate.

Authentication answers who the caller is; authorization answers what that caller may do to this resource. Neither should depend on a client-supplied role string. Secrets belong in a deliberate secret source, not committed examples or logs. The offline fixture teaches an explicit allowlist policy without pretending to implement a complete identity system.

Use exact identity comparisons and explicit permission mappings. A default-deny decision rejects absent policy entries. Parsing and authorization should remain separate methods with separately testable outcomes.

This fixture is policy reasoning, not a complete authentication system. Do not invent cryptography or store passwords in reversible form. Parameter binding and destination-specific APIs are preferable to manual escaping.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
