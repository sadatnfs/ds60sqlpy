# SQL-TYPES-01 Solutions — Native Types and Search

Run:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/solutions/sql_types_01_native_types_search_solutions.sql
```

The solution creates and rolls back only `pro_types_lab`.

## Exercise 1 — Multi-tag containment

`tags @> ARRAY['postgresql','operations']` asks whether the stored array
contains both required values. Two scalar `ANY` predicates can express the same
fixture result, but containment maps directly to the set-like question and a
GIN array operator class.

Arrays preserve order and duplicates, so they are not literally mathematical
sets. If duplicate/order semantics matter, test them explicitly.

## Exercise 2 — Availability minus blackout

The predicate combines:

```sql
availability @> DATE '2026-08-11'
AND NOT (blackout_windows @> DATE '2026-08-11')
```

The fixture uses `[start,end)`, including start and excluding end. The migration
document is generally available that day but specifically blacked out, so it is
excluded.

## Exercise 3 — Numeric JSONPath

The JSONPath predicate checks both JSON number type and value above 30. The
selected cast is safe because this controlled fixture owns the metadata shape.
With untrusted JSON, use shape validation or a normalized typed column before
casting; SQL predicate evaluation order is not a universal error guard.

## Exercise 4 — Phrase-aware full text

`websearch_to_tsquery('english', '"schema migration" verify')` builds a query
requiring the phrase plus `verify`. The generated vector weights titles above
bodies, and ordering uses rank then UUID to break ties deterministically.

Different configurations stem words differently. Always use the same explicit
configuration when generating vectors and queries.

## Exercise 5 — Index choices

- Default `jsonb_ops` supports a wider operator family and indexes keys and
  values.
- `jsonb_path_ops` is typically smaller and focused on containment/jsonpath
  value paths.
- GIN over `tsvector` supports lexeme matching.
- `pg_trgm` supports similarity and many substring patterns, but requires an
  approved extension and adds index/write cost.

Choose from observed operators and workload, then measure plans and maintenance;
do not stack every candidate index.

## Exercise 6 — Modelling choices

Use a domain for a stable reusable scalar rule, an enum for a small
database-owned closed lifecycle, a reference table when labels need metadata or
frequent change, an array for a small row-owned homogeneous collection, a range
for interval algebra, JSONB for genuinely variable document-shaped attributes,
and normalized relations for independently identified facts and cross-row
constraints.

## Edge cases

- Empty arrays and empty ranges have distinct semantics.
- Multiranges normalize overlapping/adjacent members.
- Missing JSON, JSON null, and SQL NULL differ.
- Search ranking and phrase behavior require corpus-level relevance tests.

