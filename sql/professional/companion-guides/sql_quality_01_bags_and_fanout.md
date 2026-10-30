# SQL-QUALITY-01: Bag Reconciliation and Join Fanout

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-quality-01**. The
[launcher guide](../../../docs/one-command-classroom.md) covers first preparation, strict resume and
the saved project selection. No host Python or PostgreSQL installation is
required for this browser route.

1. Read the prerequisite and fixture notes before running the file. Use only
   the local disposable `advanced_sql_training` database. A simple snippet
   such as `SELECT 1;` needs no training-schema reset.
2. Choose **Whole SQL lesson (psql)** for the cataloged learner script. This
   preserves the lesson's reviewed psql directives, relative includes and
   transaction behavior. **SQL snippet** is appropriate for ordinary SQL
   statements, but is not a replacement for an entire script's setup.
3. When the lesson requires the course training data, use the explicit
   preparation action and read its reset acknowledgement. It replaces the
   course-owned `training` schema. Do not reset unrelated data or prepare
   every lesson by habit; stateful sequences have their own ordering.
4. Edit the learner copy in the classroom and save your prediction before
   running. Its whole-script workspace is
   `.learning/sql/sql-quality-01/lesson/workspace/sql/professional/lessons/sql_quality_01_bags_and_fanout.sql`.
   For browser work this path is inside the Docker learning volume, not a
   newly created host folder beside your checkout. The checked-in source
   remains the answer-free starting artifact.
5. Run the whole script and inspect the full transcript. The runner uses
   `psql -X -v ON_ERROR_STOP=1 -f`. SELECT output has columns, rows and a row
   count; DDL/DML has command tags; intentional checks may produce NOTICE
   messages. An unexpected ERROR or nonzero exit is a failure to diagnose,
   even when an earlier query printed plausible values.
6. Verify the lesson's expected grain, ordering, constraints and declared
   transaction or cleanup outcome. Keep required ROLLBACK statements.
   The warehouse sequence and other explicitly stateful exercises explain
   when state is committed. Read saved output without rerunning it when
   reviewing an earlier attempt.

If a relation is missing, inspect the lesson's required fixture and predecessor
rather than guessing a new table definition. If authentication or runtime
readiness fails, use `./classroom status` and the setup guide. Keep credentials
out of SQL, notebooks, screenshots and committed files. Repair the first error
before trusting partial output, and reveal separate solutions only when you
want to compare after an attempt.

### Optional contributor notebook route

For notebook work, deliberately prepare the Linux/WSL contributor environment
from [CONTRIBUTING.md](../../../CONTRIBUTING.md), including a compatible psql client and
the notebook dependencies. Generate this lesson's private workspace through
the maintained CLI:

```sh
uv run --no-sync python scripts/course.py sql notebook sql-quality-01
```

Open the printed notebook path in that environment's JupyterLab. It uses the
same catalog-derived learner-copy layout in that contributor checkout and
executes the complete script through psql. Its host-side state is separate
from the Docker browser's named volume. Follow
[guided SQL notebooks](../../../docs/guided-sql-notebooks.md) for explicit local connection
selection and kernel setup. Notebook generation does not execute SQL or
authorize a reset.

## Level and prerequisites

- **Level:** advanced
- **Direct catalog prerequisites:** [`sql-06`](../../postgres-60day/companion-guides/day06_set_operations.md), [`sql-23`](../../postgres-60day/companion-guides/day23_ctes_intro.md), [`sql-test-01`](sql_test_01_contracts_migrations.md)
- **Artifacts:** [learner SQL](../lessons/sql_quality_01_bags_and_fanout.sql), [solution reasoning](../solutions/sql_quality_01_bags_and_fanout_solutions.md), [executable solution](../solutions/sql_quality_01_bags_and_fanout_solutions.sql).

Direct prerequisites name the required boundary. The fixture setup is supplied; do not mistake its table-definition syntax for extra unstated prerequisite work.

## Learning objectives

- Expose mismatches hidden by equal counts and totals.
- Reconcile both directions while preserving duplicate multiplicity and NULL state.
- Aggregate independent child relations at the parent key before joining them.

## Vocabulary and concepts

