# SQL-FOUND-01 Solutions — Relational Design


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\professional\solutions\sql_found_01_relational_design_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/professional/solutions/sql_found_01_relational_design_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Grain, Cardinality, Natural key, Surrogate key, Primary key, Foreign key. Its worked-model focus is:
The example begins with four requirements and turns each into a grain:

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

Run the complete disposable solution with:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/solutions/sql_found_01_relational_design_solutions.sql
```

It creates `pro_relational_lab` inside a transaction and rolls it back.

## Exercise 1 — Translate requirements into DDL

The grain is **one maintenance visit for one physical equipment item**. An item
can have many visits, while each visit names exactly one item, so the foreign
key belongs on `maintenance_visits`.

The executable solution uses an identity primary key for internal row identity
and keeps `external_reference` as a nullable natural identifier:

```sql
CREATE TABLE pro_relational_lab.maintenance_visits (
    visit_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_id bigint NOT NULL
        REFERENCES pro_relational_lab.equipment_items (item_id)
        ON DELETE RESTRICT,
    opened_on date NOT NULL DEFAULT CURRENT_DATE,
    completed_on date,
    provider_name text NOT NULL CHECK (btrim(provider_name) <> ''),
    service_note text NOT NULL CHECK (btrim(service_note) <> ''),
    cost numeric(10, 2) NOT NULL DEFAULT 0 CHECK (cost >= 0),
    external_reference text UNIQUE,
    service_days integer GENERATED ALWAYS AS
        (
            CASE
                WHEN completed_on IS NULL THEN NULL
                ELSE completed_on - opened_on
            END
        ) STORED,
    CONSTRAINT maintenance_completion_order_ck
        CHECK (completed_on IS NULL OR completed_on >= opened_on)
);
```

`service_days` is NULL while a visit is open because no completed duration is
known yet. Once `completed_on` exists, the stored expression reports the
calendar-day difference. Returning zero for an open visit would falsely make
“unfinished” indistinguishable from “completed the same day.”

### Reasoning and verification

- **Inputs/evidence:** For sql-found-01 Exercise 1, create `pro_relational_lab.maintenance_visits` at one-row-per-visit grain inside the rollback-only lab, referencing `equipment_items`; inspect its columns, constraints, defaults, and generated expression through PostgreSQL catalogs.
- **Expected result/shape:** For sql-found-01 Exercise 1, expected output: a successful `CREATE TABLE` command tag followed by catalog evidence for one identity primary key, one item foreign key, nonblank and nonnegative checks, completion-order logic, nullable uniqueness, the `opened_on` default, and stored `service_days` that remains NULL until completion.
- **Independent verification:** For sql-found-01 Exercise 1, assert the catalog definitions rather than generated constraint names, execute one accepted visit and rejected cost/date/foreign-key cases with their SQLSTATE classes, and confirm the final rollback removes `pro_relational_lab`.

## Exercise 2 — Prove an invalid cost is rejected

The solution inserts one valid completed visit, then attempts a negative cost
inside an exception-catching test block. Catching `check_violation` keeps the
outer transaction healthy. The block deliberately raises an unexpected
exception if the insert ever succeeds, so weakening or removing the constraint
causes the test to fail.

An application should still validate cost early for a helpful user experience,
but the database constraint is the final invariant because every writer—not
only that application—must obey it.

### Reasoning and verification

- **Inputs/evidence:** For sql-found-01 Exercise 2, resolve the `AUD-001` item key, insert one valid maintenance visit with `RETURNING visit_id, item_id, cost`, and attempt one negative-cost insert inside a nested exception block.
- **Expected result/shape:** For sql-found-01 Exercise 2, expected output: exactly one returned valid visit with `cost = 28.50`; the invalid attempt emits the expected check-violation notice and contributes no visit row.
- **Independent verification:** For sql-found-01 Exercise 2, compare the returned `item_id` with the independently selected `AUD-001` key, count exactly one `VISIT-100` row, and prove the negative-cost target count remains zero after SQLSTATE `23514` is caught.

## Exercise 3 — NULL uniqueness

Two rows with `external_reference IS NULL` succeed under an ordinary `UNIQUE`
constraint. The database does not infer that the two unknown references are the
same reference.

If the rule were “at most one row may have no external reference,” PostgreSQL
15+ supports:

```sql
UNIQUE NULLS NOT DISTINCT (external_reference)
```

That is uncommon for external identifiers. Usually many visits legitimately
lack a provider reference, while every supplied non-NULL reference must be
unique.

### Reasoning and verification

- **Inputs/evidence:** For sql-found-01 Exercise 3, insert two visits with `external_reference IS NULL`, then inspect all visit rows plus the unique index property that controls NULL comparison.
- **Expected result/shape:** For sql-found-01 Exercise 3, expected output: exactly three visits in the supplied solution state, exactly two with NULL external references, and ordinary uniqueness with `indnullsnotdistinct = false`; PostgreSQL 15+ `UNIQUE NULLS NOT DISTINCT` is the stated alternative policy.
- **Independent verification:** For sql-found-01 Exercise 3, assert the two NULL rows both survive, retry a duplicate non-NULL `VISIT-100` and record SQLSTATE `23505`, and explain that changing to `NULLS NOT DISTINCT` would permit at most one NULL.

## Exercise 4 — Deliberate denormalization

`daily_fee_at_checkout` is deliberate denormalization. The normalized current
fee belongs to the equipment item, but a historical loan must preserve the fee
quoted when the checkout occurred. The invariant is:

> Once a checkout is accepted, its quoted fee changes only through an explicit
> correction workflow; later catalog-price changes do not rewrite history.

This snapshot answers historical billing questions reliably. Copying a
category's display name into each equipment row would not provide that benefit
and would create an update anomaly when the category is renamed.

The executable answer proves the claim rather than merely classifying it: it
creates `loans.daily_fee_at_checkout numeric(10,2)`, copies the current
equipment fee at checkout, changes the current fee from 12.00 to 15.00, and
reselects the loan to show that its quoted 12.00 remains unchanged.

### Reasoning and verification

- **Inputs/evidence:** For sql-found-01 Exercise 4, create a loan-level numeric `daily_fee_at_checkout`, copy the equipment item's current fee at checkout, change the current fee, and return both values plus a decision record.
- **Expected result/shape:** For sql-found-01 Exercise 4, expected output: one loan row showing current fee 15.00 and preserved checkout fee 12.00, followed by one classification row with `attribute_name`, `classification`, `invariant`, and `historical_question`.
- **Independent verification:** For sql-found-01 Exercise 4, change the equipment item's current fee and compare both values; assert the historical `daily_fee_at_checkout` remains unchanged while the catalog fee changes.

## Exercise 5 — Providers, technicians, and assignments

Use one row per provider, one row per technician, and one row per
visit/technician assignment. A provider-to-technician relationship may be
modeled separately if employment changes independently of a visit. The
assignment table needs a composite key such as `(visit_id, technician_id)` (or
an identity plus that unique constraint) so the same technician cannot be
silently assigned twice.

Delimited names fail because the database cannot enforce a technician foreign
key, distinguish a comma inside a name, or update/query one participant without
parsing text. The executable solution creates normalized tables and demonstrates
the join at one row per visit/technician assignment. It backfills a provider
assignment for every existing visit and then drops the old mutable
`maintenance_visits.provider_name`; keeping both writable representations
would recreate the update anomaly normalization is meant to remove.

### Reasoning and verification

- **Inputs/evidence:** For sql-found-01 Exercise 5, model providers and technicians as keyed entities, one provider assignment per visit, and a many-to-many `visit_technicians` bridge; then join the normalized relationships for `VISIT-100`.
- **Expected result/shape:** For sql-found-01 Exercise 5, expected output: a four-row grain map (`providers`, `technicians`, `visit_providers`, `visit_technicians`) followed by two assignment rows with `visit_id`, `provider_name`, `technician_id`, and `technician_name`.
- **Independent verification:** For sql-found-01 Exercise 5, inspect primary and foreign keys, assert one provider assignment and two distinct technician assignments for `VISIT-100`, and prove a duplicate `(visit_id, technician_id)` is rejected.

## Exercise 6 — Preserve equipment with no loans

Start from `equipment_items`, LEFT JOIN `loans`, and aggregate by item. Put a
loan-side time filter in the `ON` clause when equipment with no qualifying loan
must remain. The latest date is `max(checked_out_on)` and count should use a
non-NULL loan key, not `count(*)`, which counts the preserved outer row.

If the report also needs columns from the latest loan, rank loans by
`checked_out_on DESC, loan_id DESC` before joining. The identity is the stated
tie-break; a date alone does not impose a total order.

### Reasoning and verification

- **Inputs/evidence:** For sql-found-01 Exercise 6, start from `pro_relational_lab.equipment_items`, `LEFT JOIN` `loans`, count the nullable-side `loan_id`, and aggregate the latest `checked_out_on` at item grain.
- **Expected result/shape:** For sql-found-01 Exercise 6, expected output: one row per equipment item with columns `item_id`, `asset_tag`, `loan_count`, and `latest_checkout`, ordered by `asset_tag, item_id`; never-loaned items show zero and NULL.
- **Independent verification:** For sql-found-01 Exercise 6, assert output row count equals equipment-item count, `AUD-001` has one loan, and `TOL-001` has zero with NULL latest checkout; move a loan-side date predicate between `ON` and `WHERE` and record the preservation difference.

## Exercise 7 — Referential deletion policy

The executable answer inventories all eight implemented foreign keys. Links
from categories to equipment, members/equipment to loans, equipment to
maintenance, and provider/technician identities to assignments use `RESTRICT`,
because deleting those parents would erase the meaning of historical facts.
Links from a visit to its provider/technician assignment rows use `CASCADE`,
because those bridges have no meaning without the visit.

The expected matrix is joined to `pg_constraint`, translating `confdeltype`
into a readable `actual_action`; every supplied row must report `matches`.
`SET NULL` would be valid only if the child remained truthful without its
parent and the column were deliberately nullable.

### Reasoning and verification

- **Inputs/evidence:** For sql-found-01 Exercise 7, join an expected deletion-policy manifest for all eight implemented foreign keys to `pg_constraint`, translating `confdeltype` into readable referential actions.
- **Expected result/shape:** For sql-found-01 Exercise 7, expected output: eight rows with `relationship`, `expected_action`, `actual_action`, `drift_status`, and `rationale`; category, borrower, equipment, provider, and technician identities use `RESTRICT`, parentless visit-assignment bridges use `CASCADE`, and every row reports `matches`.
- **Independent verification:** For sql-found-01 Exercise 7, require all eight expected relationships exactly once, compare actions with `pg_get_constraintdef`, attempt one protected parent deletion to observe a foreign-key violation, and verify deleting a disposable visit removes only its dependent assignment rows.

## Exercise 8 — Catalog-level contract

Join `pg_constraint`, `pg_class`, `pg_namespace`, and `pg_attribute`, and inspect
constraint type plus `pg_get_constraintdef`. Inspect `pg_attribute.attgenerated`
and `pg_get_expr(pg_attrdef.adbin, ...)` for the generated expression. This
checks semantic properties without coupling a test to a generated name.

For NULL-aware uniqueness, inspect `pg_index.indnullsnotdistinct` on PostgreSQL
15+. The ordinary solution expects it to be false. A robust contract also
checks column order/types and the referenced relation/columns rather than
searching rendered text alone.

### Reasoning and verification

- **Inputs/evidence:** For sql-found-01 Exercise 8, inspect `pg_constraint`, `pg_attribute`/`pg_attrdef`, and `pg_index` for `maintenance_visits` without depending on generated object names.
- **Expected result/shape:** For sql-found-01 Exercise 8, expected output: separate deterministic result sets for named constraint identities/types/definitions ordered by `conname`, column/generated-expression metadata, and external-reference unique-index properties including `indnullsnotdistinct`.
- **Independent verification:** For sql-found-01 Exercise 8, assert one primary key, one item foreign key, the declared CHECK and UNIQUE semantics, `service_days` as a stored generated column with the expected expression, and ordinary NULL-distinct uniqueness; order each result by its own displayed key.

## Edge cases and alternatives

- If overlapping loans must be impossible, a same-day `UNIQUE` constraint is
  insufficient. A later temporal-modeling lesson can use date ranges and an
  exclusion constraint.
- Case-insensitive email uniqueness needs a defined normalization strategy,
  such as a unique index over `lower(email)`; email semantics should not be
  guessed casually.
- `ON DELETE RESTRICT` preserves history. Soft deletion or a status column can
  retire an item without deleting referenced facts.
- A generated value is convenient for row-local immutable arithmetic. Values
  depending on the current clock or another table need a query, snapshot, or
  reviewed update process instead.
