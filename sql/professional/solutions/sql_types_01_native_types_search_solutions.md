# SQL-TYPES-01 Solutions — Native Types and Search


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\professional\solutions\sql_types_01_native_types_search_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/professional/solutions/sql_types_01_native_types_search_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Domain, Enum, UUID, Array, Range/multirange, JSONB. Its worked-model focus is:
The model uses a domain for a reusable email-shape rule and an enum for a small database-owned lifecycle. Enums are compact and clear, but adding/removing labels is migration work; a reference table is more flexible when labels carry metadata or change frequently.

- Start at `FROM`/`JOIN` and state the intermediate row grain. Inspect join keys
  before adding aggregates; a one-to-many join is allowed to multiply rows only
  when the later contract accounts for it.
- Apply `WHERE` to input rows, `GROUP BY` to form buckets, and `HAVING` to
  completed groups. Window functions run over the surviving relation and
  normally preserve its row count.
- Read the `SELECT` list as the public result contract: keys establish grain,
  measures state calculations, and aliases explain meaning. `ORDER BY` is the
  only output-order guarantee; add a unique tie-breaker before `LIMIT`.
- Trace every common table expression (CTE) as a temporary named relation.
  Execute or inspect one stage at a time while debugging, but compare the final
  result with an independent control rather than trusting stage names.
- Keep SQL `NULL` as “missing/unknown/not applicable” until the metric contract
  chooses another representation. Guard division with `NULLIF`; disclose
  exclusions and distinguish zero from no row.
- For DDL/DML, a command tag proves only that PostgreSQL accepted a statement.
  Catalog checks, negative cases, row-count reconciliation, and the declared
  transaction boundary prove behavior and cleanup.

The exact final queries are not the only valid syntax. A join, subquery, CTE,
window, or conditional aggregate can be an alternative when it preserves the
same grain, `NULL` semantics, deterministic ordering, and safety. Prefer the
form whose intermediate relations a reviewer can verify; optimize only after
correctness is established with evidence.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-types-01 Exercise 1, filter `documents` to published rows whose `tags` array contains both `postgresql` and `operations` using one `@>` containment predicate.
- **Expected result/shape:** For sql-types-01 Exercise 1, expected output: exactly one row at document grain with `document_id` and `title`, ordered by `document_id`.
- **Independent verification:** For sql-types-01 Exercise 1, compare the result with an independent unnest/distinct-tag control, prove both required tags—not either one—are present, and explain that array GIN supports containment while two `= ANY` predicates express separate membership tests.

## Exercise 2 — Availability minus blackout

The predicate combines:

```sql
availability @> DATE '2026-08-11'
AND NOT (blackout_windows @> DATE '2026-08-11')
```

The fixture uses `[start,end)`, including start and excluding end. The migration
document is generally available that day but specifically blacked out, so it is
excluded.

### Reasoning and verification

- **Inputs/evidence:** For sql-types-01 Exercise 2, require `availability @> probe_date` and NOT `blackout_windows @> probe_date`, then probe the lower and upper endpoints of both `[)` ranges for document 201.
- **Expected result/shape:** For sql-types-01 Exercise 2, expected output: document 202 for 2026-08-11 plus four boundary rows showing availability lower included, blackout lower excluded from use, blackout upper available, and availability upper excluded.
- **Independent verification:** For sql-types-01 Exercise 2, assert the `[lower, upper)` truth table directly and distinguish an unavailable document from a missing result row; test both range and multirange containment at exact endpoints.

## Exercise 3 — Numeric JSONPath

The JSONPath predicate checks both JSON number type and value above 30. The
selected cast is safe because this controlled fixture owns the metadata shape.
With untrusted JSON, use shape validation or a normalized typed column before
casting; SQL predicate evaluation order is not a universal error guard.

### Reasoning and verification

- **Inputs/evidence:** For sql-types-01 Exercise 3, use JSONPath to require a JSON number greater than 30 before casting its text representation to unbounded `numeric`.
- **Expected result/shape:** For sql-types-01 Exercise 3, expected output: one row per matching document with `document_id`, `title`, and `minutes_numeric`; the supplied fixture returns documents 201 and 202.
- **Independent verification:** For sql-types-01 Exercise 3, add string, missing, fractional, and very large numeric values; prove JSONPath excludes nonnumbers, numeric preserves fractional/range values, and no arbitrary JSON value reaches an unsafe integer cast.

## Exercise 4 — Phrase-aware full text