"The totals match" is a useful control and a weak equality claim. Two invoice
extracts can have the same number of rows and the same grand total while
disagreeing on individual invoices. One underpayment can cancel another
overpayment. A duplicate delivery can replace another duplicate without
changing the distinct value set. This module turns those counterexamples into
explicit diagnostic queries instead of adding more generic aggregate checks.



- **Bag:** A bag, also called a multiset, is a collection in which a row can occur
more than once. 

- **Set:** A set ignores repeated occurrences. 

- **Multiplicity:** Multiplicity is
the number of occurrences of a particular row value. 

- **Reconciliation:** Reconciliation is
comparing two representations under a declared equality contract and reporting
differences. 

- **Fanout:** Fanout is row multiplication caused by matching a parent row
to several children. 

- **Control total:** A control total is a summary used to detect certain
failures; it is evidence about that summary, not proof of all row contents.

There are two different equality questions. Keyed equality assumes one row
per invoice_id and compares attributes for that key. Bag equality compares
every projected value and its multiplicity, even when no unique source key is
available. Do not casually switch between these questions. A FULL OUTER JOIN
is useful for valid unique keys, but duplicate keys can turn its diagnostic
into a many-to-many join. EXCEPT ALL answers a bag-difference question without
requiring unique identities. Its output grain is one unmatched occurrence,
so repeated output tuples are legitimate evidence, not a formatting error.

## Syntax anatomy and query reasoning

Start by stating the comparison columns, currency, units, time boundary,
missingness policy, and grain. Here amounts are exact numeric values in one
declared currency, with no floating-point tolerance and no conversion. The
two invoice snapshots each have one row per invoice_id. The separate delivery
fixtures intentionally allow duplicate rows. Do not deduplicate them before
comparing, because multiplicity is the fact under investigation.

For keyed comparison, FULL OUTER JOIN retains source-only and target-only
identities as well as matched keys. Test key presence using non-NULL primary
keys, not amount: a present invoice may legitimately have an unknown amount.
`IS DISTINCT FROM` catches both unequal known amounts and a known-to-unknown
transition. With ordinary `<>`, an unknown operand can hide the difference.
Classify missing identities separately from changed attributes.

For bag comparison, `(source EXCEPT ALL target)` reports source excesses.
Reverse the operands to report target excesses. UNION ALL appends the labeled
diagnostics without removing repetitions. Ordinary EXCEPT removes duplicate
result rows and can report no difference for bags with different counts.
Compare compatible types and the same ordered projection on both sides.

Independent child collections require another precaution. An order with two
lines and two payment attempts produces four joined pairs. Summing a line
amount after that join counts each line twice. Summing attempts counts each
attempt twice too. Aggregate lines by order_id, aggregate attempts separately
by order_id, then join those one-row-per-order results to orders. DISTINCT
on money cannot repair this: two legitimate lines may have equal amounts.

## Worked example / walkthrough

Run these in the complete learner file so the temporary fixture and transaction are present. The fixture values are fixed; the examples never depend on the current clock. Predict each result before running it.

### Example 1: Equal summaries conceal changed identities

```sql
SELECT
  'source' AS origin,
  count(*) AS row_count,
  sum(amount) AS amount_total
FROM
  quality_source
UNION ALL
SELECT
  'target',
  count(*),
  sum(amount)
FROM
  quality_target
ORDER BY
  origin;
```

Each branch collapses four invoice rows into one summary row. Both branches report 4 and 230. The source includes invoice 4, the target includes invoice 5, and invoice 2 has changed. The matching grand totals are real but insufficient. No claim about individual invoice equality follows from this summary. Keep this control because it catches other failures, then add more discriminating evidence.

**Expected:** Two summary rows keyed by origin, columns origin, row_count, amount_total. Both totals equal 230 and both counts equal 4.

### Example 2: Aggregate separate children before joining

```sql
WITH lines AS (
  SELECT
    order_id,
    sum(amount) AS line_total
  FROM
    quality_lines
  GROUP BY
    order_id
),
attempts AS (
  SELECT
    order_id,
    sum(amount) AS attempted_total
  FROM
    quality_attempts
  GROUP BY
    order_id
)
SELECT
  o.order_id,
  COALESCE(l.line_total, 0) AS line_total,
  COALESCE(a.attempted_total, 0) AS attempted_total
FROM
  quality_orders AS o
  LEFT JOIN lines AS l ON l.order_id = o.order_id
  LEFT JOIN attempts AS a ON a.order_id = o.order_id
ORDER BY
  o.order_id;
```

