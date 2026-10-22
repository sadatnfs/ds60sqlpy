# SQL-QUALITY-01: solution reasoning

Use this after an honest attempt at the [guide](../companion-guides/sql_quality_01_bags_and_fanout.md)
and [learner script](../lessons/sql_quality_01_bags_and_fanout.sql). The separate
[executable solution](sql_quality_01_bags_and_fanout_solutions.sql) runs all six answers and independent
fail-fast checks with `psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/solutions/sql_quality_01_bags_and_fanout_solutions.sql`.
It uses only temporary fixtures, starts a transaction, and ends in rollback.
It must exit 0 with no contract failures. Each answer has a savepoint so an
experiment cannot silently change a later exercise's starting conditions.
The assertion helper treats false and unknown as failures, rather than allowing
a NULL assertion to pass accidentally. Keep the original fixture unchanged
when comparing your work so the stated identities remain a reliable oracle.

The code below is the answer for each numbered prompt, followed by its
reasoning. Inspect the first discrepancy in your own transcript before reading
a different answer. A solution is one defensible implementation of this contract;
an alternative is valid if its identities, values, missingness, ordering, and
transaction behavior match. Tests constrain the actual returned relation,
rather than assuming a familiar-looking query must be right.

## Exercise solutions

## Exercise 1: Disprove summary equality

```sql
SELECT 'source' AS origin, count(*) AS row_count, sum(amount) AS amount_total FROM quality_source
UNION ALL SELECT 'target', count(*), sum(amount) FROM quality_target ORDER BY origin;
```

Each input has a valid unique invoice key and four rows. The summary loses invoice identity and attribute distribution, so it cannot distinguish the target's ten-unit reduction on invoice 2 from its larger replacement invoice. This is a deliberate negative control for the idea that one matching number proves correctness. The assertion checks that the deceptive equality actually exists; a counterexample with different totals would not demonstrate this failure mode. Retain the summary in a real test suite because it is cheap and useful, but phrase its conclusion narrowly: counts and aggregate amounts match. The next exercise adds row-level evidence needed for a stronger statement.

**Inputs/evidence:** For sql-quality-01 Exercise 1, Compare quality_source and quality_target using one row per origin with origin, row_count, amount_total. Explain one concrete mismatch the summary cannot reveal.

**Expected result/shape:** For sql-quality-01 Exercise 1, Two summary rows keyed by origin, columns origin, row_count, amount_total; final ORDER BY origin. Both counts are 4 and totals are 230 despite differing invoice contents.

**Verify:** For sql-quality-01 Exercise 1, Inspect changed invoice 2 and the replacement of identity 4 by 5 while confirming both summaries still report four rows and amount_total 230.

## Exercise 2: Report keyed mismatches in both directions

```sql
SELECT COALESCE(s.invoice_id,t.invoice_id) AS invoice_id,
       s.amount AS source_amount, t.amount AS target_amount,
       CASE WHEN s.invoice_id IS NULL THEN 'missing_source'
            WHEN t.invoice_id IS NULL THEN 'missing_target' ELSE 'changed' END AS difference_kind
FROM quality_source AS s FULL OUTER JOIN quality_target AS t USING (invoice_id)
WHERE s.invoice_id IS NULL OR t.invoice_id IS NULL OR s.amount IS DISTINCT FROM t.amount
ORDER BY invoice_id;
```

FULL OUTER JOIN retains all keys, so neither missing side disappears before diagnosis. COALESCE chooses the available identity for the output without replacing a measurement. The CASE tests source and target key presence first because a present amount could be NULL. Only matched keys reach the changed classification. The WHERE condition includes missing keys and NULL-safe attribute differences. The assertion checks both the three identities and their classification order, so a query that notices only changed invoice 2 cannot pass. This keyed method depends on the declared primary keys; if an upstream staging extract lacks that guarantee, validate uniqueness before interpreting its join as one diagnostic row per invoice.

**Inputs/evidence:** For sql-quality-01 Exercise 2, Use FULL OUTER JOIN on invoice_id and NULL-safe amount comparison. Return invoice_id, source_amount, target_amount, difference_kind with missing_target, missing_source, or changed.

