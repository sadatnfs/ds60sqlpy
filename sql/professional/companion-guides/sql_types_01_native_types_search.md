# SQL-TYPES-01: PostgreSQL-Native Types and Searchable Documents

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-types-01**. The
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
   `.learning/sql/sql-types-01/lesson/workspace/sql/professional/lessons/sql_types_01_native_types_search.sql`.
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
uv run --no-sync python scripts/course.py sql notebook sql-types-01
```

Open the printed notebook path in that environment's JupyterLab. It uses the
same catalog-derived learner-copy layout in that contributor checkout and
executes the complete script through psql. Its host-side state is separate
from the Docker browser's named volume. Follow
[guided SQL notebooks](../../../docs/guided-sql-notebooks.md) for explicit local connection
selection and kernel setup. Notebook generation does not execute SQL or
authorize a reset.

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

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence at the
table's declared grain. A query creates a temporary **result set**: rows printed
on screen are not automatically stored. The key vocabulary for this lesson is Domain, Enum, UUID, Array, Range/multirange, JSONB. Its worked SQL reads or creates `pro_types_lab.documents`, `pg_catalog.pg_indexes`, `pg_catalog.pg_available_extensions`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: The model uses a domain for a reusable email-shape rule and an enum for a small database-owned lifecycle. Enums are compact and clear, but adding/removing labels is migration work; a reference table is more flexible when labels carry metadata or change frequently.
The first runnable example has a concrete contract: Example 1 must print the expected DDL command tag for `pro_types_lab.documents`. Verify the object in `pg_catalog.pg_class`, and `information_schema.columns`, run one accepted behavior and one rejected boundary behavior, and confirm the lesson rollback/cleanup removes only course-owned state. Its final projection is the columns written in the final `SELECT`. Verify the command tag in `pg_catalog`/`information_schema`, run one accepted value and one value the declared rule rejects, and confirm the lesson rollback removes the course-owned object. Where this query can emit `NULL`, identify the exact source expression and explain whether the output preserves, classifies, or rejects it.

## Two worked SQL examples

These worked excerpts come from `sql/professional/lessons/sql_types_01_native_types_search.sql`. Use **Whole SQL lesson (psql)** in the unified classroom for the complete file, including its fixture and transaction context. The optional contributor notebook and prepared `psql` routes are described above.

### Example 1

```sql
CREATE TABLE pro_types_lab.documents (
    document_id uuid PRIMARY KEY,
    owner_email pro_types_lab.email_address NOT NULL,
    state pro_types_lab.document_state NOT NULL DEFAULT 'draft',
    title text NOT NULL CHECK (btrim(title) <> ''),
    body text NOT NULL,
    tags text[] NOT NULL DEFAULT ARRAY[]::text[],
    availability daterange NOT NULL
        CHECK (NOT isempty(availability)),
    blackout_windows datemultirange NOT NULL
        DEFAULT '{}'::datemultirange,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb
        CHECK (jsonb_typeof(metadata) = 'object'),
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(
            to_tsvector('english'::regconfig, COALESCE(title, '')),
            'A'
        )
        ||
        setweight(
            to_tsvector('english'::regconfig, COALESCE(body, '')),
            'B'
        )
    ) STORED
);
```

**How to read it:** Example 1 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** Example 1 must print the expected DDL command tag for `pro_types_lab.documents`. Verify the object in `pg_catalog.pg_class`, and `information_schema.columns`, run one accepted behavior and one rejected boundary behavior, and confirm the lesson rollback/cleanup removes only course-owned state.

### Example 2

```sql
INSERT INTO pro_types_lab.documents (
    document_id,
    owner_email,
    state,
    title,
    body,
    tags,
    availability,
    blackout_windows,
    metadata
)
VALUES
    (
        '00000000-0000-0000-0000-000000000101',
        'avery@example.test',
        'published',
        'Safe schema migrations',
        'Plan additive changes, backfill data, verify invariants, and contract later.',
        ARRAY['postgresql', 'sql', 'operations'],
        daterange(DATE '2026-01-01', DATE '2027-01-01', '[)'),
        datemultirange(
            daterange(DATE '2026-07-01', DATE '2026-07-08', '[)')
        ),
        '{"audience":["developer","operator"],"difficulty":"advanced","minutes":45}'
    ),
    (
        '00000000-0000-0000-0000-000000000102',
        'morgan@example.test',
        'published',
        'Analytical SQL patterns',
        'Use windows and explicit grain for sessions, funnels, and retention.',
        ARRAY['postgresql', 'sql', 'analytics'],
        daterange(DATE '2026-03-01', DATE '2026-10-01', '[)'),
        '{}'::datemultirange,
        '{"audience":["analyst"],"difficulty":"intermediate","minutes":35}'
    ),
    (
        '00000000-0000-0000-0000-000000000103',
        'taylor@example.test',
        'draft',
        'Python service notes',
        'Validate configuration and add request identifiers to structured logs.',
        ARRAY['python', 'services'],
        daterange(DATE '2026-05-01', DATE '2026-12-01', '[)'),
        datemultirange(
            daterange(DATE '2026-08-10', DATE '2026-08-12', '[)'),
            daterange(DATE '2026-09-03', DATE '2026-09-05', '[)')
        ),
        '{"audience":["developer"],"difficulty":"intermediate","minutes":25}'
    );
