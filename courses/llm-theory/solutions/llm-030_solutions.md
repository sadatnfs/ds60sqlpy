# llm-030: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Pretraining data provenance records where a document came from, what use is permitted and how it enters the experiment. A filename or download timestamp alone cannot answer these questions. Evaluation contamination includes exact benchmark answers and derived paraphrases entering training or selection sources. Deduplication helps but does not establish permission, privacy or semantic independence. The local fixture contains authored snippets so no external collection or permission decision is required. The goal is to design a reviewable manifest and identify when a source should be excluded or investigated, not to issue legal conclusions about an unknown corpus.

**Provenance:** A record of origin and transformations for a data item.

**Permission field:** An explicit documented basis or unresolved status for use.

**Derived contamination:** Assessment information entering through paraphrases or transformed copies.

## Reading the implementation

A useful record has document_id, source, permission, split, family and content_hash. Source identifies origin; permission records an explicit basis or unresolved status. Split states intended information use. Family groups related derivatives. Audit the complete dependency path, including tokenizer fitting and prompt selection, because contamination can occur before gradient training.

## Exercise 1: Complete a validation row

The question is: Document d6 is an authored practice question placed in validation, family F3. Write its manifest row and state which uses it may serve.

Validation data may guide choices such as early stopping, which is why it must stay separate from the test family F2 used for the final report.

```text
d6 | local author | course fixture permission | validation | F3 | hash-of-d6
Gradient updates: not admitted
Model selection: admitted
Final test reporting: not admitted
```

**Expected:** row d6 | local author | course fixture permission | validation | F3 | hash-of-d6; model selection only, not gradients or final test reporting.

**Verify:** Check that the d6 row fills all five required fields and that the use list admits model selection while refusing gradient updates and final test reporting.

## Exercise 2: Correct a mislabelled family

The question is: A manifest records d3, the answer to test document d2, as family F1 in train because it came from a crawl labelled training. Identify the error and correct the row.

The family follows the evaluation relationship, not the folder where the bytes were found. Leaving d3 in F1 would let a test answer reach training while every manifest field looked complete.

```text
Recorded: d3 | crawl | unknown | train | F1
Problem: d3 reproduces the answer to test document d2
Corrected: d3 | crawl | unresolved permission | blocked | F2 (evaluation-derived)
```

**Expected:** d3 belongs to evaluation-derived family F2 and is blocked; a crawl label is neither provenance nor permission.

**Verify:** Check that the corrected row moves d3 from F1 to F2, blocks its training admission and keeps permission unresolved instead of inferring it from the crawl label.

## Exercise 3: Follow a paraphrase family

The question is: d4 rewrites d3 without sharing an exact hash. Assign a family and audit.

A hash detects exact identity, not semantic derivation. Family metadata preserves the relation that matters to this contamination scenario.

```text
d3 -> paraphrase -> d4
Different bytes do not erase provenance.
Family F2 must not cross into train or prompt-selection material.
```

**Expected:** d4 remains in evaluation-derived family F2.

**Verify:** Check that d4 inherits family F2 through its d3 relationship even though its hash differs, and that the record blocks F2 from training and prompt selection.

## Exercise 4: Separate permission and cleanliness

The question is: A source has explicit permission but contains evaluation answers. Is it suitable training data for this assessment?

Different gates answer different questions. A permitted source can still invalidate an evaluation, and a clean split does not establish permission.

```text
Permission check: pass
Evaluation independence check: fail
Training decision for this experiment: exclude
```

**Expected:** permission alone does not resolve contamination.

**Verify:** Check that the record has two separate results, permission pass and evaluation independence fail, and that the exclusion follows from the failed check.

## Exercise 5: Audit preprocessing inputs

The question is: A tokenizer is fitted on train+test although model gradients use only train. Identify the boundary failure.

The representation is fitted state. Keeping test labels out of the optimizer does not undo an earlier information leak through vocabulary selection.

```text
Tokenizer fit sources: d1,d2
Allowed training sources: d1
Unexpected assessment source: d2
Repair: refit tokenizer on admitted training sources and rerun evaluation.
```

**Expected:** test information influenced the fitted tokenizer.

**Verify:** Check that the audit lists d2 among the tokenizer fit sources but not among allowed training sources, and that the repair refits on d1 before evaluation is rerun.

## Exercise 6: Record an unresolved source

The question is: d5 has unknown origin and unspecified permission. Write its manifest status without inventing approval.

Unknown fields should remain visibly unknown. Filling them with assumed values would make an apparently complete manifest less trustworthy than an honest incomplete one.

```text
d5 | unresolved origin | unresolved permission | unassigned | unknown family | actual hash required
Action: obtain evidence before admitting to the experiment.
```

**Expected:** origin unresolved; permission unresolved; admission blocked.

**Verify:** Check that the d5 row keeps origin, permission and family unresolved, requires the actual hash and leaves the document unadmitted.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