**Expected result/shape:** For sql-quality-01 Exercise 2, Three invoice rows keyed by invoice_id, columns invoice_id, source_amount, target_amount, difference_kind; final ORDER BY invoice_id: 2 changed (50,40), 4 missing_target (80,NULL), 5 missing_source (NULL,90).

**Verify:** For sql-quality-01 Exercise 2, Compare exact diagnostics for invoices 2,4,5 with kinds changed,missing_target,missing_source and amounts (50,40),(80,NULL),(NULL,90). Matching keys 1 and 3 are absent.

## Exercise 3: Preserve duplicate multiplicity

```sql
SELECT 'sent_only' AS direction, invoice_id, amount FROM (
 SELECT invoice_id,amount FROM quality_sent EXCEPT ALL SELECT invoice_id,amount FROM quality_received
) AS missing
UNION ALL
SELECT 'received_only', invoice_id, amount FROM (
 SELECT invoice_id,amount FROM quality_received EXCEPT ALL SELECT invoice_id,amount FROM quality_sent
) AS extra
ORDER BY direction,invoice_id,amount;
```

The sent bag contains two occurrences of invoice 1 and one of invoice 2; the received bag has the opposite multiplicities. Their distinct sets are equal, but one invoice-1 occurrence is missing and one invoice-2 occurrence is extra. EXCEPT ALL subtracts occurrence counts while ordinary EXCEPT would collapse them. Labeling direction prevents a reader from confusing missing with extra. UNION ALL preserves every diagnostic occurrence. The assertion verifies two total rows and one of each precise value and direction. Do not claim the output tuple is a unique event identity: repeated unmatched occurrences can legitimately share every selected value. Real occurrence identity requires a separately supplied delivery key.

**Inputs/evidence:** For sql-quality-01 Exercise 3, Compare quality_sent and quality_received as bags on invoice_id, amount using two EXCEPT ALL branches labeled sent_only and received_only. Explain why ordinary EXCEPT would miss this difference.

**Expected result/shape:** For sql-quality-01 Exercise 3, Two unmatched occurrence rows, columns direction, invoice_id, amount; final ORDER BY direction, invoice_id, amount: received_only (2,50), sent_only (1,100). An occurrence has no independent ID; (direction,invoice_id,amount) is a value tuple and may repeat in larger bags.

**Verify:** For sql-quality-01 Exercise 3, Count one sent-only occurrence (1,100) and one received-only occurrence (2,50). Repeat with ordinary EXCEPT and explain why its empty difference hides the changed multiplicities.

## Exercise 4: Repair independent-child fanout

```sql
WITH lines AS (SELECT order_id,sum(amount) AS line_total FROM quality_lines GROUP BY order_id),
attempts AS (SELECT order_id,sum(amount) AS attempted_total FROM quality_attempts GROUP BY order_id)
SELECT o.order_id,COALESCE(l.line_total,0) AS line_total,COALESCE(a.attempted_total,0) AS attempted_total
FROM quality_orders AS o LEFT JOIN lines AS l USING(order_id) LEFT JOIN attempts AS a USING(order_id)
ORDER BY o.order_id;
```

Each CTE establishes uniqueness by order_id before the join. LEFT joins retain order 3, whose lack of child rows is explicitly displayed as zero for these additive metrics. Order 1 has 100 in lines and 200 in attempts because two attempts are separate facts, not a duplicated order value. A naive joined sum repeats each line once per attempt. SUM(DISTINCT amount) is not a valid generic repair because separate legitimate lines can share a price. The assertion tests all parent identities and both independent totals, making a plausible-looking single metric insufficient. Add source child sums as independent controls when transferring the pattern to more child collections.

**Inputs/evidence:** For sql-quality-01 Exercise 4, Return order_id, line_total, attempted_total for all quality_orders. Aggregate quality_lines and quality_attempts separately before joining. Diagnose the raw two-child join on order 1.

