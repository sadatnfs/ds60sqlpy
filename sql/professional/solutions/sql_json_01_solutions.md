# sql-json-01: Explained JSON_TABLE solutions

Attempt the [lesson](../companion-guides/sql_json_01_json_table.md) before
comparing these references. The [complete executable solution](sql_json_01_solutions.sql)
creates the four-document temporary fixture and actual typed item views, checks
every answer against independently specified rows or values, and rolls back.
No external extension, service or permanent table is required.

## Exercise 1: Distinguish child rows from preserved parent rows

**Inputs:** For sql-json-01 Exercise 1, inspect document IDs 1, 2 and 3 in j17_practice_documents. They contain two items, an empty items array and an absent items field respectively.
**Expected result/shape:** For sql-json-01 Exercise 1, cROSS yields two item rows; LEFT yields four outer-preserving rows. Display document_id, item_no, sku ordered by document_id, item_no. Actual child identity is (document_id,item_no); documents 2 and 3 have NULL item positions in the LEFT result.
**Verify:** For sql-json-01 Exercise 1, count non-NULL item_no independently and inspect the original field presence and type. A preserved outer placeholder is not an item, and empty and absent arrays are different source states.

The first three documents contain two items, an explicitly empty array and an
absent array. CROSS expansion produces only two item rows. LEFT expansion
preserves all parent identities and produces four rows: two actual items plus
one null-extended placeholder for each unmatched document.

```sql
SELECT d.document_id,
       d.payload ? 'items' AS items_field_present,
       jsonb_typeof(d.payload->'items') AS items_type
FROM j17_documents AS d
WHERE d.document_id <= 3
ORDER BY d.document_id;
```

This inspection keeps the source meaning visible. Document two has a declared
array with zero entries. Document three does not have the field. The projected
absence of an item row alone cannot distinguish them. The reference checks the
actual CROSS count of two and LEFT count of four, then shows source field
presence and type. Do not replace the missing array with an assumed empty array
unless that is an explicit producer policy.

**Verify:** Compare matched item positions with parent IDs rather than using
the number of LEFT result rows as an item count.

## Exercise 2: Produce the actual typed item relation

**Inputs:** For sql-json-01 Exercise 2, project every declared items array in the four-document fixture. Missing qty defaults to one, explicit JSON null remains unknown, and prices use the declared exact numeric type.
**Expected result/shape:** For sql-json-01 Exercise 2, display document_id, item_no, sku, qty, unit_price ordered by document_id, item_no as (1,1,P,2,5), (1,2,Q,1,3), (4,1,R,NULL,7), (4,2,S,1,2), one row per (document_id,item_no).
**Verify:** For sql-json-01 Exercise 2, compare all projected values with the original array entries and assert four unique position pairs. R retains unknown quantity; S receives the declared absence default.

The reference view `j17_lines` uses the lesson's `JSON_TABLE` column definitions:
one ordinal position, text SKU, integer quantity and exact numeric unit price.
The quantity policy defaults an empty path to one and rejects conversion errors.

```sql
SELECT document_id,item_no,sku,qty,unit_price
FROM j17_lines
ORDER BY document_id,item_no;
```

The four rows are document one's P/two/five and Q/one/three, followed by document
four's R/NULL/seven and S/one/two. R remains represented even though its quantity
is unknown. S receives the declared default for omitted quantity. Empty or absent
arrays have no rows in this CROSS item relation.

The complete executable assertion compares all projected values in document and
ordinal order. It also requires four distinct position pairs. That uniqueness
applies to this snapshot; positions are not stable business identifiers when an
array changes order between versions.

**Verify:** Match every actual row to its original JSON array context, including
R's retained unknown quantity.

## Exercise 3: Separate empty paths, JSON null and conversion errors

**Inputs:** For sql-json-01 Exercise 3, use the two-item worked literal with explicit JSON null and an omitted qty, then a separate literal whose qty is the text two.
**Expected result/shape:** For sql-json-01 Exercise 3, for the two-item literal, display item_no, qty, qty_present ordered by item_no as (1,NULL,true), (2,1,false). Invalid text produces SQL NULL under NULL ON ERROR and SQLSTATE 22P02 under ERROR ON ERROR; each generated literal position is identified by item_no.
**Verify:** For sql-json-01 Exercise 3, check presence separately from scalar value and catch only the intended conversion error. Neither policy permits silently converting a malformed quantity to zero revenue.

The two-item literal produces one explicitly null field and one missing field.
A presence projection complements the typed quantity:

```sql
SELECT j.item_no,j.qty,j.qty_present
FROM JSON_TABLE('{"items":[{"qty":null},{}]}','$.items[*]'
  COLUMNS (
    item_no FOR ORDINALITY,
    qty integer PATH '$.qty' DEFAULT 1 ON EMPTY ERROR ON ERROR,
    qty_present boolean EXISTS PATH '$.qty'
  )) AS j
ORDER BY j.item_no;
```

The rows are `(1,NULL,true)` and `(2,1,false)`. An existing JSON null is not an
empty path. The scalar projection maps it to SQL NULL rather than activating the
default. With invalid quantity text `two`, `NULL ON ERROR` deliberately returns
SQL NULL, while `ERROR ON ERROR` raises the observed conversion error `22P02`.
The reference handles that specific error and fails if the malformed conversion
unexpectedly succeeds.

