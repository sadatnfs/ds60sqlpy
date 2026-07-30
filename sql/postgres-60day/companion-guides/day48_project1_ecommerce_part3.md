# Day 48 — E-commerce Project, Part 3: Affinity and Attribution

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 47 — cohort retention](day47_project1_ecommerce_part2.md)
- **Artifacts:** [learner SQL](../day48_project1_ecommerce_part3.sql) ·
  [solution reasoning](../solutions/day48_solutions.md) ·
  [executable solution](../solutions/day48_solutions.sql)

## Learning objectives

- Count each undirected basket pair once per order.
- Attribute a purchase event across distinct qualifying campaigns under an
  explicit lookback rule.

## Vocabulary and concepts

- **Market basket:** the distinct products associated with one order.
- **Attribution window:** the time interval in which a touch can qualify for
  conversion credit.
- **Fractional credit:** one conversion divided across several qualifying
  touches or campaigns.

## Worked example / walkthrough

Deduplicate products within each order, self-join with
`a.product_id < b.product_id`, and count orders per pair. For attribution,
deduplicate campaigns per purchase before dividing one credit by the distinct
campaign count; verify allocated credit sums to one for every assisted purchase.

## Exercises

Complete these in the [learner SQL](../day48_project1_ecommerce_part3.sql):

1. Calculate seven-day assisted conversions.
2. Allocate equal fractional multi-touch credit.
3. Predict repeated-campaign behavior at touch versus campaign grain.
4. Calculate product-pair support, bidirectional confidence, and lift.
5. Assign a touch only to the next purchase.
6. Add a direct bucket and reconcile credit to eligible purchases.

Test touches exactly at both seven-day boundaries.

## Self-check

- Are reversed pairs, self-pairs, and repeat quantities excluded as intended?
- Does fractional credit reconcile to assisted conversions without implying
  causal impact?

## Next step

Continue to [Day 49 — revenue forecasting](day49_project2_finance_part1.md).

## Deep dive and reference

## Project focus

- Form undirected market-basket product pairs.
- Count campaign-assisted purchase events in a seven-day lookback.
- Allocate equal fractional credit across distinct qualifying campaigns.

## How the learner script uses the current schema

The starter deduplicates products within each order and pairs them with
`a.product_id < b.product_id`. It also extracts campaign from
`events.metadata->>'campaign'` and demonstrates each customer's first and last
touch by `events.event_time`.

The setup provides event types `page_view`, `add_to_cart`, `checkout`,
`purchase`, and `support`. It has no separate sessions or experiment assignment
table.

## Practice — match the learner prompts exactly

1. For every `purchase` event, find non-purchase campaign touches for the same
   customer from seven days before the purchase up to, but not including, the
   purchase timestamp. Count distinct assisted purchases by campaign.
2. Deduplicate repeated campaign touches per purchase, divide one conversion
   equally across its distinct campaigns with a window count, and sum
   fractional credit by campaign.

## Attribution reasoning

- The conversion anchor is a purchase event, not an order. State that definition
  before comparing results with order revenue.
- Assisted counts are not additive because one purchase can have several
  assisting campaigns.
- Equal credit for a qualifying purchase should sum to exactly one across its
  distinct campaigns.
- Decide whether missing campaign metadata, represented as `none`, should
  receive credit.

## Validation and limits

- Enforce `product_id` ordering to avoid self-pairs and reversed duplicates.
- The exercise does not establish causal marketing impact.
- The seven-day half-open window needs explicit boundary tests.
- Without session IDs, do not imply session-level journeys.
