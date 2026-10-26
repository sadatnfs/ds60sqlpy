# A complete experiment, from question to decision

This twelve-unit tutorial develops one synthetic activity-page experiment and
then changes its design for factorial, network and time-block questions. All
answers and programs are visible. There are no exams or hidden solutions.

1. [Assignment and estimand](01-question-and-estimand.md)
2. [Metric contracts](02-metric-contracts.md)
3. [Instrumentation and selection](03-instrumentation-and-selection.md)
4. [Power and duration](04-power-and-duration.md)
5. [A/A and integrity](05-aa-and-integrity.md)
6. [Fixed-horizon inference](06-fixed-horizon-analysis.md)
7. [CUPED and adjusted uncertainty](07-cuped-and-adjustment.md)
8. [Multiplicity and sequential monitoring](08-monitoring-and-multiplicity.md)
9. [Replicated factorial analysis](09-factorial-analysis.md)
10. [Interference and saturation](10-interference-and-saturation.md)
11. [Switchbacks and carryover](11-switchbacks-and-carryover.md)
12. [Ramping and a decision memo](12-ramping-and-decision-memo.md)

## Shared offline fixture contract

Every self-contained example that uses the product data reconstructs the same
240-user fixture with a fixed local generator. The seed stabilizes teaching
observations; it does not replace a real randomization system. The durable
definition is `experiment_fixture` in
[the casebook source](../authoring/experiment_casebook.py). The standalone pads
embed their required helpers so copying one program into the classroom does
not depend on sibling imports or an undeclared file mount.

| Table/field | Meaning and constraints |
| --- | --- |
| User `unit` | Unique assigned user; independent unit for the basic model |
| `assigned` | Exactly 120 control and 120 treatment labels from complete randomization |
| `baseline` | Pretreatment activity signal, uniformly distributed between -2 and 2 |
| `trigger` | Pretreatment opportunity for four of every five users |
| `value` | Seven-day total synthetic value points; treatment adds two for opportunity users |
| `visits` | Positive visit count; generated independently of assignment in this basic fixture |
| `converted` | Binary user conversion, with probability .20 plus .04 for treated opportunity users |
| `device` | Fixed mobile/desktop grouping for instrumentation diagnosis |
| `age_days` | Available follow-up for the maturity illustration, not an outcome-based exclusion |
| Event `event_id` | Unique event identity; duplicate copies model replay |
| Event `unit`, `points` | Many events per user whose points sum to that user's total |

The latent untreated values and treatment effects are retained only as a
synthetic oracle. They would not both be observed in a real experiment.
Continuous-value and binary-conversion mechanisms are separate. Units 08 to 12
explicitly introduce additional small worlds to isolate monitoring, factorial,
network, carryover and novelty mechanisms. Their assumptions are not inferred
from the basic fixture.

Programs require NumPy, pandas, SciPy and statsmodels already declared by the
scientific environment. No network, account, service, dataset download or
optional package is required. Read the guide, open its worked example in the
classroom's Python pad, and run the complete file. Output labels identify the
unit and report estimates or invariants. A successful run verifies those
bounded calculations, not the validity of a future real experiment.

Continue with the [statistical learning tutorials](../learning/README.md) or
the [scientific case studies](../science/README.md). Return to the
[original forty-chapter book](../../README.md).