```

**How to read it:** Example 2 changes rows inside the lesson's declared transaction. The command tag reports affected rows, but a follow-up query must prove the intended before/after invariant.

**Expected result/shape:** Example 2 must complete through `psql` with its documented command tag or notice for `pro_types_lab.documents`. Treat an unexpected error as failure, and prove the stated catalog/behavior invariant plus cleanup.

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
ranks. Ranking is not a relevance guarantee, language, corpus, weights, recency,
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
   **Inputs/evidence:** For sql-types-01 Exercise 1, filter `documents` to published rows whose `tags` array contains both `postgresql` and `operations` using one `@>` containment predicate.
   **Expected result/shape:** For sql-types-01 Exercise 1, expected output: exactly one row at document grain with `document_id` and `title`, ordered by `document_id`.
   **Verify:** For sql-types-01 Exercise 1, compare the result with an independent unnest/distinct-tag control, prove both required tags, not either one, are present, and explain that array GIN supports containment while two `= ANY` predicates express separate membership tests.
2. **Range subtraction:** apply the half-open rule and prove both range
   boundaries.
   **Inputs/evidence:** For sql-types-01 Exercise 2, require `availability @> probe_date` and NOT `blackout_windows @> probe_date`, then probe the lower and upper endpoints of both `[)` ranges for document 201.
   **Expected result/shape:** For sql-types-01 Exercise 2, expected output: document 202 for 2026-08-11 plus four boundary rows showing availability lower included, blackout lower excluded from use, blackout upper available, and availability upper excluded.
   **Verify:** For sql-types-01 Exercise 2, assert the `[lower, upper)` truth table directly and distinguish an unavailable document from a missing result row; test both range and multirange containment at exact endpoints.
3. **Typed JSONPath:** guard shape/type before numeric comparison.
   **Inputs/evidence:** For sql-types-01 Exercise 3, use JSONPath to require a JSON number greater than 30 before casting its text representation to unbounded `numeric`.
   **Expected result/shape:** For sql-types-01 Exercise 3, expected output: one row per matching document with `document_id`, `title`, and `minutes_numeric`; the supplied fixture returns documents 201 and 202.
   **Verify:** For sql-types-01 Exercise 3, add string, missing, fractional, and very large numeric values; prove JSONPath excludes nonnumbers, numeric preserves fractional/range values, and no arbitrary JSON value reaches an unsafe integer cast.
4. **Full-text query:** parse the web-style phrase, rank, and add a stable
   secondary order.
   **Inputs/evidence:** For sql-types-01 Exercise 4, build one English `websearch_to_tsquery` for the phrase and term, match it against the stored weighted search vector, and compute `ts_rank_cd`.
   **Expected result/shape:** For sql-types-01 Exercise 4, expected output: matching `document_id`, `title`, and `rank_score`, ordered by rank descending then `document_id`; the fixture returns document 201.
   **Verify:** For sql-types-01 Exercise 4, display the parsed tsquery and source lexemes, assert every returned vector satisfies `@@`, and retain the document-ID tie-breaker because equal rank scores are possible.
5. **Index comparison:** map JSONB, text-search, and trigram operators to their
   useful operator classes.
   **Inputs/evidence:** For sql-types-01 Exercise 5, return an operator-first matrix mapping four real predicates to candidate index families and one superficially related query that each index does not serve.
   **Expected result/shape:** For sql-types-01 Exercise 5, expected output: four rows with `workload`, `matching_operator`, `candidate_index`, `nonmatching_query`, and `reason`, covering arrays, JSONB, full-text, and ranges.
   **Verify:** For sql-types-01 Exercise 5, inspect operator classes and compare EXPLAIN plans only after representative data exists; distinguish `jsonb_ops` flexibility from `jsonb_path_ops` size/supported-operator trade-offs and treat pg_trgm as optional.
6. **Type decision:** defend domain, enum, lookup, array, range, JSONB, or
   normalized-relation choices field by field.
   **Inputs/evidence:** For sql-types-01 Exercise 6, classify modeled field shapes against domain, CHECK/enum, reference table, array, range/multirange, JSONB, and normalized relation choices.
   **Expected result/shape:** For sql-types-01 Exercise 6, expected output: seven deterministic rows with `field_shape`, `candidate_type`, and a concrete `decision_rule`.
   **Verify:** For sql-types-01 Exercise 6, challenge each choice with one evolution/query/integrity counterexample, and prefer the type whose operators and constraints match the domain rather than the most exotic type.
7. **Multirange:** normalize availability, find August gaps, and define whether
   adjacency merges.
   **Inputs/evidence:** For sql-types-01 Exercise 7, construct a `datemultirange` from overlapping and adjacent half-open date ranges, then subtract it from the August 2026 month range.
   **Expected result/shape:** For sql-types-01 Exercise 7, expected output: exactly one row with canonical `normalized_availability` and `august_gaps`; adjacent/overlapping discrete ranges merge.
   **Verify:** For sql-types-01 Exercise 7, independently test every August date for membership in either availability or gaps, require no overlap and complete month coverage, and state whether adjacency should merge in this business domain.
8. **Networks:** match addresses to their most-specific containing `cidr` and
   identify an operator-compatible index.
   **Inputs/evidence:** For sql-types-01 Exercise 8, preserve every client with `LEFT JOIN LATERAL`; inside the lateral query choose the containing CIDR with greatest mask length and `rule_id` tie-breaker.
   **Expected result/shape:** For sql-types-01 Exercise 8, expected output: one row per client with `client_id`, `address`, `rule_id`, and `network`; matched clients receive their longest prefix and the unmatched client retains NULL rule fields.
   **Verify:** For sql-types-01 Exercise 8, assert output count equals client count, validate each chosen network contains its address, prove no more-specific candidate exists, and test both IPv4, IPv6, and unmatched addresses.
9. **Money:** compare fixed-scale numeric, minor-unit bigint, and floating point
   using explicit precision and rounding tests.
   **Inputs/evidence:** For sql-types-01 Exercise 9, define a nonnegative `numeric(12,2)` domain, demonstrate exact arithmetic and rounding, and compare it with bigint minor units and double precision.
   **Expected result/shape:** For sql-types-01 Exercise 9, expected output: one scalar evidence row plus a three-row storage matrix; the domain cast of NULL remains NULL because NOT NULL belongs on the consuming column.
   **Verify:** For sql-types-01 Exercise 9, reject a negative value, assert exact sum `30.30` and declared rounding `10.13`, test NULL at both domain and NOT NULL column boundaries, and document currency/scale when using minor units.
10. **Promoted JSON:** validate a generated typed value, index it, and test an
    old payload against the evolved contract.
   **Inputs/evidence:** For sql-types-01 Exercise 10, add a stored generated integer that accepts only JSON numbers that are integral and within PostgreSQL integer range; otherwise return NULL, then index it.
   **Expected result/shape:** For sql-types-01 Exercise 10, expected output: boundary rows for string, missing, fractional, and out-of-range minutes, all safely classified as NULL; valid integral seed values remain queryable.
   **Verify:** For sql-types-01 Exercise 10, prove all four malformed-for-the-property payloads insert without cast errors, valid 35/45 values materialize, the index exists, and the application policy distinguishes invalid from absent rather than silently treating both as zero.
11. **Language search:** inspect lexemes and design configuration selection for
    non-English rows.
   **Inputs/evidence:** For sql-types-01 Exercise 11, convert each title/body pair with an explicit English text-search configuration and expose the resulting lexemes.
   **Expected result/shape:** For sql-types-01 Exercise 11, expected output: one row per document with `document_id` and `lexemes`, ordered by `document_id`.
   **Verify:** For sql-types-01 Exercise 11, inspect stemming and stop-word behavior with known tokens, compare a non-English sample under the English and appropriate configurations, and keep the configured language explicit in stored-vector policy.
12. **Normalize tags:** compare normalized keys and joins with array
    containment, duplicates, order, constraints, and writes.
   **Inputs/evidence:** For sql-types-01 Exercise 12, normalize legacy tag arrays with `lower(btrim(tag))`, insert distinct vocabulary rows, and insert distinct `(document_id, tag_id)` bridge rows.
   **Expected result/shape:** For sql-types-01 Exercise 12, expected output: one normalized vocabulary row per canonical tag, one bridge row per document/tag pair despite duplicate legacy spellings, and document 201 for the two-tag relational query.
   **Verify:** For sql-types-01 Exercise 12, inject `python`, ` Python `, and duplicate `python` in one array, assert only one bridge pair survives, verify foreign-key and composite-primary-key enforcement, and record that array order/case/whitespace are intentionally discarded.

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

Continue to [SQL-OPS-01; index types, statistics, and maintenance](sql_ops_01_indexes_statistics_maintenance.md)
to connect these operators to planner evidence and lifecycle cost. Revisit the
relational-design module whenever a convenient native type begins hiding a
cross-row invariant.

## Ask an AI tutor about this lesson

An AI tutor is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in the AI tutor:

```text
Tutor me through sql-types-01 — PostgreSQL-Native Types and Searchable Documents.

I have completed the direct catalog prerequisite: `sql-29`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/professional/companion-guides/sql_types_01_native_types_search.md
- Answer-free learner SQL: sql/professional/lessons/sql_types_01_native_types_search.sql

Key terms to teach in context: Domain, Enum, UUID, Array, Range/multirange, JSONB. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: The model uses a domain for a reusable email-shape rule and an enum for a small database-owned lifecycle. Enums are compact and clear, but adding/removing labels is migration work; a reference table is more flexible when labels carry metadata or change frequently.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-types-01/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Treat every path under `solutions/` as closed until I explicitly ask after an attempt.

Follow guide -> predict -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back. Done when I can explain the row grain and clause order, produce a passing transcript for the current exercise, justify its verification evidence, and answer the retrieval questions without copying the solution.
```
