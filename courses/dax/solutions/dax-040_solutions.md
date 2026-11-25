# dax-040: explained reference and practice reasoning

Check that the reference counts eligibility from CohortMember and activity with DISTINCTCOUNT of MemberKey, and that February's age-one result is BLANK. Your draft should name which member makes each half. Read it beside the [reference source](dax-040_reference.dax); the [study guide](../STUDY-GUIDE.md#answers-and-references) explains how the sidecar binds it to the model.

## Worked-case reconciliation

### Case A: January cohort at one-month age

Analytics cohort population; January entrants 100/200; activity observed through February 2025.

| EligibleMembers | ActiveAtEntry | ActiveAtAgeOne | RetentionAtAgeOne |
| --- | --- | --- | --- |
| 2 | 2 | 1 | 0.5 |

This denominator is the entry cohort, not the subset observed active in a later month. Filtering to active members before counting eligibility would inflate retention.

- Both January members remain in the eligible denominator.
- Both are active in January, but only 100 is active in February.
- One-month retention is 1/2, regardless of how many events member 100 generated.

### Case B: A newer cohort has unavailable follow-up

February entrants 300/400; March follow-up is outside the declared observed months.

| EligibleMembers | ActiveAtEntry | EntryActivityRate | RetentionAtAgeOne |
| --- | --- | --- | --- |
| 2 | 1 | 0.5 | BLANK |

The two 50-percent values in the lesson have different ages and meanings. A matrix must expose both cohort month and observation age.

- Both members are enrolled, but only 300 has February activity.
- Entry activity is 1/2.
- Month-one retention asks about March, so the coverage guard returns BLANK rather than an invented zero.

## Explained practice answers

### Exercise 1

Predict January retention if member 100 has three February events.

Retention stays 1/2. An event-count numerator would incorrectly inflate it.

**Why it fits this model:** Retention counts retained members, not events. DISTINCTCOUNT(Activity[MemberKey]) counts member 100 once however many February rows exist.

**Tempting mistake:** Using COUNTROWS(Activity) for the numerator gives 3 / 2 = 1.5, a retention rate above 100 percent.

**How to confirm:** With three February events for member 100, ActiveAtAgeOne stays 1 and RetentionAtAgeOne stays 0.5.

### Exercise 2

Add a February event for member 200.

Both January members would be active at age one, so retention becomes 1.

**Why it fits this model:** The denominator is the January cohort (100 and 200), fixed at entry. A February event for 200 adds to the numerator only.

**Tempting mistake:** Counting the new event as a new member, or letting the denominator follow the activity, gives a ratio that is no longer defined by the cohort.

**How to confirm:** ActiveAtAgeOne becomes 2 with EligibleMembers still 2, so retention is 1.

### Exercise 3

Write a cohort metric contract.

For this fixture: enrolled members by signup month, any observed activity in the target calendar month, distinct member count, full enrollment denominator and a coverage guard.

**Why it fits this model:** Each part of the contract has a number here: cohorts by CohortMonth (202501 for 100 and 200), activity as any Activity row in the target month, a distinct member count, and observation through 202502.

**Tempting mistake:** Defining the cohort by first activity instead of enrollment. A member with no activity would never enter the denominator.

**How to confirm:** The contract reproduces case A (2 eligible, 1 active, 0.5) and case B (BLANK at age one).

### Exercise 4

Diagnose dropping inactive member 400 before calculating the February entry rate.

It would turn 1/2 into 1/1 and conceal inactive eligible members.

**Why it fits this model:** Members 300 and 400 enrolled in February. Only 300 was active, so the February entry activity rate is 1 / 2.

**Tempting mistake:** Removing member 400 because it has no activity makes the rate 1 / 1. Filtering on the outcome removes the evidence it should measure.

**How to confirm:** Case B returns EligibleMembers 2 and EntryActivityRate 0.5; COUNTROWS(CohortMember) must not depend on Activity.

### Exercise 5

Explain why 202512 + 1 is not a valid next-month calculation.

It gives 202513. Use a date-aware calendar mapping or EDATE with explicit period membership.

**Why it fits this model:** MonthKey is a YYYYMM label. Adding 1 works inside a year, 202501 to 202502, but gives 202513 after December.

**Tempting mistake:** Writing the next-month filter as MonthKey + 1 because it works for both cohorts here. It fails at the first year boundary.

**How to confirm:** Derive the next month from a date: EDATE(DATE(2025, 12, 1), 1) is 2026-01-01, giving 202601 through 'Date'[MonthKey].

### Exercise 6

Transfer the coverage rule to survival follow-up.

Retain observation time and censoring status; choose an estimator matching those assumptions rather than zero-filling future outcomes.

**Why it fits this model:** Survival needs follow-up time and censoring. The February cohort has no month after entry in the observed range, so its members are censored, not lost.

**Tempting mistake:** Counting members 300 and 400 as churned at age one gives 0 / 2 retention, which conflicts with case B's BLANK.

**How to confirm:** Record each member's observed months; the February cohort contributes entry month only, and an estimator such as Kaplan-Meier uses that.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
