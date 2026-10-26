# Metrics are definitions of what gets counted

Tutorial ID: `statistics-exp-002`. Prerequisites: `statistics-exp-001`, `statistics-006`, `statistics-008`. Complete example: [experiment_02.py](examples/experiment_02.py).

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

Continue to [instrumentation](03-instrumentation-and-selection.md). Reference: [Trustworthy Online Controlled Experiments, official contents](https://assets.cambridge.org/97811087/24265/toc/9781108724265_toc.pdf).
