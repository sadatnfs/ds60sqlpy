## Define the boundary being tested

A robustness test changes an input condition and observes whether a required property survives. A harmless formatting change may be intended to preserve the answer, while a changed unit or date should alter it. The relation must be specified before calling every output difference a failure or every identical output a success.

Security requirements are different from average task quality. A research assistant must not obtain access merely because a document or generated tool proposal claims to be authorized. Authority should come from trusted metadata and the caller's permissions. Retrieved text is data for the task. It is not an instruction channel for granting new rights.

The examples use public and restricted synthetic fixture records. They do not inspect real credentials, make network requests or execute shell commands. Their purpose is to make an authorization invariant and a bounded proposal validator executable. A system that passes these small checks has demonstrated only the named cases, not universal resistance to adversarial prompting.

## Worked case A: authorization before content matching

The retrieval helper first filters documents by trusted access metadata and only then evaluates the query. A restricted document includes the word public in its text. A content-based shortcut would misclassify it, but the metadata policy does not. The code also shows that appending an instruction-like request to the query cannot expand the allowed document set.

{{WORKED_A}}

## Worked case B: generated proposals have no inherent authority

A generated proposal is parsed as a small data object. Its operation must be allowlisted, its fields exact, its identifier well formed and its target authorized. The helper returns an approved synthetic lookup result only after all conditions hold. A proposal to invoke an unspecified operation is rejected; the string is never passed to a shell or interpreted as executable code.

{{WORKED_B}}

## Design an adversarial assessment

Create a threat model describing the attacker-controlled surface, trusted policy, possible side effects and failure severity. Sample tests across relevant attack families instead of repeating one phrase many times. Keep a record of which families and transformations were attempted. Zero failures among a few known patterns does not imply zero risk for unrepresented conditions.

Use metamorphic cases alongside adversarial ones. Whitespace or display-order transformations can test intended invariances. A changed permission or document date should change eligibility. Check the intermediate authorized candidate set as well as the final answer, because a system may accidentally access restricted content without quoting it in its response.

## Separate policy enforcement from model scoring

A model judge can help classify suspicious outputs, but it should not be the sole authority deciding whether an operation is permitted. Deterministic controls are appropriate for explicit constraints such as an allowed operation set, resource identity and maximum request size. Model behavior and policy controls should have separate versions and evidence.

When evaluating safety-related outcomes, preserve unknown and ambiguous cases for review. Do not reduce a critical failure to a small negative contribution in a broad helpfulness average. Define escalation and rollback decisions with the same care as the ordinary quality metric. A statistical confidence interval around observed failure frequency does not prove that the test distribution covers the threat model.

## Diagnose failures and transfer responsibly

A failed case should retain its input, policy context, attempted operation and actual side effect. Fixing the visible response while leaving an unauthorized intermediate action is insufficient. Re-run the failed case and independent neighboring cases after a repair, then evaluate the changed system on a broader held-out set.

The fixture demonstrates strict schema and authorization checks for an inert local lookup. A real system additionally needs identity integration, auditable resource ownership, secure implementation and operational monitoring. Those requirements cannot be inferred from a successful toy validator or a high benchmark score.