`websearch_to_tsquery('english', '"schema migration" verify')` builds a query
requiring the phrase plus `verify`. The generated vector weights titles above
bodies, and ordering uses rank then UUID to break ties deterministically.

Different configurations stem words differently. Always use the same explicit
configuration when generating vectors and queries.

### Reasoning and verification

- **Inputs/evidence:** For sql-types-01 Exercise 4, build one English `websearch_to_tsquery` for the phrase and term, match it against the stored weighted search vector, and compute `ts_rank_cd`.
- **Expected result/shape:** For sql-types-01 Exercise 4, expected output: matching `document_id`, `title`, and `rank_score`, ordered by rank descending then `document_id`; the fixture returns document 201.
- **Independent verification:** For sql-types-01 Exercise 4, display the parsed tsquery and source lexemes, assert every returned vector satisfies `@@`, and retain the document-ID tie-breaker because equal rank scores are possible.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-types-01 Exercise 5, return an operator-first matrix mapping four real predicates to candidate index families and one superficially related query that each index does not serve.
- **Expected result/shape:** For sql-types-01 Exercise 5, expected output: four rows with `workload`, `matching_operator`, `candidate_index`, `nonmatching_query`, and `reason`, covering arrays, JSONB, full-text, and ranges.
- **Independent verification:** For sql-types-01 Exercise 5, inspect operator classes and compare EXPLAIN plans only after representative data exists; distinguish `jsonb_ops` flexibility from `jsonb_path_ops` size/supported-operator trade-offs and treat pg_trgm as optional.

## Exercise 6 — Modelling choices

Use a domain for a stable reusable scalar rule, an enum for a small
database-owned closed lifecycle, a reference table when labels need metadata or
frequent change, an array for a small row-owned homogeneous collection, a range
for interval algebra, JSONB for genuinely variable document-shaped attributes,
and normalized relations for independently identified facts and cross-row
constraints.

### Reasoning and verification

- **Inputs/evidence:** For sql-types-01 Exercise 6, classify modeled field shapes against domain, CHECK/enum, reference table, array, range/multirange, JSONB, and normalized relation choices.
- **Expected result/shape:** For sql-types-01 Exercise 6, expected output: seven deterministic rows with `field_shape`, `candidate_type`, and a concrete `decision_rule`.
- **Independent verification:** For sql-types-01 Exercise 6, challenge each choice with one evolution/query/integrity counterexample, and prefer the type whose operators and constraints match the domain rather than the most exotic type.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-types-01 Exercise 7, construct a `datemultirange` from overlapping and adjacent half-open date ranges, then subtract it from the August 2026 month range.
- **Expected result/shape:** For sql-types-01 Exercise 7, expected output: exactly one row with canonical `normalized_availability` and `august_gaps`; adjacent/overlapping discrete ranges merge.
- **Independent verification:** For sql-types-01 Exercise 7, independently test every August date for membership in either availability or gaps, require no overlap and complete month coverage, and state whether adjacency should merge in this business domain.

## Exercise 8 — Network containment

Store client endpoints as `inet` and rules as `cidr`. Join where the network
contains the address (`network >>= address`), then rank by
`masklen(network) DESC, rule_id` so the longest prefix wins deterministically.
GiST or SP-GiST network operator classes can support containment; confirm the
exact operator and plan.

Do not compare addresses as text: lexical order and spelling variants do not
express network containment. Explicitly define IPv4/IPv6 coexistence and the
default rule when no network matches.

### Reasoning and verification

- **Inputs/evidence:** For sql-types-01 Exercise 8, preserve every client with `LEFT JOIN LATERAL`; inside the lateral query choose the containing CIDR with greatest mask length and `rule_id` tie-breaker.
- **Expected result/shape:** For sql-types-01 Exercise 8, expected output: one row per client with `client_id`, `address`, `rule_id`, and `network`; matched clients receive their longest prefix and the unmatched client retains NULL rule fields.
- **Independent verification:** For sql-types-01 Exercise 8, assert output count equals client count, validate each chosen network contains its address, prove no more-specific candidate exists, and test both IPv4, IPv6, and unmatched addresses.

## Exercise 9 — Monetary representation

`numeric(p,s)` gives exact decimal arithmetic and a declared scale; validate
rounding at ingestion and choose capacity from maximum business value. Bigint
minor units are exact and interoperable but require an explicit currency scale
that may differ by currency. Double precision is approximate and is unsuitable
for exact equality/accounting totals.