**Expected result/shape:** For sql-quality-01 Exercise 4, Three order rows, columns order_id, line_total, attempted_total; final ORDER BY order_id: (1,100,200),(2,50,50),(3,0,0). The raw order-1 join has four pairs and incorrectly sums lines to 200.

**Verify:** For sql-quality-01 Exercise 4, Check all three order_id values survive, reconcile each metric with a separate child-only sum, and expose the raw order-1 join with four pairs and incorrect line sum 200.

## Exercise 5: Detect a missingness transition

```sql
WITH s(invoice_id,amount) AS (VALUES (6,NULL::numeric)), t(invoice_id,amount) AS (VALUES (6,0::numeric))
SELECT s.invoice_id,s.amount AS source_amount,t.amount AS target_amount
FROM s JOIN t USING(invoice_id) WHERE s.amount IS DISTINCT FROM t.amount ORDER BY s.invoice_id;
```

The identity matches, so the difference concerns the value's state rather than a missing invoice. IS DISTINCT FROM treats unknown and known zero as different, while ordinary inequality would yield unknown and fail the filter. COALESCE(amount,0) on both sides would incorrectly make the rows equal. The assertion explicitly requires a NULL source amount and zero target amount, which protects the diagnostic semantics. Financial or measurement reconciliation must declare whether missingness matters instead of inheriting a display fallback from another report. This example does not assert that every domain should reject such a transition; it demonstrates the equality policy the exercise explicitly chose.

**Inputs/evidence:** For sql-quality-01 Exercise 5, Compare a source invoice (6,NULL::numeric) with target invoice (6,0::numeric). Return invoice_id, source_amount, target_amount only when the amounts differ under a missingness-sensitive contract.

**Expected result/shape:** For sql-quality-01 Exercise 5, One invoice row keyed by invoice_id, columns invoice_id, source_amount, target_amount; final ORDER BY invoice_id: (6,NULL,0). The keyed row exists on both sides.

**Verify:** For sql-quality-01 Exercise 5, Inspect the one row with NULL source and known zero target. Coalescing both sides to zero hides the mismatch, while ordinary inequality fails to qualify it.

## Exercise 6: Gate a keyed comparison on valid identity

```sql
SELECT invoice_id,count(*) AS occurrences FROM quality_sent GROUP BY invoice_id HAVING count(*)>1 ORDER BY invoice_id;
```

GROUP BY collects occurrences by the proposed key and HAVING retains keys with more than one occurrence. This diagnostic has one row per invalid invoice key, even though its input bag intentionally has no uniqueness guarantee. Finding invoice 1 twice invalidates the premise needed for a one-to-one keyed comparison. Stop that comparison and either repair upstream data under an approved rule or choose a bag contract when repeated records are meaningful. Blind DISTINCT would decide the policy without evidence. The assertion verifies exactly invoice 1 with multiplicity two. A useful publication gate requires this diagnostic to be empty before applying keyed equality, then checks both missing keys and attribute differences.

**Inputs/evidence:** For sql-quality-01 Exercise 6, For quality_sent, return invoice_id, occurrences only for duplicate keys. Explain why a keyed reconciliation must stop before joining this fixture to another nonunique extract.

**Expected result/shape:** For sql-quality-01 Exercise 6, One diagnostic row keyed by invoice_id, columns invoice_id, occurrences; final ORDER BY invoice_id: (1,2). No amount is used as an identity.

**Verify:** For sql-quality-01 Exercise 6, Require exactly duplicate-key diagnostic (invoice_id=1,occurrences=2). This nonempty result prevents interpreting a later keyed join as one diagnostic per invoice.

## Cleanup and evidence boundary

The final rollback removes every temporary table, helper function, index, and modeled change. Running this file twice starts from the same fixture and should produce the same logical evidence. No extension, external dataset, current timestamp, or administrator capability is required. For the optional two-session concurrency lab, use its separate explicit cleanup because that fixture is deliberately committed; the default script never prepares that shared state. A static content check can validate contracts and file structure, while only a live PostgreSQL transcript validates SQL execution. Retain that distinction when reporting completion.
