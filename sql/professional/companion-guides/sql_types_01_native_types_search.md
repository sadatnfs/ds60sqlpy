# SQL-TYPES-01 — PostgreSQL-Native Types and Searchable Documents

## Level and prerequisites

- **Level:** Advanced
- **Catalog prerequisite:** `sql-29`
- **Prerequisites:** SQL Day 28 JSON,
  [SQL Day 29 pattern matching](../../postgres-60day/companion-guides/day29_pattern_matching.md),
  constraints, and basic index concepts.
- **Artifacts:** [learner SQL](../lessons/sql_types_01_native_types_search.sql) ·
  [solution reasoning](../solutions/sql_types_01_native_types_search_solutions.md) ·
  [executable solution](../solutions/sql_types_01_native_types_search_solutions.sql)

Run on Windows PowerShell, macOS, or Linux:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/lessons/sql_types_01_native_types_search.sql
```

Only built-in PostgreSQL 16 features are used. The script inspects
`pg_trgm` availability but does not enable any extension.

## Learning objectives

- Model and query domains, enums, UUIDs, arrays, ranges, multiranges, JSONB, and
  JSONPath.
- Build generated `tsvector`, `tsquery`, and ranked full-text results.
- Connect GIN/GiST operator support to query shape and explain when a normalized
  relation is safer than a convenient native container.

## Vocabulary and concepts

- **Domain:** reusable base type plus constraints, such as an email-shaped text
  value.
- **Enum:** ordered closed set of labels stored as a PostgreSQL type.
- **UUID:** 128-bit identifier useful when independent writers need identifiers
  without a central integer allocation.
- **Array:** ordered collection of values of one type in a row.
- **Range/multirange:** one interval or normalized set of intervals with explicit
  inclusive/exclusive bounds.
- **JSONB:** decomposed binary JSON supporting containment, path queries, and
  indexes.
- **JSONPath:** expression language for navigating and testing JSON structure.
- **tsvector/tsquery:** normalized document lexemes and a parsed search query.
- **GIN:** inverted index suited to membership/search over composite values.
- **GiST:** generalized search tree supporting operators such as overlap.
- **Operator class:** the operators and ordering semantics an index implements.

## Worked example / walkthrough

The model uses a domain for a reusable email-shape rule and an enum for a small
database-owned lifecycle. Enums are compact and clear, but adding/removing
labels is migration work; a reference table is more flexible when labels carry
metadata or change frequently.

UUID literals make the fixture deterministic. Production UUID generation may
use application generation or PostgreSQL's available generator, but randomness
does not make an identifier an authorization secret.

`tags text[]` supports containment (`@>`) and membership (`= ANY`). Arrays fit a
small row-owned set. If tags need descriptions, permissions, global uniqueness,
or frequent independent updates, normalize them into tag and join tables.

`daterange` and `datemultirange` express availability and blackouts. The lesson
uses `[lower, upper)`: the lower date is included and the upper date is excluded.
That boundary convention prevents adjacent intervals from double-counting a
date.

JSONB stores optional document-shaped metadata while a `CHECK` requires an
object. Stable, required, relationally constrained attributes should remain
columns. `jsonb_path_ops` is compact and effective for containment/path
operators but supports fewer operator strategies than the default `jsonb_ops`;
choose from measured query requirements.

The stored `search_vector` weights title lexemes above body lexemes. Passing an
explicit `'english'::regconfig` makes tokenization stable across sessions.
`websearch_to_tsquery` accepts familiar syntax; `@@` matches and `ts_rank_cd`
ranks. Ranking is not a relevance guarantee—language, corpus, weights, recency,
and product expectations need evaluation.

`pg_trgm` can support similarity and wildcard-like search, but it is an
extension with write/storage cost. The default lesson only reads
`pg_available_extensions`; enabling extensions is an approved database-owner
decision.

## Exercises

Complete all twelve learner prompts. Begin with multi-tag containment, range-minus-blackout
logic, typed JSONPath filtering, phrase-aware full-text ranking, index/operator
trade-offs, and type-selection reasoning; then cover multirange, networks,
money, promoted JSON, language search, and normalization. Preserve deterministic
ordering and state all NULL and boundary assumptions.

For JSON, first guard shape/type when data is not controlled. A cast from an
arbitrary string to integer can fail before a predicate excludes it.

For each choice, name the operators, constraints, index support, boundary rules,
write cost, and migration cost:

1. **Tag containment:** require both tags, preserve published status, and order
   ties deterministically.
2. **Range subtraction:** apply the half-open rule and prove both range
   boundaries.
3. **Typed JSONPath:** guard shape/type before numeric comparison.
4. **Full-text query:** parse the web-style phrase, rank, and add a stable
   secondary order.
5. **Index comparison:** map JSONB, text-search, and trigram operators to their
   useful operator classes.
6. **Type decision:** defend domain, enum, lookup, array, range, JSONB, or
   normalized-relation choices field by field.
7. **Multirange:** normalize availability, find August gaps, and define whether
   adjacency merges.
8. **Networks:** match addresses to their most-specific containing `cidr` and
   identify an operator-compatible index.
9. **Money:** compare fixed-scale numeric, minor-unit bigint, and floating point
   using explicit precision and rounding tests.
10. **Promoted JSON:** validate a generated typed value, index it, and test an
    old payload against the evolved contract.
11. **Language search:** inspect lexemes and design configuration selection for
    non-English rows.
12. **Normalize tags:** compare normalized keys and joins with array
    containment, duplicates, order, constraints, and writes.

## Self-check

- Do UUID, domain, and enum constraints reject invalid representations?
- Can you distinguish array containment from scalar membership?
- Can you say whether each range endpoint is included?
- Does every JSON cast have a documented shape assumption or guard?
- Is the text-search configuration explicit?
- Does the index operator class support the operators in the query?
- Does rollback remove types, indexes, and schema without enabling extensions?

## Common pitfalls

- Treating JSONB as a reason to avoid relational design loses foreign keys and
  clear contracts.
- Arrays make cross-row uniqueness and per-element metadata awkward.
- Enum removal/reordering is not casual application data maintenance.
- Range upper bounds are frequently misunderstood; write boundary tests.
- `jsonb_path_ops` is not a universal replacement for `jsonb_ops`.
- GIN indexes can be large and add write/maintenance cost.
- `LIKE '%term%'` and full-text search answer different language questions.
- Ranking ties need a deterministic secondary order.
- UUIDs hide sequence order but do not provide secrecy or tenant isolation.

## Next step

Continue to [SQL-OPS-01 — index types, statistics, and maintenance](sql_ops_01_indexes_statistics_maintenance.md)
to connect these operators to planner evidence and lifecycle cost. Revisit the
relational-design module whenever a convenient native type begins hiding a
cross-row invariant.
