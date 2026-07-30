# Day 49 — Finance/Operations Project, Part 1: Revenue Forecasting

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 48 — affinity and attribution](day48_project1_ecommerce_part3.md)
- **Artifacts:** [learner SQL](../day49_project2_finance_part1.sql) ·
  [solution reasoning](../solutions/day49_solutions.md) ·
  [executable solution](../solutions/day49_solutions.sql)

## Learning objectives

- Backtest moving-average and seasonal-naive forecasts without target leakage.
- Compare errors on a common scoring population and disclose sparse history.

## Vocabulary and concepts

- **Backtest:** evaluate a forecast using only information available before each
  historical target.
- **Target leakage:** using the actual target or future information in its
  prediction.
- **MAPE:** mean absolute percentage error, undefined for zero actuals.

## Worked example / walkthrough

At complete monthly grain, compute MA(6) with a frame ending at
`1 PRECEDING`, place it beside actual revenue, and score only months with a
forecast and nonzero actual. Compare seasonal naive on that same scoring set and
retain the number of evaluated months.

## Exercises

Complete these in the [learner SQL](../day49_project2_finance_part1.sql):

1. Backtest MA(6), MA(12), and seasonal naive with MAPE.
2. Produce a 50/50 seasonal/MA(6) forecast.
3. Explain and remove current-row leakage.
4. Build a complete monthly spine before lagging 12 months.
5. Handle zero actuals and report excluded MAPE rows.
6. Compare MAE with MAPE on a low-revenue miss.

Score every model on a common observation window.

## Self-check

- Does every forecast exclude its current actual?
- Are model errors compared over the same months, with excluded zero actuals
  and warm-up periods reported?

## Next step

Continue to [Day 50 — budget variance](day50_project2_finance_part2.md).

## Deep dive and reference

## Project focus

- Build one monthly order-revenue series.
- Backtest moving-average and seasonal-naive forecasts.
- Compare MAPE and inspect a 50/50 blended forecast.

## How the learner script uses the current schema

The starter aggregates `orders.total_amount` by order month, calculates
year-over-year growth with `LAG(..., 12)`, projects future months from last
year's matching month, and shows a trailing three-month average.

## Practice — match the learner prompts exactly

1. Build MA(6) and MA(12) one-step forecasts and compare their MAPEs with a
   12-month seasonal naive.
2. Produce a forecast equal to 50% seasonal naive plus 50% MA(6), and inspect it
   month by month.

## Backtesting reasoning

- Moving windows must end at `1 PRECEDING`; including the current actual leaks
  the answer into its forecast.
- `LAG(revenue, 12)` means the previous 12 result rows. Build a complete month
  calendar first if months can be absent.
- MAPE is undefined when actual revenue is zero; disclose excluded periods and
  consider MAE as a companion metric.
- Compare models over a common scoring window when warm-up history differs.

## Validation and limits

- Return forecast and actual side by side.
- Record the number of scored months for each model.
- The deterministic seed has only a few years of history, so model ranking is a
  learning result, not evidence of forecast reliability.
- A historical backtest does not create a production forecast pipeline.
