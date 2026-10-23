# nlp-023: Explanatory solutions

The executable reference checks the declared fixtures. It is separate from the learner scaffold and does not certify general task quality.

## Exercise 1: Filter permission and freshness

The result excludes both stale and unauthorized evidence. A production system must obtain identity and time from trusted inputs and preserve why a source was excluded. Relevance scoring should run only inside the permitted corpus rather than override the access decision.

**Expected:** Only policy version 2 for ops; unknown role and expired time30 yield no records.

## Exercise 2: Fingerprint content reproducibly

The hash identifies the exact canonical bytes used by the system. It does not certify that the policy is correct or complete. Pair the fingerprint with human-readable version and provenance information so a reviewer can interpret it.

**Expected:** Reordering leaves hash unchanged; text change produces a different hash.

## Exercise 3: Measure a defined drift

The distance measures probability mass redistribution under the fixed categories. It is not a performance score or a causal explanation. Input validation prevents meaningless normalization from creating a plausible-looking alert statistic.

**Expected:** Distance.3; negative,nonfinite or zero-total count vectors are rejected.

## Exercise 4: Respect label maturity

Unknown is not the negative class. Mature-case performance may still be selected or unrepresentative if label delay depends on outcome, so retain cohort information and avoid claiming complete deployment accuracy from the available subset.

**Expected:** Two mature cases with accuracy1; all-unknown returns count0 and no accuracy.

## Exercise 5: Treat external text as data

The fixture demonstrates separation of data from control and a narrow pattern transformation. Production prompt-injection defenses and privacy controls require stronger independent boundaries, but the teaching code must not pretend that a source sentence is authorized instruction.

**Expected:** Text remains inert; only the declared email pattern is replaced; no broad anonymization claim.

## Exercise 6: Write a recovery and monitoring contract

If the current policy is absent from the index, changing model weights may not address the problem. A useful runbook names the affected snapshot, a bounded check and a success condition such as the correct permitted version entering retrieval. Preserve user data and original incident evidence during recovery.

**Expected:** A concrete record distinguishes observed failure,hypothesis,authorized action and verified recovery.

## Transfer and limits

A reliable NLP system includes data ingestion, representation, model inference, source access, output validation and monitoring. A correct model file does not establish that the surrounding system is current, authorized or useful. Text corpora change through new documents, revisions, removals and altered permissions, while labels often arrive after predictions.

This lesson treats those boundaries as inspectable data contracts. The reference filters a versioned synthetic document collection by role and validity time, fingerprints its contents, measures a simple distribution shift and computes accuracy only on mature labels. It also keeps adversarial-looking source text as an inert data field. No external service, credential or private corpus is used.

Distinguish data drift from performance degradation. A change in word or category frequencies can be harmless, while an unchanged input distribution can accompany a changed meaning or label policy. Monitoring should lead to a bounded investigation rather than automatically declaring failure or retraining every time a distribution statistic moves.

## Mechanism review and counterexample

A regex can remove a synthetic email pattern, but that is only one narrow redaction mechanism. Names, contextual identifiers, quoted secrets and combinations of fields can still disclose information. Do not label an entire corpus anonymous because one pattern was replaced. Define the data-minimization and access requirements before deciding which text is retained in logs or training.

A production incident record should connect an observed problem to an affected snapshot/model, a reversible check, a recovery action and an acceptance condition. Reindexing may restore missing current documents; rollback may restore a prior model; retraining may be inappropriate if the issue is a changed schema or permission filter. Preserve original evidence and avoid deleting user data as a troubleshooting shortcut.

The system's output contract should include unsupported, stale, unauthorized and malformed outcomes. A reliable assistant can escalate when evidence is insufficient. Measure unnecessary abstention and review workload too, so reliability does not become an excuse for a system that never completes useful tasks.
