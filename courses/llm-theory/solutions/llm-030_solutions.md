# llm-030: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Pretraining data provenance records where a document came from, what use is permitted and how it enters the experiment. A filename or download timestamp alone cannot answer these questions. Evaluation contamination includes exact benchmark answers and derived paraphrases entering training or selection sources. Deduplication helps but does not establish permission, privacy or semantic independence. The local fixture contains authored snippets so no external collection or permission decision is required. The goal is to design a reviewable manifest and identify when a source should be excluded or investigated, not to issue legal conclusions about an unknown corpus.

**Provenance:** A record of origin and transformations for a data item.

**Permission field:** An explicit documented basis or unresolved status for use.

**Derived contamination:** Assessment information entering through paraphrases or transformed copies.

## Reading the implementation

A useful record has document_id,source,permission,split,family andcontent_hash. Source identifies origin; permission records an explicit basis or unresolved status. Split states intended information use. Family groups related derivatives. Audit the complete dependency path, including tokenizer fitting and prompt selection, because contamination can occur before gradient training.

## Exercise 1: Complete a manifest

The question is: Documentd1 is authored for the lesson, familyF1, training;d2 is an authored evaluation question, familyF2,test. Fill required fields.

The placeholder hash labels in this worksheet identify the field to calculate from actual bytes. They are not claimed cryptographic receipts. Every real manifest row needs its actual digest.

```text
d1 | local author | course fixture permission | train | F1 | hash-of-d1
d2 | local author | course fixture permission | test  | F2 | hash-of-d2
```

**Expected:** both rows have source,permission,split,family,hash.

**Verify:** Compare the computed values or written argument with both rows have source,permission,split,family,hash.

## Exercise 2: Flag a benchmark answer

The question is: A candidate training document reproduces the answer tod2. Decide how to treat it before fitting.

Changing the filename or splitting at the row level does not remove the information transfer. The answer has already exposed the assessment target.

```text
candidate d3: answer-to-d2
Relationship: evaluation-derived
Training admission: blocked
Selection-source admission: blocked
```

**Expected:** exclude from training and selection sources pending contamination review.

**Verify:** Compare the computed values or written argument with exclude from training and selection sources pending contamination review.

## Exercise 3: Follow a paraphrase family

The question is: d4 rewritesd3 without sharing an exact hash. Assign a family and audit.

A hash detects exact identity, not semantic derivation. Family metadata preserves the relation that matters to this contamination scenario.

```text
d3 -> paraphrase -> d4
Different bytes do not erase provenance.
FamilyF2 must not cross into train or prompt-selection material.
```

**Expected:** d4 remains in evaluation-derived familyF2.

**Verify:** Compare the computed values or written argument with d4 remains in evaluation-derived familyF2.

## Exercise 4: Separate permission and cleanliness

The question is: A source has explicit permission but contains evaluation answers. Is it suitable training data for this assessment?

Different gates answer different questions. A permitted source can still invalidate an evaluation, and a clean split does not establish permission.

```text
Permission check: pass
Evaluation independence check: fail
Training decision for this experiment: exclude
```

**Expected:** permission alone does not resolve contamination.

**Verify:** Compare the computed values or written argument with permission alone does not resolve contamination.

## Exercise 5: Audit preprocessing inputs

The question is: A tokenizer is fitted ontrain+test although model gradients use onlytrain. Identify the boundary failure.

The representation is fitted state. Keeping test labels out of the optimizer does not undo an earlier information leak through vocabulary selection.

```text
Tokenizer fit sources: d1,d2
Allowed training sources: d1
Unexpected assessment source: d2
Repair: refit tokenizer on admitted training sources and rerun evaluation.
```

**Expected:** test information influenced the fitted tokenizer.

**Verify:** Compare the computed values or written argument with test information influenced the fitted tokenizer.

## Exercise 6: Record an unresolved source

The question is: d5 has unknown origin and unspecified permission. Write its manifest status without inventing approval.

Unknown fields should remain visibly unknown. Filling them with assumed values would make an apparently complete manifest less trustworthy than an honest incomplete one.

```text
d5 | unresolved origin | unresolved permission | unassigned | unknown family | actual hash required
Action: obtain evidence before admitting to the experiment.
```

**Expected:** origin unresolved; permission unresolved; admissionblocked.

**Verify:** Compare the computed values or written argument with origin unresolved; permission unresolved; admissionblocked.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
