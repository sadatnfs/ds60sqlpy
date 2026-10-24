# nlp-019: Explanatory solutions

The executable reference checks the declared fixtures. It is separate from the learner scaffold and does not certify general task quality.

## Exercise 1: Define the annotation unit

A useful rubric makes disagreement diagnosable. It distinguishes a quoted urgent phrase from an actual urgent request and states how missing context is handled. The exact operational criteria depend on the application; the task is to make them inspectable rather than assume a word has a universal label.

**Expected:** A concrete unit, two label definitions, abstention/review rule and a counterexample.

## Exercise 2: Calculate agreement manually

The numerator removes the agreement implied by marginal category usage, while the denominator rescales the remaining possible agreement. Comparing with the independent arithmetic catches a library-call or label-alignment mistake. The statistic still says nothing by itself about construct validity.

**Expected:** 2/3,1/2,1/3 respectively, matching the library.

## Exercise 3: Explain the imbalanced case

The raters agree on the common category but disagree on the rare exceptions. The chance-adjusted score reflects that pattern. Inspecting the confusion table and category-specific behavior is more informative than choosing whichever single statistic looks favorable.

**Expected:** Raw agreement.98 but kappa slightly below zero.

## Exercise 4: Retain soft labels

The proportions summarize this rater panel's judgments. Entropy describes their dispersion, not a calibrated probability of objective truth. A downstream use should preserve that interpretation and consider whether disagreement reflects ambiguity, measurement error or differing legitimate perspectives.

**Expected:** Soft labels[2/3,1,0]; positive entropy only for the disputed row.

## Exercise 5: Preserve adjudication evidence

Adjudication resolves a workflow decision while preserving its history. Replacing all raw ratings with the final value would erase the evidence needed to improve the guide or audit consistency. Include the rubric version and source evidence when extending the record.

**Expected:** Original(1,1,0),final label1,rationale and item identity retained.

## Exercise 6: Handle undefined agreement

An undefined statistic should remain visible rather than be coerced into perfect reliability. The sample contains no category variation, so it cannot reveal how raters distinguish cases. A better follow-up deliberately includes relevant difficult cases while preserving a separate representative sample for population estimates.

**Expected:** Raw agreement1,kappa undefined/None; follow-up includes rare and ambiguous categories.

## Transfer and limits

Labels are measurements created by people, rules or models under an annotation contract. They are not automatically error-free truth. A sentiment label can depend on whose sentiment is being described, an entity boundary can depend on a corpus convention, and an urgency label can depend on an operational threshold. Improving a model before clarifying the label can optimize the wrong target more efficiently.

An annotation guide should define the unit, label inventory, inclusion/exclusion rules, ambiguous cases and an abstention or uncertainty policy. It should include counterexamples, not only easy positive examples. Annotators need the same source context that the eventual task requires, and that context must not contain information unavailable at the intended prediction time.

This lesson calculates agreement, preserves disagreement through soft labels and demonstrates an auditable adjudication record. The examples use invented binary judgments to expose mathematical behavior. Agreement measures consistency among raters under a procedure; they do not establish that the procedure measures the right construct.

## Mechanism review and counterexample

Pilot the guide on representative examples, collect independent labels, inspect disagreement and revise ambiguous rules. Keep a record of which cases informed rubric development, then evaluate the revised process on new items. Split by document family when near-duplicate sentences share context.

A language model can propose labels or explanations, but model-assisted annotation changes the measurement process. Human reviewers may anchor on the suggestion, making apparent agreement less independent. Compare assisted and unassisted judgments when the distinction matters, and preserve the proposal separately from the accepted label. The same principle applies to using one model to label data for another model's evaluation.
