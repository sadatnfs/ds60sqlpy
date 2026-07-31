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

## How to run this lesson

The rendered lesson page is for reading. PostgreSQL runs the real learner SQL.
For a first attempt, use the private course portal so the database check,
ignored working copy, and complete `psql` transcript remain together.

1. Open a terminal in the repository root. On Windows, double-click
   `START_DS60.cmd` or run:

   ```powershell
   .\START_DS60.cmd
   ```

   On macOS or Linux, run:

   ```bash
   .venv/bin/python scripts/learning_portal.py
   ```

2. Open **SQL-TYPES-01 — PostgreSQL-Native Types and Searchable Documents** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-types-01/sql_types_01_native_types_search.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\professional\lessons\sql_types_01_native_types_search.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/professional/lessons/sql_types_01_native_types_search.sql
```

The terminal is then the output surface. If PowerShell says `psql` is not
recognized, restart with `START_DS60.cmd`; it can discover PostgreSQL for that
process. If the database or a relation is missing, return to the notebook
preparation cell and explicitly prepare the disposable database. For
authentication failures, rerun setup/doctor—never put a password in SQL, a
notebook, or Git. With `ON_ERROR_STOP`, fix the **first** error and rerun the
whole file instead of trusting partial output.

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence at the
table's declared grain. A query creates a temporary **result set**: rows printed
on screen are not automatically stored. This lesson introduces or reinforces
Domain, Enum, UUID, Array, Range/multirange, JSONB. Its worked SQL reads or creates `pro_types_lab.documents`, `pg_catalog.pg_indexes`, `pg_catalog.pg_available_extensions`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: The model uses a domain for a reusable email-shape rule and an enum for a small database-owned lifecycle. Enums are compact and clear, but adding/removing labels is migration work; a reference table is more flexible when labels carry metadata or change frequently.
The expected contract is that the result must preserve the row grain described in the walkthrough and expose every named key or measure. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/professional/lessons/sql_types_01_native_types_search.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

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

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
2. **Range subtraction:** apply the half-open rule and prove both range
   boundaries.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
3. **Typed JSONPath:** guard shape/type before numeric comparison.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
4. **Full-text query:** parse the web-style phrase, rank, and add a stable
   secondary order.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
5. **Index comparison:** map JSONB, text-search, and trigram operators to their
   useful operator classes.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
6. **Type decision:** defend domain, enum, lookup, array, range, JSONB, or
   normalized-relation choices field by field.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
7. **Multirange:** normalize availability, find August gaps, and define whether
   adjacency merges.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
8. **Networks:** match addresses to their most-specific containing `cidr` and
   identify an operator-compatible index.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
9. **Money:** compare fixed-scale numeric, minor-unit bigint, and floating point
   using explicit precision and rounding tests.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
10. **Promoted JSON:** validate a generated typed value, index it, and test an
    old payload against the evolved contract.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
11. **Language search:** inspect lexemes and design configuration selection for
    non-English rows.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
12. **Normalize tags:** compare normalized keys and joins with array
    containment, duplicates, order, constraints, and writes.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.

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

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-types-01 — PostgreSQL-Native Types and Searchable Documents.

I am a complete beginner. Use these checked-in sources:
- Guide: sql/professional/companion-guides/sql_types_01_native_types_search.md
- Answer-free learner SQL: sql/professional/lessons/sql_types_01_native_types_search.sql

The lesson concepts include Domain, Enum, UUID, Array, Range/multirange, JSONB. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: The model uses a domain for a reusable email-shape rule and an enum for a small database-owned lifecycle. Enums are compact and clear, but adding/removing labels is migration work; a reference table is more flexible when labels carry metadata or change frequently.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-types-01/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
