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

## Exercise 7 — Multirange normalization and gaps

Construct a `datemultirange` from input ranges; PostgreSQL canonicalizes and
merges overlapping or adjacent discrete date ranges. The August gap is the
bounded month range minus the normalized availability multirange. Expand only
for display/testing when the domain is small—range algebra avoids one row per
day.

Adjacency merging is correct when uninterrupted consecutive dates are one
availability period. If a handoff at the boundary has business meaning, store
separate identified periods rather than relying on a multirange that
canonicalizes them together.

## Exercise 8 — Network containment

Store client endpoints as `inet` and rules as `cidr`. Join where the network
contains the address (`network >>= address`), then rank by
`masklen(network) DESC, rule_id` so the longest prefix wins deterministically.
GiST or SP-GiST network operator classes can support containment; confirm the
exact operator and plan.

Do not compare addresses as text: lexical order and spelling variants do not
express network containment. Explicitly define IPv4/IPv6 coexistence and the
default rule when no network matches.

## Exercise 9 — Monetary representation

`numeric(p,s)` gives exact decimal arithmetic and a declared scale; validate
rounding at ingestion and choose capacity from maximum business value. Bigint
minor units are exact and interoperable but require an explicit currency scale
that may differ by currency. Double precision is approximate and is unsuitable
for exact equality/accounting totals.

A domain can centralize nonnegative/range rules, but currency compatibility is
cross-column and usually needs a composite model or reference table. Test sum,
rounding, multiplication, overflow, serialization, and mixed-currency rejection.

## Exercise 10 — Promote a JSON property

Validate that the payload property is a JSON number before casting it in a
generated expression, or constrain accepted payload shape first. Index the
stored typed column and query that column directly; this makes the frequently
used contract visible to statistics and tools.

The trade-off is stricter writes: a legacy string such as `"30"` may have been
accepted JSON but now fails the promoted contract. Inventory/backfill bad rows,
deploy compatible writers, validate, and only then enforce the generated value.

## Exercise 11 — Language-aware full text

`to_tsvector` reveals normalized lexemes and positions after parsing,
dictionary stop-word removal, and stemming. Weight title/body lexemes before
ranking. Generate and query with the same explicit configuration.

For multilingual data, store/validate a language configuration per row or route
rows into language-specific vectors/indexes. A generic `simple` configuration
avoids stemming but is not automatically better. Evaluate relevance against a
labeled corpus, including unsupported/mixed-language fallback.

## Exercise 12 — Normalize tags

Create a `tags` vocabulary and a `document_tags(document_id, tag_id)` relation
with a composite primary key. Containment becomes grouping/HAVING or joins, and
foreign keys enforce vocabulary and prevent duplicates.

Arrays are simpler for a small row-owned list queried by containment, but cannot
foreign-key individual elements and preserve duplicates/order. Normalization
adds join/write cost while supporting tag metadata, independent identity,
cross-row constraints, and referential updates.

## Edge cases

- Empty arrays and empty ranges have distinct semantics.
- Multiranges normalize overlapping/adjacent members.
- Missing JSON, JSON null, and SQL NULL differ.
- Search ranking and phrase behavior require corpus-level relevance tests.