A domain can centralize nonnegative/range rules, but currency compatibility is
cross-column and usually needs a composite model or reference table. Test sum,
rounding, multiplication, overflow, serialization, and mixed-currency rejection.

### Reasoning and verification

- **Inputs/evidence:** For sql-types-01 Exercise 9, define a nonnegative `numeric(12,2)` domain, demonstrate exact arithmetic and rounding, and compare it with bigint minor units and double precision.
- **Expected result/shape:** For sql-types-01 Exercise 9, expected output: one scalar evidence row plus a three-row storage matrix; the domain cast of NULL remains NULL because NOT NULL belongs on the consuming column.
- **Independent verification:** For sql-types-01 Exercise 9, reject a negative value, assert exact sum `30.30` and declared rounding `10.13`, test NULL at both domain and NOT NULL column boundaries, and document currency/scale when using minor units.

## Exercise 10 — Promote a JSON property

Validate that the payload property is a JSON number before casting it in a
generated expression, or constrain accepted payload shape first. Index the
stored typed column and query that column directly; this makes the frequently
used contract visible to statistics and tools.

This implementation keeps writes compatible while making the typed contract
observable: a legacy string such as `"30"`, a missing property, a fractional
number, or an out-of-range number materializes as SQL `NULL`. Consumers must
distinguish “not a valid promoted integer” from zero. A stricter design can add
a validated `CHECK` later, after inventorying old rows and updating writers.

### Reasoning and verification

- **Inputs/evidence:** For sql-types-01 Exercise 10, add a stored generated integer that accepts only JSON numbers that are integral and within PostgreSQL integer range; otherwise return NULL, then index it.
- **Expected result/shape:** For sql-types-01 Exercise 10, expected output: boundary rows for string, missing, fractional, and out-of-range minutes, all safely classified as NULL; valid integral seed values remain queryable.
- **Independent verification:** For sql-types-01 Exercise 10, prove all four malformed-for-the-property payloads insert without cast errors, valid 35/45 values materialize, the index exists, and the application policy distinguishes invalid from absent rather than silently treating both as zero.

## Exercise 11 — Language-aware full text

`to_tsvector` reveals normalized lexemes and positions after parsing,
dictionary stop-word removal, and stemming. Weight title/body lexemes before
ranking. Generate and query with the same explicit configuration.

For multilingual data, store/validate a language configuration per row or route
rows into language-specific vectors/indexes. A generic `simple` configuration
avoids stemming but is not automatically better. Evaluate relevance against a
labeled corpus, including unsupported/mixed-language fallback.

### Reasoning and verification

- **Inputs/evidence:** For sql-types-01 Exercise 11, convert each title/body pair with an explicit English text-search configuration and expose the resulting lexemes.
- **Expected result/shape:** For sql-types-01 Exercise 11, expected output: one row per document with `document_id` and `lexemes`, ordered by `document_id`.
- **Independent verification:** For sql-types-01 Exercise 11, inspect stemming and stop-word behavior with known tokens, compare a non-English sample under the English and appropriate configurations, and keep the configured language explicit in stored-vector policy.

## Exercise 12 — Normalize tags

Create a `tags` vocabulary and a `document_tags(document_id, tag_id)` relation
with a composite primary key. Containment becomes grouping/HAVING or joins, and
foreign keys enforce vocabulary and prevent duplicates.

Arrays are simpler for a small row-owned list queried by containment, but cannot
foreign-key individual elements and preserve duplicates/order. Normalization
adds join/write cost while supporting tag metadata, independent identity,
cross-row constraints, and referential updates.

### Reasoning and verification

- **Inputs/evidence:** For sql-types-01 Exercise 12, normalize legacy tag arrays with `lower(btrim(tag))`, insert distinct vocabulary rows, and insert distinct `(document_id, tag_id)` bridge rows.
- **Expected result/shape:** For sql-types-01 Exercise 12, expected output: one normalized vocabulary row per canonical tag, one bridge row per document/tag pair despite duplicate legacy spellings, and document 201 for the two-tag relational query.
- **Independent verification:** For sql-types-01 Exercise 12, inject `python`, ` Python `, and duplicate `python` in one array, assert only one bridge pair survives, verify foreign-key and composite-primary-key enforcement, and record that array order/case/whitespace are intentionally discarded.

## Edge cases

- Empty arrays and empty ranges have distinct semantics.
- Multiranges normalize overlapping/adjacent members.
- Missing JSON, JSON null, and SQL NULL differ.
- Search ranking and phrase behavior require corpus-level relevance tests.