The CTEs each reduce a child collection to one row per order_id before they meet. Their LEFT joins therefore preserve the three parent identities. An order without children receives zero under this lesson's explicit empty-child policy. Attempted payment total is not revenue: a retry is a separate attempt. Here the source amounts are NOT inferred from one another, so the two metrics remain independently meaningful.

**Expected:** Three order rows; columns order_id, line_total, attempted_total: (1,100,200),(2,50,50),(3,0,0).

## Exercises

Attempt these in order in the ignored working copy, before its final rollback. Write the output grain and a prediction before execution. Compare the actual identities and values with each contract. A query merely running is not sufficient evidence. Hints are optional and leave the answer construction to you.

1. **Disprove summary equality.**

   **Inputs/evidence:** For sql-quality-01 Exercise 1, Compare quality_source and quality_target using one row per origin with origin, row_count, amount_total. Explain one concrete mismatch the summary cannot reveal.

   **Expected result/shape:** For sql-quality-01 Exercise 1, Two summary rows keyed by origin, columns origin, row_count, amount_total; final ORDER BY origin. Both counts are 4 and totals are 230 despite differing invoice contents.

   **Verify:** For sql-quality-01 Exercise 1, Inspect changed invoice 2 and the replacement of identity 4 by 5 while confirming both summaries still report four rows and amount_total 230.

   **Progressive hint:** Keep the aggregate as a control, then inspect invoice 2 and identities 4 and 5.

2. **Report keyed mismatches in both directions.**

   **Inputs/evidence:** For sql-quality-01 Exercise 2, Use FULL OUTER JOIN on invoice_id and NULL-safe amount comparison. Return invoice_id, source_amount, target_amount, difference_kind with missing_target, missing_source, or changed.

   **Expected result/shape:** For sql-quality-01 Exercise 2, Three invoice rows keyed by invoice_id, columns invoice_id, source_amount, target_amount, difference_kind; final ORDER BY invoice_id: 2 changed (50,40), 4 missing_target (80,NULL), 5 missing_source (NULL,90).

   **Verify:** For sql-quality-01 Exercise 2, Compare exact diagnostics for invoices 2,4,5 with kinds changed,missing_target,missing_source and amounts (50,40),(80,NULL),(NULL,90). Matching keys 1 and 3 are absent.

   **Progressive hint:** Use key presence to classify an absent row before comparing its amount.

3. **Preserve duplicate multiplicity.**

   **Inputs/evidence:** For sql-quality-01 Exercise 3, Compare quality_sent and quality_received as bags on invoice_id, amount using two EXCEPT ALL branches labeled sent_only and received_only. Explain why ordinary EXCEPT would miss this difference.

   **Expected result/shape:** For sql-quality-01 Exercise 3, Two unmatched occurrence rows, columns direction, invoice_id, amount; final ORDER BY direction, invoice_id, amount: received_only (2,50), sent_only (1,100). An occurrence has no independent ID; (direction,invoice_id,amount) is a value tuple and may repeat in larger bags.

   **Verify:** For sql-quality-01 Exercise 3, Count one sent-only occurrence (1,100) and one received-only occurrence (2,50). Repeat with ordinary EXCEPT and explain why its empty difference hides the changed multiplicities.

   **Progressive hint:** Run both directions before adding UNION ALL; do not insert DISTINCT.

4. **Repair independent-child fanout.**

   **Inputs/evidence:** For sql-quality-01 Exercise 4, Return order_id, line_total, attempted_total for all quality_orders. Aggregate quality_lines and quality_attempts separately before joining. Diagnose the raw two-child join on order 1.

   **Expected result/shape:** For sql-quality-01 Exercise 4, Three order rows, columns order_id, line_total, attempted_total; final ORDER BY order_id: (1,100,200),(2,50,50),(3,0,0). The raw order-1 join has four pairs and incorrectly sums lines to 200.

   **Verify:** For sql-quality-01 Exercise 4, Check all three order_id values survive, reconcile each metric with a separate child-only sum, and expose the raw order-1 join with four pairs and incorrect line sum 200.

   **Progressive hint:** A parent with two rows in each independent child has 2 x 2 matched pairs.

