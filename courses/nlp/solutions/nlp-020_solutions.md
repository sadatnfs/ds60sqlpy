# nlp-020: Explanatory solutions

The executable reference checks the declared fixtures. It is separate from the learner scaffold and does not certify general task quality.

## Exercise 1: Compute weak-label diagnostics

Coverage identifies any non-abstaining source, while conflict requires at least one zero and one one. The third row is the only conflict. Reporting .25 or one-third without naming the denominator would make two correct calculations look inconsistent.

**Expected:** Coverage.75,overall conflict.25 and conflict among covered1/3.

## Exercise 2: Implement tie-aware voting

Abstentions contribute no class evidence. A tie and no coverage share the output sentinel but should retain different diagnostic flags. A production consumer must not coerce -1 into class zero or a negative array index.

**Expected:** Outputs[1,0,-1,-1].

## Exercise 3: Inspect source correlation

The numerical change shows how repetition of one cue can dominate a naive vote. It does not establish that collapsing is always the best statistical model. A learned label model needs assumptions and validation for source dependence and accuracy.

**Expected:** Majority1 becomes abstain, with a written explanation of duplicated evidence.

## Exercise 4: Rank uncertainty

Entropy measures uncertainty under the current predicted distribution. It does not directly measure expected labeling value or detect every confidently wrong outlier. The selection rule is a heuristic whose behavior should be inspected by class and domain.

**Expected:** Top two uncertainty indices[0,1]; \(p=0.5\) has maximum entropy.

## Exercise 5: Enforce diversity and budget

The second-most-uncertain item is skipped because its family is already present. Index three is more uncertain than index two, so it fills the second slot. The explicit budget and stable ordering make the policy reproducible, but not universally optimal.

**Expected:** Selected indices[0,3]; budget0 returns an empty batch.

## Exercise 6: Protect independent evaluation

Active selection changes the distribution of labeled examples. A final score on that selected pool answers a different question from expected deployment performance. Keep a representative gold set or use a justified sampling-aware analysis, and record rule/model versions so changes in supervision are auditable.

**Expected:** A written split and provenance ledger prevent reviewed pool cases from silently becoming the final acceptance set.

## Transfer and limits

Weak supervision creates noisy training signals from rules, heuristics, databases or model suggestions when full manual annotation is expensive. Active learning chooses which examples to send for labeling next. They address different parts of the data problem: weak supervision expands label supply, while active learning allocates a limited review budget. Neither makes an independently labeled evaluation set unnecessary.

A labeling function can emit class zero, class one or abstain. Abstention means the rule has no applicable evidence under its scope, not that the example belongs to a negative class. Multiple rules can overlap, conflict or share the same underlying cue. Treating three correlated versions of one rule as three independent experts can exaggerate confidence.

The executable reference implements transparent majority voting with tie abstention and uncertainty/diversity selection. It does not implement Snorkel's learned label model or claim to estimate rule accuracies from unlabeled data. That distinction keeps the limitations of a simple baseline visible before introducing a probabilistic weak-supervision system.

## Mechanism review and counterexample

Start with an annotation guide and a small independent reviewed set. Write labeling functions with narrow documented scopes, inspect coverage/conflict and evaluate their errors. Train a baseline on weak labels, then use uncertainty and diversity to propose a bounded review batch from a pool disjoint from final evaluation. Reviewers should see the source evidence and know whether labels were model-assisted.

After each iteration, retrain and compare on unchanged acceptance cases plus deliberately added regression cases. Measure annotation cost, class coverage and task utility, not only label volume. Stop when the marginal information gain no longer justifies the review effort or when the dominant issue is a label definition or data-collection gap rather than model uncertainty.
