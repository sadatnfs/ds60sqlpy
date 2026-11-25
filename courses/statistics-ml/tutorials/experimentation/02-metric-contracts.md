# Metrics are definitions of what gets counted

Tutorial ID: `statistics-exp-002`. Prerequisites: `statistics-exp-001`, `statistics-006`, `statistics-008`. Complete example: [experiment_02.py](examples/experiment_02.py).

## Key terms

- **Metric contract:** A written specification of a metric's unit, numerator, denominator, time window, inclusion rules and interpretation, fixed before analysis.
- **Ratio of totals:** Total value divided by total visits, which implicitly weights each user's own ratio by that user's visit count.
- **Mean of user ratios:** The average of each user's value per visit, which weights users equally and is undefined for users with zero visits.
- **Linearized contribution:** The per-user quantity \((R_i-rV_i)/\bar V\) whose sample standard deviation gives the ratio's standard error while keeping the covariance between value and visits.
- **Noncompensatory constraint:** A limit, such as a reliability guardrail, that no gain on another metric is allowed to offset.

## One product, three denominators

The activity-page experiment has repeated visits within users. Before choosing a metric, write its contract. A contract specifies the unit, numerator, denominator, time window, inclusion rules and interpretation. Otherwise two analysts can produce different correct-looking totals from the same events.

| Metric | Numerator | Denominator | Question |
| --- | --- | --- | --- |
| Value per assigned user | Seven-day user value | All assigned eligible users | Does the assignment policy create more total value? |
| Value per visit | Total value | Total recorded visits | How much value does an observed visit contain? |
| Mean user value-per-visit | Sum of each user's individual ratio | Assigned users with defined ratios | What is the average user's visit efficiency? |
| Conversion | Users with at least one conversion | All assigned users with mature observation | How many assigned users convert? |

All users in this fixture have at least one visit. A real experiment must define zero-visit handling before analysis. Removing zero-visit users because division is inconvenient changes the population. A ratio of totals can include their zero contributions without constructing an undefined individual ratio.

## Derive why two ratios differ

Consider two users with values 2 and 18 and visit counts 1 and 3. The ratio of totals is \((2+18)/(1+3)=5\). The average of user ratios is \((2/1+18/3)/2=4\). The first implicitly weights individual ratios by visit counts; the second weights users equally. Neither is a universally correct replacement for the other.

For independent users, write \(r=\bar R/\bar V\). Linearizing gives the user contribution

\[
\psi_i=\frac{R_i-rV_i}{\bar V},
\qquad \widehat{\operatorname{SE}}(r)=\frac{s_\psi}{\sqrt n}.
\]

The covariance between value and visits is retained inside \(R_i-rV_i\). Treating numerator and denominator as independent discards it. Treating visits as independent observations discards the dependence created by a shared user.

## Read the complete calculation

The fixture's mean value is about 20.744 points per assigned user. The ratio of totals is about 5.279 points per visit, while averaging individual user ratios gives about 6.742. The event-table mean matches the ratio of totals because each event receives its share of the user's total value. The code checks that algebraic relationship and reports a user-level ratio SE around 0.179. It does not assert that event rows provide independent uncertainty.

## A metric gain can hide a total loss

Suppose a page removes low-value visits: total value stays 100 while visits drop from 50 to 40. Value per visit rises from two to 2.5 with no increase in total value. Conversely, attracting exploratory visits may lower the ratio while increasing total useful activity. Show numerator and denominator effects alongside every ratio.

The primary criterion should follow the product decision. Diagnostics explain mechanisms; guardrails specify unacceptable harm. A reliability guardrail might require the upper uncertainty bound for excess failure probability to stay below a prespecified margin. A nonsignificant failure estimate with a wide interval is not evidence of acceptable reliability.

**Answered discussion: Can a weighted composite settle every tradeoff?** It can make a chosen utility rule explicit, but its weights encode values. A gain in engagement can offset reliability harm numerically even when the product owner considers that harm unacceptable. Keep noncompensatory constraints visible.

## Worked example: decompose the ratio by arm

A ratio metric moves when either its numerator or its denominator moves, so print both per arm before reading the ratio. Paste this into [experiment_02.py](examples/experiment_02.py) below `ratio_summary`.

```python prelude=examples/experiment_02.py
users, _, _, _ = experiment_fixture()
for arm, rows in users.groupby("assigned"):
    ratio, se = ratio_summary(rows.value, rows.visits)
    print(
        f"arm {arm}: value/user={rows.value.mean():.3f} "
        f"visits/user={rows.visits.mean():.3f} value/visit={ratio:.3f} (se {se:.3f})"
    )
```

```text
arm 0: value/user=19.952 visits/user=3.825 value/visit=5.216 (se 0.259)
arm 1: value/user=21.535 visits/user=4.033 value/visit=5.339 (se 0.248)
```

Value per assigned user rises by about 1.58 points, roughly 7.9%, while value per visit rises by only about 0.12, roughly 2.4%. The gap comes from the denominator: treatment users happen to record 4.033 visits against 3.825 in control. The fixture generates visits independently of assignment, so that difference is chance, yet it absorbs most of the lift when the analyst reads only the ratio. In a real product, the same arithmetic would mislead in the opposite direction if the redesign genuinely suppressed visits. Reporting value per user, visits per user and their ratio together makes the mechanism visible.

## Worked example: the unit of uncertainty is the user

The event table has many more rows than the assignment table. Treating each row as an independent draw shrinks the standard error without adding information.

```python
users, events, _, _ = experiment_fixture()
ratio, user_se = ratio_summary(users.value, users.visits)
naive_se = events.points.std(ddof=1) / np.sqrt(len(events))
print("events:", len(events), "users:", len(users))
print(f"user-level delta SE {user_se:.3f}; event-row SE {naive_se:.3f}")
```

```text
events: 943 users: 240
user-level delta SE 0.179; event-row SE 0.105
```

Both calculations target the same 5.279 points per visit, but the event-row SE is about 41% smaller. It divides by \(\sqrt{943}\) as if every visit were separately sampled, while all visits from one user share that user's baseline activity; in this fixture every event of a user carries the identical value \(R_i/V_i\). The delta-method contribution \(\psi_i\) keeps one term per user, so its SE reflects 240 independent units. An interval built from 0.105 would cover the population ratio far less often than its nominal level.

## When the ratio estimator breaks down

The linearization is a large-sample approximation. It deteriorates when the denominator total is small, when a few heavy users dominate visits, or when many users have zero visits so the ratio is driven by a handful of units. In those cases compare the delta SE with a user-level bootstrap, as unit 06 does, and inspect how concentrated visits are before trusting either number.

Continue to [instrumentation](03-instrumentation-and-selection.md). Reference: [Trustworthy Online Controlled Experiments, official contents](https://assets.cambridge.org/97811087/24265/toc/9781108724265_toc.pdf).