5. **Detect a missingness transition.**

   **Inputs/evidence:** For sql-quality-01 Exercise 5, Compare a source invoice (6,NULL::numeric) with target invoice (6,0::numeric). Return invoice_id, source_amount, target_amount only when the amounts differ under a missingness-sensitive contract.

   **Expected result/shape:** For sql-quality-01 Exercise 5, One invoice row keyed by invoice_id, columns invoice_id, source_amount, target_amount; final ORDER BY invoice_id: (6,NULL,0). The keyed row exists on both sides.

   **Verify:** For sql-quality-01 Exercise 5, Inspect the one row with NULL source and known zero target. Coalescing both sides to zero hides the mismatch, while ordinary inequality fails to qualify it.

   **Progressive hint:** Replacing both values with zero before comparison destroys this diagnostic.

6. **Gate a keyed comparison on valid identity.**

   **Inputs/evidence:** For sql-quality-01 Exercise 6, For quality_sent, return invoice_id, occurrences only for duplicate keys. Explain why a keyed reconciliation must stop before joining this fixture to another nonunique extract.

   **Expected result/shape:** For sql-quality-01 Exercise 6, One diagnostic row keyed by invoice_id, columns invoice_id, occurrences; final ORDER BY invoice_id: (1,2). No amount is used as an identity.

   **Verify:** For sql-quality-01 Exercise 6, Require exactly duplicate-key diagnostic (invoice_id=1,occurrences=2). This nonempty result prevents interpreting a later keyed join as one diagnostic per invoice.

   **Progressive hint:** Validate the key at the incoming extract grain before validating its attributes.

## Self-check

- Which equality claim can matching count and sum support?
- When does EXCEPT ALL teach something that EXCEPT cannot?
- Why is SUM(DISTINCT amount) an unsafe repair for independent-child fanout?

Keep your actual query and transcript. Explain one incorrect alternative and the exact fixture row that exposes it. A passing worked example does not prove an unattempted exercise. Revisit a failed prediction after taking a break, then answer the retrieval questions without looking at the code.

## Common pitfalls

- If totals agree but customer invoices disagree, inspect keyed FULL OUTER JOIN diagnostics before celebrating a passing grand total.

- If a reconciliation suddenly contains many rows per key, validate input key uniqueness; DISTINCT on the output hides the cause.

- If an order total doubles after adding a new child join, count child combinations and aggregate each collection independently.

## Next step

Use `sql-scale-01` to preserve correctness while traversing large changing inputs.

Concrete next target: [Cursor pagination and bounded batches](sql_scale_01_cursors_and_batches.md).

## Reference

The course works offline after setup. These optional official references describe the PostgreSQL semantics used here:

- [PostgreSQL 16 documentation](https://www.postgresql.org/docs/16/queries-union.html)

## Ask an AI tutor about this lesson

The lesson and expected observations are sufficient offline. For optional coaching, copy:

```text
Tutor me through sql-quality-01: Bag Reconciliation and Join Fanout using the checked-in $guide-ds60sqlpy-learning skill.
Guide: sql/professional/companion-guides/sql_quality_01_bags_and_fanout.md
Answer-free learner: sql/professional/lessons/sql_quality_01_bags_and_fanout.sql
Direct prerequisite boundary: sql-06, sql-23, sql-test-01.
Teach at the advanced level, defining each new term before relying on it.
Focus on Expose mismatches hidden by equal counts and totals. Reconcile both directions while preserving duplicate multiplicity and NULL state.
Use the guide -> explain -> predict -> my attempt -> one hint at a time -> evidence review -> retrieval loop.
Keep solutions/ closed until I ask after an honest attempt. Do not read, quote,
or summarize the official solution before that boundary.
Prefer Whole SQL lesson (psql) and its ignored .learning/sql/sql-quality-01/ working copy.
Run live SQL only against the local disposable advanced_sql_training database.
Never request a password or point a reset at shared or valuable data.
Ask for my actual SQL and complete psql transcript, compare identities and values
with each Expected contract, and explain the first discrepancy before editing.
Done when my attempted exercises have inspectable matching evidence and I can
answer the guide's retrieval questions and a small transfer question in my own words.
```
