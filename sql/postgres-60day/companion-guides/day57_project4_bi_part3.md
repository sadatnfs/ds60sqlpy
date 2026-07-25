# Day 57 — Complex BI Project, Part 3: Trends and Anomalies

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 56 — percentiles and CUBE](day56_project4_bi_part2.md)
- **Artifacts:** [learner SQL](../day57_project4_bi_part3.sql) ·
  [solution reasoning](../solutions/day57_solutions.md) ·
  [executable solution](../solutions/day57_solutions.sql)

## Learning objectives

- Backtest observation-based moving average and calendar-week seasonal naive
  without leakage.
- Compare standard-deviation and median-absolute-deviation anomaly scores.

## Vocabulary and concepts

- **Seasonal naive:** forecast equal to the observation from a fixed seasonal
  lag.
- **MAD:** median absolute deviation, a robust dispersion statistic.
- **Anomaly candidate:** an observation prioritized for investigation, not
  proof of an incident.

## Worked example / walkthrough

Build a complete daily spine before `LAG(revenue, 7)` so the offset means seven
calendar days. Calculate a trailing forecast that excludes the current actual,
then score the same six-month rows. For anomaly output, retain raw revenue,
center, dispersion, and both scores beside the rank.

## Exercises

Complete the prompts in the [learner SQL](../day57_project4_bi_part3.sql). Compare
results with absent no-order days versus explicit zero-revenue days.

## Self-check

- Do forecast windows end before the current actual and use a common scoring
  set?
- Are zero dispersion, rank ties, and synthetic-data limitations explicit?

## Next step

Continue to [Day 58 — capstone ingestion and data quality](day58_final_capstone_part1.md).

## Deep dive and reference

## Project focus

- Compare a seven-observation moving average with a weekly seasonal naive.
- Calculate standard-deviation and median-absolute-deviation scores.
- Rank the strongest recent positive and negative anomaly candidates.

## How the learner script uses the current schema

Daily revenue is `SUM(orders.total_amount)` by order date. The starter shows a
14-prior-observation rolling mean/standard deviation, a global MAD score, and a
seven-prior-observation moving-average forecast with APE.

## Practice — match the learner prompts exactly

1. Replace MA(7) with `LAG(revenue, 7)` seasonal naive and compare MAPE for the
   last six months.
2. Over the last six months, calculate both SD z-score and modified MAD z-score,
   then return the top ten positive and top ten negative anomalies.

## Time-series reasoning

- Build a complete date spine before `LAG(..., 7)` when “seven days ago” must
  mean calendar days; otherwise it means seven observed rows.
- Moving-average windows must exclude the current actual to prevent leakage.
- MAPE excludes zero actuals unless another error definition is chosen.
- MAD is robust to outliers; SD is more sensitive. They are complementary, not
  interchangeable proof of an incident.

## Validation and limits

- Guard zero standard deviation and zero MAD with `NULLIF`.
- State whether no-order days are absent or represented as zero.
- Rank anomaly candidates deterministically and retain both score types.
- Synthetic anomalies are investigation examples, not operational alerts or
  calibrated probabilities.
