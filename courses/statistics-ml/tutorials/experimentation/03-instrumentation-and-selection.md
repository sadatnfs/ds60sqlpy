# Reconstruct the experiment before trusting its result

Tutorial ID: `statistics-exp-003`. Prerequisites: `statistics-exp-002`, `statistics-006`. Complete example: [experiment_03.py](examples/experiment_03.py).

## Keep assignment and measurement separate

An assignment table records who was randomized and to what. An event table records what the instrumentation observed. Assignment remains the population spine for intent-to-treat analysis. Joining from events instead silently drops assigned users without recorded events. Counting event rows instead of users gives frequent visitors more influence.

The shared user table has a unique `unit` key. The event table has a unique `event_id` and repeated `unit` values. Aggregate event value by user first, then join with `validate="one_to_one"`. This makes an unintended duplicate user key an explicit error. A database join can be syntactically successful while duplicating every outcome twice; statistical software cannot infer that this was unintended.

## Worked defect: replayed events

The example appends the first ten events again. Summing without deduplication adds about 51.593 points to the measured total. Dropping duplicate `event_id` values restores the original total, and the user aggregates agree with the independently constructed user outcomes.

Deduplication is justified because these rows share stable event identities and represent exact replays. Deduplicating on user and timestamp alone could remove legitimate repeated activity. The record identity and producer contract must explain why two rows represent the same event. If duplicate payloads disagree, preserve both records for diagnosis rather than arbitrarily keeping whichever happened to arrive first.

## Worked defect: failures disappear from exposure logs

Now suppose the new page loses the exposure event for some mobile users who do not convert. The example removes treatment/mobile/nonconversion rows only from the observed exposure population. Assignment-based conversion remains 29/120 in control and 32/120 in treatment. Logged-only treatment conversion becomes 32/95, approximately 0.337. The apparent lift grows because the denominator lost 25 failures, not because any user converted differently.

This is selection on a treatment-affected observation process. The original assignment was randomized, but the analyzed subset is no longer guaranteed comparable. A clean p-value computed on the corrupted subset would quantify variability around the wrong comparison.

## Trace the repair

Start from assignment counts, then compare eligible, triggered, exposure-logged and outcome-observed counts by arm and device. The earliest divergent stage narrows the failure. Inspect event identities and missing outcomes as well as totals. A symmetric loss of every fifth user could preserve allocation balance while changing the target population; passing SRM alone cannot certify the pipeline.

Reconstruct outcomes independently where possible. If outcome data are genuinely missing because the page fails, labeling them zero might or might not match the defined estimand. For a complete transaction system, no transaction can mean zero purchases. For a broken reporting system, no record can mean unknown purchases. The measurement contract decides which interpretation is defensible.

**Answered discussion: Should we discard the bad device segment and ship?** Only a new, transparently defined target could support that restricted decision. The original all-user result is not repaired by deleting the harmed subgroup. Report affected scope, recover measurement if possible, and preserve the original analysis definition alongside any justified revision.

Continue to [power and duration](04-power-and-duration.md). Related source: [data quality and joins](../../chapters/06-measurement-exploratory-analysis-and-data-quality.md).
