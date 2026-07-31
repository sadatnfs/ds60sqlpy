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
        (COALESCE(completed_on, opened_on) - opened_on) STORED,
    CONSTRAINT maintenance_completion_order_ck
        CHECK (completed_on IS NULL OR completed_on >= opened_on)
);
```

`service_days` is zero while a visit is open. Another valid design would leave
it NULL until completion by using
`completed_on - opened_on` without `COALESCE`. That is a product-semantic
choice, not merely a syntax choice.

### Reasoning and verification

- **Inputs/evidence:** For sql-found-01 Exercise 1, change only `pro_relational_lab.equipment_items`, and `pro_relational_lab.maintenance_visits` inside the lesson rollback/cleanup boundary. Capture the DDL command tag and the relevant `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, and `information_schema.columns` rows.
- **Expected result/shape:** For sql-found-01 Exercise 1, expected output: the requested DDL command tag plus catalog rows and one accepted and one rejected behavior. The final columns are `external_reference`, `service_days`, `completed_on`, `opened_on`, and `coalesce`.
- **Independent verification:** For sql-found-01 Exercise 1, inspect `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, and `information_schema.columns` for `pro_relational_lab.equipment_items`, and `pro_relational_lab.maintenance_visits`; run one accepted and one rejected operation, record the SQLSTATE, and confirm rollback/cleanup removes the course-owned object. Run one value that satisfies the new rule and one value that must fail; record the catalog definition and SQLSTATE.
- **Intermediate relation check:** For sql-found-01 Exercise 1, inspect `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, and `information_schema.columns` for `pro_relational_lab.equipment_items`, and `pro_relational_lab.maintenance_visits`; run one accepted and one rejected operation, record the SQLSTATE, and confirm rollback/cleanup removes the course-owned object.
- **Clause check:** For sql-found-01 Exercise 1, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pro_relational_lab.equipment_items`, and `pro_relational_lab.maintenance_visits` or label it as proposed policy.
- **Alternative/trade-off:** For sql-found-01 Exercise 1, the chosen form is justified by this lesson-specific rationale: The grain is one maintenance visit for one physical equipment item. Evaluate another form against the concrete expected result (the requested DDL command tag plus catalog rows and one accepted and one rejected behavior) and the verification above.
- **Edge case:** Run one value that satisfies the new rule and one value that must fail; record the catalog definition and SQLSTATE.

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

- **Inputs/evidence:** For sql-found-01 Exercise 2, read the target keys from `pro_relational_lab.maintenance_visits`, and `pro_relational_lab.equipment_items` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
- **Expected result/shape:** For sql-found-01 Exercise 2, expected output: the command tag and an independently counted set of affected `item_id` values. The final columns are `item_id`.
- **Independent verification:** For sql-found-01 Exercise 2, materialize the intended `item_id` target set first; require the command tag/`RETURNING` set to match it, then query `pro_relational_lab.maintenance_visits`, and `pro_relational_lab.equipment_items` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `item_id` values in both cases.
- **Intermediate relation check:** For sql-found-01 Exercise 2, materialize the intended `item_id` target set first; require the command tag/`RETURNING` set to match it, then query `pro_relational_lab.maintenance_visits`, and `pro_relational_lab.equipment_items` again and prove rollback or idempotent retry.
- **Clause check:** For sql-found-01 Exercise 2, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `pro_relational_lab.maintenance_visits`, and `pro_relational_lab.equipment_items`, preserve one row per `item_id`, and finish with `item_id`.
- **Alternative/trade-off:** For sql-found-01 Exercise 2, the chosen form is justified by this lesson-specific rationale: The solution inserts one valid completed visit, then attempts a negative cost inside an exception-catching test block. Evaluate another form against the concrete expected result (the command tag and an independently counted set of affected `item_id` values) and the verification above.
- **Edge case:** Use an empty target set and a multi-row target set; reconcile the affected `item_id` values in both cases.

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

- **Inputs/evidence:** For sql-found-01 Exercise 3, read the target keys from `pro_relational_lab.maintenance_visits`, and `pro_relational_lab.equipment_items` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
- **Expected result/shape:** For sql-found-01 Exercise 3, expected output: at most one row may have no external reference,” PostgreSQL 15+ supports: That is uncommon for external identifiers. The final columns are `item_id`, `opened_on`, `service_note`, and `NULL`. The final order is `mv.visit_id`.
- **Independent verification:** For sql-found-01 Exercise 3, materialize the intended `item_id` target set first; require the command tag/`RETURNING` set to match it, then query `pro_relational_lab.maintenance_visits`, and `pro_relational_lab.equipment_items` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `item_id` values in both cases.
- **Intermediate relation check:** For sql-found-01 Exercise 3, count the input rows from `pro_relational_lab.maintenance_visits`, and `pro_relational_lab.equipment_items`, then run each aggregate `FILTER` predicate as its own count before combining the values into the one-row summary.
- **Clause check:** For sql-found-01 Exercise 3, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, aggregate `FILTER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_relational_lab.maintenance_visits`, and `pro_relational_lab.equipment_items`, preserve exactly one summary row, and finish with `item_id`, `opened_on`, `service_note`, and `NULL` ordered by `mv.visit_id`.
- **Alternative/trade-off:** For sql-found-01 Exercise 3, the chosen form is justified by this lesson-specific rationale: Two rows with `external_reference IS NULL` succeed under an ordinary `UNIQUE` constraint. Evaluate another form against the concrete expected result (at most one row may have no external reference,” PostgreSQL 15+ supports: That is uncommon for external identifiers) and the verification above.
- **Edge case:** Use an empty target set and a multi-row target set; reconcile the affected `item_id` values in both cases.

## Exercise 4 — Deliberate denormalization

`daily_fee_at_checkout` is deliberate denormalization. The normalized current
fee belongs to the equipment item, but a historical loan must preserve the fee
quoted when the checkout occurred. The invariant is:

> Once a checkout is accepted, its quoted fee changes only through an explicit
> correction workflow; later catalog-price changes do not rewrite history.

This snapshot answers historical billing questions reliably. Copying a
category's display name into each equipment row would not provide that benefit
and would create an update anomaly when the category is renamed.

### Reasoning and verification

- **Inputs/evidence:** For sql-found-01 Exercise 4, read from `pro_relational_lab.equipment_categories`, `CASCADE`, and `pro_relational_lab.equipment_items`. Build the answer toward `daily_fee_at_checkout`; keep `item_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-found-01 Exercise 4, expected output: one row per `item_id`. The final columns are `daily_fee_at_checkout`.
- **Independent verification:** For sql-found-01 Exercise 4, reselect the returned keys directly from the source; require unique `item_id` where the expected grain is one row per key and confirm the projected `daily_fee_at_checkout` against `pro_relational_lab.equipment_categories`, `CASCADE`, and `pro_relational_lab.equipment_items`. Add one source row with a new `item_id`; verify the result gains exactly one row carrying that `item_id` value.
- **Intermediate relation check:** For sql-found-01 Exercise 4, select `item_id` from `pro_relational_lab.equipment_categories`, `CASCADE`, and `pro_relational_lab.equipment_items` before adding derived columns.
- **Clause check:** For sql-found-01 Exercise 4, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pro_relational_lab.equipment_categories`, `CASCADE`, and `pro_relational_lab.equipment_items` or label it as proposed policy.
- **Alternative/trade-off:** For sql-found-01 Exercise 4, the chosen form is justified by this lesson-specific rationale: `daily_fee_at_checkout` is deliberate denormalization. Evaluate another form against the concrete expected result (one row per `item_id`) and the verification above.
- **Edge case:** Add one source row with a new `item_id`; verify the result gains exactly one row carrying that `item_id` value.

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
the join at one row per visit/technician assignment.

### Reasoning and verification

- **Inputs/evidence:** For sql-found-01 Exercise 5, read from `pro_relational_lab.maintenance_visits`, `pro_relational_lab.technicians`, `pro_relational_lab.providers`, and `pro_relational_lab.visit_technicians`. Compute `visit_id`, and `technician_id` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-found-01 Exercise 5, expected output: one row per provider, one row per technician, and one row per visit/technician assignment. The final columns are `visit_id`, and `technician_id`.
- **Independent verification:** For sql-found-01 Exercise 5, evaluate each of `technician_id` in a separate control `SELECT` over `pro_relational_lab.maintenance_visits`, `pro_relational_lab.technicians`, `pro_relational_lab.providers`, and `pro_relational_lab.visit_technicians` using `(mv.external_reference = 'VISIT-100')`; require one final row and compare every value. Add one row for which `(mv.external_reference = 'VISIT-100')` is true and one for which it is false; verify only the matching `visit_id` value is returned.
- **Intermediate relation check:** For sql-found-01 Exercise 5, start with the first relation in `pro_relational_lab.maintenance_visits`, `pro_relational_lab.technicians`, `pro_relational_lab.providers`, and `pro_relational_lab.visit_technicians`; after each join, record total rows and distinct `visit_id` so the exact fanout or loss is visible.
- **Clause check:** For sql-found-01 Exercise 5, the solution actually uses `FROM`, `JOIN ... ON`, `WHERE`, and `SELECT`. Read only those operations: begin at `pro_relational_lab.maintenance_visits`, `pro_relational_lab.technicians`, `pro_relational_lab.providers`, and `pro_relational_lab.visit_technicians`, preserve exactly one summary row, and finish with `visit_id`, and `technician_id`.
- **Alternative/trade-off:** For sql-found-01 Exercise 5, the chosen form is justified by this lesson-specific rationale: Use one row per provider, one row per technician, and one row per visit/technician assignment. Evaluate another form against the concrete expected result (one row per provider, one row per technician, and one row per visit/technician assignment) and the verification above.
- **Edge case:** Add one row for which `(mv.external_reference = 'VISIT-100')` is true and one for which it is false; verify only the matching `visit_id` value is returned.

## Exercise 6 — Preserve equipment with no loans

Start from `equipment_items`, LEFT JOIN `loans`, and aggregate by item. Put a
loan-side time filter in the `ON` clause when equipment with no qualifying loan
must remain. The latest date is `max(checked_out_on)` and count should use a
non-NULL loan key, not `count(*)`, which counts the preserved outer row.

If the report also needs columns from the latest loan, rank loans by
`checked_out_on DESC, loan_id DESC` before joining. The identity is the stated
tie-break; a date alone does not impose a total order.

### Reasoning and verification

- **Inputs/evidence:** For sql-found-01 Exercise 6, read from `pro_relational_lab.equipment_items`, and `pro_relational_lab.loans`. Build the answer toward `item_id`; keep `item_id`, and `asset_tag` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-found-01 Exercise 6, expected output: one row per `item_id`, and `asset_tag`. The final columns are `item_id`. The final order is `i.asset_tag`.
- **Independent verification:** For sql-found-01 Exercise 6, independently aggregate `pro_relational_lab.equipment_items`, and `pro_relational_lab.loans` by `item_id`, and `asset_tag`; require one output row for every distinct `item_id`, and `asset_tag` tuple satisfying `(i.asset_tag = 'AUD-001')` and compare `row_count` tuple by tuple. Give two rows the same `i.asset_tag` value and different ``item_id`, and `asset_tag`` values; verify `i.asset_tag` produces the intended rank and display order.
- **Intermediate relation check:** For sql-found-01 Exercise 6, start with the first relation in `pro_relational_lab.equipment_items`, and `pro_relational_lab.loans`; after each join, record total rows and distinct `item_id`, and `asset_tag` so the exact fanout or loss is visible.
- **Clause check:** For sql-found-01 Exercise 6, the solution actually uses `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_relational_lab.equipment_items`, and `pro_relational_lab.loans`, preserve one row per `item_id`, and `asset_tag`, and finish with `item_id` ordered by `i.asset_tag`.
- **Alternative/trade-off:** For sql-found-01 Exercise 6, the chosen form is justified by this lesson-specific rationale: Start from `equipment_items`, LEFT JOIN `loans`, and aggregate by item. Evaluate another form against the concrete expected result (one row per `item_id`, and `asset_tag`) and the verification above.
- **Edge case:** Give two rows the same `i.asset_tag` value and different ``item_id`, and `asset_tag`` values; verify `i.asset_tag` produces the intended rank and display order.

## Exercise 7 — Referential deletion policy

`category -> equipment` and `equipment -> loans` should normally RESTRICT
physical deletion because silently deleting assets or historical checkouts
destroys facts. `equipment -> maintenance_visits` should also RESTRICT under the
same audit requirement. Retire a category/item with status or effective dates.

CASCADE is appropriate for components that have no meaning outside their
parent, not merely because cleanup is easy. `SET NULL` is valid only when the
child remains truthful without its parent and the column is deliberately
nullable. Every choice is a domain rule and requires a deletion test.

### Reasoning and verification

- **Inputs/evidence:** For sql-found-01 Exercise 7, read from `pro_relational_lab.equipment_categories`, `CASCADE`, and `pro_relational_lab.equipment_items`. Build the answer toward `maintenance_visits`; keep `item_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-found-01 Exercise 7, expected output: one row per `item_id`. The final columns are `maintenance_visits`.
- **Independent verification:** For sql-found-01 Exercise 7, reselect the returned keys directly from the source; require unique `item_id` where the expected grain is one row per key and confirm the projected `maintenance_visits` against `pro_relational_lab.equipment_categories`, `CASCADE`, and `pro_relational_lab.equipment_items`. Add one source row with a new `item_id`; verify the result gains exactly one row carrying that `item_id` value.
- **Intermediate relation check:** For sql-found-01 Exercise 7, select `item_id` from `pro_relational_lab.equipment_categories`, `CASCADE`, and `pro_relational_lab.equipment_items` before adding derived columns.
- **Clause check:** For sql-found-01 Exercise 7, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pro_relational_lab.equipment_categories`, `CASCADE`, and `pro_relational_lab.equipment_items` or label it as proposed policy.
- **Alternative/trade-off:** For sql-found-01 Exercise 7, the chosen form is justified by this lesson-specific rationale: `category -> equipment` and `equipment -> loans` should normally RESTRICT physical deletion because silently deleting assets or historical checkouts destroys facts. Evaluate another form against the concrete expected result (one row per `item_id`) and the verification above.
- **Edge case:** Add one source row with a new `item_id`; verify the result gains exactly one row carrying that `item_id` value.

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

- **Inputs/evidence:** For sql-found-01 Exercise 8, read from `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, `pg_catalog.pg_namespace`, `pg_catalog.pg_attribute`, and `pg_catalog.pg_attrdef`. Build the answer toward `contype`, and `constraint_definition`; keep `contype` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-found-01 Exercise 8, expected output: one row per `contype`. The final columns are `contype`, and `constraint_definition`. The final order is `a.attnum`.
- **Independent verification:** For sql-found-01 Exercise 8, project `contype` plus the raw source columns from `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, `pg_catalog.pg_namespace`, `pg_catalog.pg_attribute`, and `pg_catalog.pg_attrdef` at each join stage; record row count and distinct `contype`, then assert the final `contype`, and `constraint_definition` values match those staged rows without unintended fanout or loss. Give two rows the same `a.attnum` value and different ``contype`` values; verify `a.attnum` produces the intended rank and display order.
- **Intermediate relation check:** For sql-found-01 Exercise 8, start with the first relation in `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, `pg_catalog.pg_namespace`, `pg_catalog.pg_attribute`, and `pg_catalog.pg_attrdef`; after each join, record total rows and distinct `contype` so the exact fanout or loss is visible.
- **Clause check:** For sql-found-01 Exercise 8, the solution actually uses `FROM`, `JOIN ... ON`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, `pg_catalog.pg_namespace`, `pg_catalog.pg_attribute`, and `pg_catalog.pg_attrdef`, preserve one row per `contype`, and finish with `contype`, and `constraint_definition` ordered by `a.attnum`.
- **Alternative/trade-off:** For sql-found-01 Exercise 8, the chosen form is justified by this lesson-specific rationale: Join `pg_constraint`, `pg_class`, `pg_namespace`, and `pg_attribute`, and inspect constraint type plus `pg_get_constraintdef`. Evaluate another form against the concrete expected result (one row per `contype`) and the verification above.
- **Edge case:** Give two rows the same `a.attnum` value and different ``contype`` values; verify `a.attnum` produces the intended rank and display order.

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