SQL NULL is also different from a stored JSON null value. Calling `to_jsonb` on
an SQL NULL returns SQL NULL. The reference therefore tests the predicate
`qty IS NULL` directly when checking the error-fallback result.

**Verify:** Inspect both existence and value, and preserve the distinction
between a controlled fallback and successful typed measurement.

## Exercise 4: Count only actual items and their missing quantities

**Inputs:** For sql-json-01 Exercise 4, use a LEFT JSON_TABLE relation for all four source documents and count only generated item positions when measuring item or unknown-quantity rows.
**Expected result/shape:** For sql-json-01 Exercise 4, display document_id, item_count, unknown_qty_count ordered by document_id as (1,2,0), (2,0,0), (3,0,0), (4,2,1), one row per document_id.
**Verify:** For sql-json-01 Exercise 4, compare actual position counts with source array lengths. COUNT(*) would count an outer placeholder; unknown quantities count only rows with a non-NULL item_no.

`j17_outer` preserves the four documents, including placeholders for documents
two and three. Count the generated ordinal to measure actual items. An unknown
quantity counts only when a real item exists.

```sql
SELECT document_id,
       count(item_no) AS item_count,
       count(*) FILTER (
         WHERE item_no IS NOT NULL AND qty IS NULL
       ) AS unknown_qty_count
FROM j17_outer
GROUP BY document_id
ORDER BY document_id;
```

The exact triples are `(1,2,0)`, `(2,0,0)`, `(3,0,0)` and `(4,2,1)`.
`COUNT(*)` instead would count one row for each empty or absent parent, while
counting all NULL quantities without checking `item_no` would misclassify those
placeholders as unknown items. The executable assertion checks the complete
four-row result, not only an overall count.

**Verify:** Independently count each source array's entries and identify the
single actual unknown quantity, R.

## Exercise 5: Keep partial value separate from complete acceptance

**Inputs:** For sql-json-01 Exercise 5, use all four documents, one declared currency and the worked missing-qty policy. Preserve array presence/type and unknown item counts before accepting an order total.
**Expected result/shape:** For sql-json-01 Exercise 5, display document_id, known_line_value, accepted_order_value, coverage_state ordered by document_id, one row per document_id. Accepted values are 13, 0, NULL, NULL; document 4 has known partial value 2 and incomplete coverage.
**Verify:** For sql-json-01 Exercise 5, compare each item contribution and unknown count with the displayed line values before checking the coverage CASE. Document 3 lacks its array, document 4 has an unknown quantity, and a partial SUM must not become a complete accepted amount.

Aggregate at document grain but preserve coverage. The reference first computes
known line value and actual unknown-item count. It then rejoins each original
document to inspect the declared array shape before accepting the total.

```sql
CASE
  WHEN jsonb_typeof(d.payload->'items') IS DISTINCT FROM 'array'
       OR a.unknown_count > 0 THEN NULL
  ELSE a.known_line_value
END AS accepted_order_value
```

The accepted values are thirteen, zero, NULL and NULL. Document one has complete
known contributions ten plus three. Document two explicitly declares zero
items, so zero is accepted under this contract. Document three has no declared
array and is labeled `missing_items_array`. Document four has one unknown
quantity, so its known partial value of two is labeled separately from its
unaccepted complete value.

Using `COALESCE(SUM(...),0)` to produce a useful known-partial subtotal does not
authorize publishing it as a complete amount. The reference compares both
values and coverage labels, making that distinction inspectable.

**Verify:** Reconstruct ten plus three and the separate known two contribution
from original items, then identify exactly which missing evidence blocks each
complete total.

## Exercise 6: Add a parent fee after reducing item grain

**Inputs:** For sql-json-01 Exercise 6, use accepted child totals and one shipping_fee from each original document. Aggregate child rows to document grain before adding the parent amount.
**Expected result/shape:** For sql-json-01 Exercise 6, display document_id, accepted_total ordered by document_id as (1,17), (2,0), (3,NULL), (4,NULL), one row per document_id.
**Verify:** For sql-json-01 Exercise 6, assert the deliberately incorrect output value 21 for document 1 when its fee is repeated at item grain, then assert accepted output 17 charges the parent fee four exactly once.

The prior answer has one row per document. Join it to the original one-row
document relation and add its single parent fee:

```sql
SELECT d.document_id,
       a.accepted_order_value
         + (d.payload->>'shipping_fee')::numeric(10,2) AS accepted_total
FROM j17_documents AS d
JOIN answer_5 AS a ON a.document_id=d.document_id
ORDER BY d.document_id;
```

The results are seventeen, zero, NULL and NULL. Unknown complete item values
remain unknown when a known shipping fee is added. The final result is ordered
by the document identity, with exactly one row for each original parent.

The executable reference also computes the tempting wrong item-grain result
for document one: summing each line plus the repeated parent fee yields
`2*5+4 + 1*3+4 = 21`. That deliberately wrong result is asserted so the
counterexample remains visible. The correct calculation is `2*5 + 1*3 + 4 = 17`.
Typed extraction and a valid numeric value do not prevent a relational grain
error.

**Verify:** Count how many times shipping enters the expression and confirm that
reducing to parent grain occurs before the fee is applied.

## Final evidence review

Explain the grain of the document table, actual item view, outer-preserving view
and accepted-total relation. Review exact NULL behavior, positions and coverage
alongside numeric amounts. The final transaction rollback removes all reference
objects. A successful reference run is comparison evidence; reconstruct the
reasoning independently before treating the lesson as understood.
