## Define the quantity before collecting scores

An evaluation is an argument about a decision. The Research Support Desk answers questions about metrics, evidence and operational procedures. Before comparing assistants, specify the intended population: all future requests, an equal mixture of task families, or requests admitted by an access policy. These populations can have different averages even when they use the same rows. A benchmark is a sample with a construction process, not the population itself.

An **estimand** is the quantity the analysis seeks to learn. A **metric** is a rule applied to observations to estimate or describe it. The **unit** is what counts as an independent opportunity or randomized entity. A request row can be an observation while a user, document or question family is the dependence unit. A metric definition must include the denominator and how refusals, timeouts, missing labels and duplicate variants are treated. Dropping failures after inspecting outcomes changes the question.

For loss \(L\), system \(s\), input \(X\), outcome \(Y\) and target distribution \(P\), the risk is

\[
R_s(P)=\mathbb{E}_{(X,Y)\sim P}[L(s(X),Y)].
\]

Here \(\mathbb{E}\) denotes expectation: the population-weighted average of the loss under the stated distribution. A sample mean estimates that quantity only under an appropriate sampling or modeling argument.

A paired improvement can be defined as \(\Delta=\mathbb{E}[L_A-L_B]\), so positive values favor B. If using correctness instead, define \(\Delta=\mathbb{E}[C_B-C_A]\). Do not reuse the word improvement while silently reversing this sign convention. The programs use correctness differences with explicit identifiers.

## Worked case A: family balance changes the question

Three metrics questions improve by one point each; one policy question worsens by one. The request-weighted difference is 0.5. Equal weighting of the two family means gives zero. Neither calculation is arithmetically wrong. The first describes the observed request mix; the second treats the two families as equally important. A product decision needs a declared target mix and enough independently sampled families to support its uncertainty analysis.

Duplicating the metrics examples should change the request average if those copies are treated as additional requests. It should not change an equal-family average when the family means themselves stay unchanged. This is an invariant of the estimator, not evidence that duplication creates new information. The assertion below makes the distinction inspectable.

{{WORKED_A}}

## Worked case B: unknown labels and critical failures

Suppose one candidate has two judged successes and one unjudged response. Its observed-label accuracy is 1.0, but only two thirds of eligible responses have labels. Reporting 1.0 without label coverage hides a selection problem. Coding the missing response as a failure changes the estimand too; that may be a conservative operational convention, but it must be named and justified.

A critical access violation remains a separate gate. High average correctness cannot compensate for exposing a restricted document. Keep a decision packet with named metric results, label coverage, critical-error outcomes and unresolved conditions. The code returns an explicit no-go when a required gate fails or remains unknown.

{{WORKED_B}}

## Reading the code and diagnosing errors

`family_difference` first pairs systems on the same identifiers, forms differences, then groups them. Means calculated from two independently filtered tables are not paired comparisons. The duplicate-key guard fails before any average is produced. `decision` uses `is True`, so missing evidence cannot become a positive decision by truthiness or by an empty list of failures.

When a result looks unexpectedly favorable, inspect the eligible row count, judged row count, refusal policy and family mix before changing a model. Preserve the original eligibility ledger. Otherwise a later analyst cannot determine whether an improvement came from better answers or from removing difficult requests.

For a real deployment, replace the authored records with a documented sample and a labeling protocol. State the coverage gap, affected users, evaluation period and conditions for revisiting the decision. This lesson establishes arithmetic and contract checks on a synthetic fixture. It does not estimate a real assistant's risk or provide a universal release threshold.
