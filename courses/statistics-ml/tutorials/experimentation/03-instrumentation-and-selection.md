# Reconstruct the experiment before trusting its result

Tutorial ID: `statistics-exp-003`. Prerequisites: `statistics-exp-002`, `statistics-006`. Complete example: [experiment_03.py](examples/experiment_03.py).

## Key terms

- **Population spine:** The assignment table of everyone randomized, onto which event data are joined so assigned users without events stay in the analysis.
- **Intent-to-treat analysis:** A comparison of all units as randomized, regardless of whether they generated events or used the change.
- **User-level aggregation:** Summing event values per user before joining to assignment, so the comparison has one outcome per randomized unit.
- **Deduplication key:** A unique identifier such as `event_id` whose repeated values mark replayed rows that can be dropped without losing real events.
- **Treatment-affected selection:** Bias that arises when treatment changes which units or events are observed, so filtering on the observed data no longer preserves randomization.

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

## Worked example: a fan-out join changes the estimand silently

The defect below raises no error. Run it inside [experiment_03.py](examples/experiment_03.py) after the fixture is defined.

```python prelude=examples/experiment_03.py
users, events, _, _ = experiment_fixture()
fanned = users.merge(events, on="unit", how="left")
print("rows after naive join:", len(fanned))
print(
    "mean value per row:",
    round(fanned.value.mean(), 3),
    "vs per user:",
    round(users.value.mean(), 3),
)
try:
    users.merge(events, on="unit", how="left", validate="one_to_one")
except pd.errors.MergeError as error:
    print("validate caught:", type(error).__name__)
```

```text
rows after naive join: 943
mean value per row: 20.407 vs per user: 20.744
validate caught: MergeError
```

Joining user rows to event rows repeats each user's seven-day value once per visit, producing 943 rows from 240 users. The resulting mean, 20.407, is a visit-weighted average of user values rather than value per assigned user. Here the two numbers are close only because the fixture generates visits independently of value. If heavy visitors were also high-value users, the fanned mean would be inflated, and a treatment that raised visits would appear to raise value even with no change per user. The same `merge` with `validate="one_to_one"` refuses to run, turning a silent estimand change into an error the analyst must explain.

## Worked example: localize the exposure loss with a funnel table

A single overall count hides where users disappear. Break assignment and logging counts out by device and arm.

```python
users, _, _, _ = experiment_fixture()
failed = (users.assigned == 1) & (users.device == "mobile") & (users.converted == 0)
funnel = pd.DataFrame(
    {
        "assigned": users.groupby(["device", "assigned"]).size(),
        "logged": users[~failed].groupby(["device", "assigned"]).size(),
    }
)
funnel["retained"] = (funnel.logged / funnel.assigned).round(3)
print(funnel)
```

```text
                  assigned  logged  retained
device  assigned
desktop 0               78      78     1.000
        1               82      82     1.000
mobile  0               42      42     1.000
        1               38      13     0.342
```

Three cells retain every assigned user and one cell, treated mobile, keeps only 13 of 38. That asymmetry is the signature of a treatment-caused logging failure; a loss affecting both arms on mobile would instead point to device instrumentation unrelated to the redesign. The 25 missing rows are exactly the 25 failures that inflated logged-only conversion to 32/95. Note that this table needs outcome-independent assignment records: if the assignment service itself were fed by exposure logs, no retained ratio could be computed and the failure would be invisible.

## Diagnostics to run before any effect estimate

Check key uniqueness on both tables, row counts at each stage by arm and segment, and the reconciliation of event totals against independently stored user totals. A defect that passes all three can still exist, for example a timestamp shift that moves events across the seven-day boundary, so also compare outcome windows by arm.

Continue to [power and duration](04-power-and-duration.md). Related source: [data quality and joins](../../chapters/06-measurement-exploratory-analysis-and-data-quality.md).
