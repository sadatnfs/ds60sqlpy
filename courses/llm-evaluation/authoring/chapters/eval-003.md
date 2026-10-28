## Operationalize the claim

A rubric connects an intended capability to observations. For the Research Support Desk, an answer may be syntactically valid, numerically correct, supported by its cited source, appropriately scoped and usable by its recipient. These are separate properties. A fluent answer with the wrong denominator can satisfy a style criterion while failing the actual task.

Begin with the use case and the decisions that labels will support. Specify an eligible response, an applicable criterion, the allowed evidence and the unit at which the label is assigned. A citation-support label may belong to a claim, while task completion belongs to an answer. Averaging claim scores gives long answers more weight unless the aggregation rule explicitly addresses that choice.

**Construct validity** asks whether the operational measure represents the intended concept. Reliable annotators can agree perfectly on a poor proxy. For example, a rule that awards a point whenever an answer contains a citation marker is reproducible but does not measure whether the cited passage supports the claim. Conversely, a nuanced factuality rubric may be meaningful yet initially yield poor agreement because its instructions are incomplete.

Use anchored categories with examples and counterexamples. A numerical-answer rubric can distinguish a wrong value, a correct value with an unstated unit, and a fully correct value/unit/denominator. Ordinal levels carry an ordering, but equal distances between adjacent levels are not automatic. A score of two is not necessarily twice the quality of one. Keep labels and aggregation policy separately versioned.

## Worked case A: critical conditions remain separate

The first example evaluates two authored answers. Both have useful surface form, but one fails an access-control condition. A weighted average can still favor that answer if the other dimensions are strong. The release gate therefore combines a minimum quality score with an explicit critical-condition check. The chosen numbers are illustrative policy constants, not universal thresholds for assistants.

The rubric function distinguishes an inapplicable criterion from a failed criterion. Dividing by the full rubric length when some dimensions do not apply penalizes a system for questions it was not asked to answer. Dropping difficult applicable criteria has the opposite problem. Eligibility should be fixed without using the desired outcome.

{{WORKED_A}}

## Worked case B: adjudication does not erase evidence

Two reviewers assign different labels. An adjudicator can resolve a production label for downstream scoring, but the original annotations remain useful for assessing ambiguity, training annotators and estimating uncertainty. The code appends an adjudication record linked to the originals instead of overwriting the first reviewer.

An audit ledger needs stable item and annotator IDs, a rubric version, a timestamp or order, the evidence consulted and an adjudication reason. The toy records omit real people and real timestamps intentionally. Their purpose is to show version and lineage checks, not to impersonate an actual human annotation study.

{{WORKED_B}}

## Design a labeling study

Train annotators on a development set, revise ambiguous rules there, and then freeze the rubric before assessing the held-out evaluation set. Blind candidate identity when feasible. Randomize display order for paired judgments and retain that order for analysis. Include repeated and calibration items deliberately, while distinguishing them from new independent observations.

Estimate the resources needed for double labeling and adjudication rather than pretending that every row has equal certainty. A sample of difficult cases selected for adjudication is valuable for improving a rubric, but its disagreement rate is not automatically the population disagreement rate. Sampling weights and selection criteria matter.

## Diagnose a rubric failure

If agreement rises while task usefulness falls, inspect whether the rubric became easier to satisfy rather than more valid. If a model optimizes the visible rubric, test counterexamples that keep the proxy high while damaging the intended outcome. Preserve failures with their original inputs and evidence. A single composite score is insufficient to explain whether a system became more correct, merely longer, or better at producing required formatting.
