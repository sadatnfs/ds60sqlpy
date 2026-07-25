# Day 28 — Solutions: JSONB and XML

The setup stores event metadata in `jsonb` and sample order documents in
PostgreSQL's `xml` type. These exercises extract scalar values and reconcile
semi-structured data with relational tables.

## Exercise 1 — Count events by first path segment

Leading and trailing slashes are removed before `split_part` extracts the first
directory. Empty paths are labeled `[root]`.

```sql
SET search_path TO training, public;

WITH paths AS (
  SELECT CASE
           WHEN trim(BOTH '/' FROM metadata->>'path') = ''
             THEN '[root]'
           ELSE split_part(
             trim(BOTH '/' FROM metadata->>'path'),
             '/',
             1
           )
         END AS first_path_segment
  FROM events
)
SELECT first_path_segment,
       COUNT(*) AS events
FROM paths
GROUP BY first_path_segment
ORDER BY events DESC, first_path_segment;
```

Expected shape: one row per first path segment. If `metadata` lacks `path`,
the expression evaluates to `NULL`, which forms its own aggregate group.

## Exercise 2 — Extract XML order IDs and validate status

`xpath` returns an XML array even when the path selects one node. Index `[1]`
extracts that node, and the order ID is cast through text to integer before the
join.

```sql
SET search_path TO training, public;

WITH parsed AS (
  SELECT doc_id,
         ((xpath('/order/id/text()', payload))[1]::text)::int AS order_id,
         (xpath('/order/status/text()', payload))[1]::text AS xml_status
  FROM xml_docs
)
SELECT p.doc_id,
       p.order_id,
       p.xml_status,
       o.status AS relational_status,
       p.xml_status = o.status AS statuses_match
FROM parsed p
LEFT JOIN orders o USING (order_id)
ORDER BY p.doc_id;
```

Expected shape: one row per XML document. `statuses_match` is `true` when both
sources agree, `false` when they disagree, and `NULL` if no relational order is
found.

## Pitfalls

- `metadata->'path'` returns JSONB; `metadata->>'path'` returns text. Text
  functions need the latter.
- A missing JSON key yields SQL `NULL`; it is different from a JSON value that
  literally contains `null`.
- This XML path assumes exactly one `/order/id` and `/order/status`. Production
  parsing should validate cardinality before indexing the returned array.
- XML is case-sensitive and namespace-aware; namespaced documents require a
  namespace mapping argument to `xpath`.
